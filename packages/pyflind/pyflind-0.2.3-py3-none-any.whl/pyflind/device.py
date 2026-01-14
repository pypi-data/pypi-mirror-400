from collections.abc import Mapping, Sequence
from collections import deque
from enum import Enum
import logging
import multiprocessing as mp
import numpy as np
from queue import Queue, Empty
from threading import Thread, Lock, Event
from time import time, sleep
from typing import Any, Callable

from .bidirmap import BidirectionalStrIntMap
from .codec import V2SerialProtocolCodec
from .deviceio import get_deviceio_from_uri


class FliBaseRegisterMap(BidirectionalStrIntMap):
    '''Base FLI device register map, to be replaced by device specific map.
    '''

    def __init__(self):
        self._dict = {
            'csr':                  0x00,
            'read_reg':             0x03,
            'schedule_freq':        0x17, # 23
        }


class FliProtocolReq(Enum):
    CLOSE = 0
    SET_REGISTER = 1
    GET_REGISTER = 2
    CONFIGURE_STREAM = 3
    GET_MAX_STREAMS = 4
    GET_STATS = 5
    WRITE_DRAIN = 6


class FliProtocolResp(Enum):
    CLOSED = 0
    OPENED = 1
    REGISTER_VALUE = 2
    STREAM_SAMPLE = 3
    MAX_STREAMS = 4
    STATS = 5
    WRITE_DRAINED = 6


class FliProtocolBase:

    def __init__(self, device_uri):
        self._device_uri = device_uri
        self._logger = logging.getLogger('FliProtocolProc')

        self._rtt = 0
        self._rtt_t0 = 0
        self._last_rx_cnt = 0
        self._last_tx_cnt = 0
        self._last_cnt_t = 0
        self._rx_rate = 0
        self._tx_rate = 0
        self._io_rate_dt = 0.5
        self._io_rate_alpha = 0.269597

    def _send_req(self, req):
        pass

    def _recv_req(self):
        pass

    def _send_rsp(self, rsp):
        pass

    def _remote_io_close(self):
        pass

    def recv(self):
        pass

    def join(self):
        pass

    def close_req(self):
        self._send_req((FliProtocolReq.CLOSE,))

    def set_register_req(self, address, value):
        self._send_req((FliProtocolReq.SET_REGISTER, address, value))

    def get_register_req(self, address):
        self._send_req((FliProtocolReq.GET_REGISTER, address))

    def configure_stream_req(self, sid, enable):
        self._send_req((FliProtocolReq.CONFIGURE_STREAM, sid, enable))

    def get_max_streams_req(self, baud, fs):
        self._send_req((FliProtocolReq.GET_MAX_STREAMS, baud, fs))

    def get_stats_req(self):
        self._send_req((FliProtocolReq.GET_STATS,))

    def write_drain_req(self):
        self._send_req((FliProtocolReq.WRITE_DRAIN,))

    def _process_req(self, req):
        proc_exit = False

        if req[0] == FliProtocolReq.CLOSE:
            proc_exit = True

        elif req[0] == FliProtocolReq.SET_REGISTER:
            address = req[1]
            value = req[2]
            self._devio.write(self._codec.reg_write_cmd(address, value))

        elif req[0] == FliProtocolReq.GET_REGISTER:
            address = req[1]
            buf = self._codec.one_time_read_cmd(address)
            if self._rtt_t0 == 0:
                self._rtt_t0 = time()
            self._devio.write(buf)

        elif req[0] == FliProtocolReq.CONFIGURE_STREAM:
            sid = req[1]
            enable = req[2]
            self._devio.write(self._codec.config_stream_cmd(sid, enable))

        elif req[0] == FliProtocolReq.GET_MAX_STREAMS:
            baud = req[1]
            fs = req[2]
            max_streams = self._codec.get_max_streams(baud, fs)
            self._send_rsp((FliProtocolResp.MAX_STREAMS, max_streams))

        elif req[0] == FliProtocolReq.GET_STATS:
            stats = {
                'rx_count': self._last_rx_cnt,
                'tx_count': self._last_tx_cnt,
                'rx_rate': self._rx_rate,
                'tx_rate': self._tx_rate,
                'rtt': self._rtt
            }
            self._send_rsp((FliProtocolResp.STATS, stats))

        elif req[0] == FliProtocolReq.WRITE_DRAIN:
            self._devio.write_queue_drain()
            self._send_rsp((FliProtocolResp.WRITE_DRAINED,))

        else:
            self._logger.error(f'unhandled request: {req}')

        return proc_exit

    def _compute_io_rates(self):
        t = time()
        dt = t - self._last_cnt_t
        if self._last_cnt_t == 0:
            rx_cnt, tx_cnt = self._devio.get_rxtx_count()
            self._last_cnt_t = t
            self._last_rx_cnt = rx_cnt
            self._last_tx_cnt = tx_cnt
        elif dt >= self._io_rate_dt:
            rx_cnt, tx_cnt = self._devio.get_rxtx_count()
            rx_rate_now = (rx_cnt - self._last_rx_cnt)/dt
            tx_rate_now = (tx_cnt - self._last_tx_cnt)/dt
            self._rx_rate = rx_rate_now*self._io_rate_alpha + self._rx_rate*(1-self._io_rate_alpha)
            self._tx_rate = tx_rate_now*self._io_rate_alpha + self._tx_rate*(1-self._io_rate_alpha)
            self._last_cnt_t = t
            self._last_rx_cnt = rx_cnt
            self._last_tx_cnt = tx_cnt

    def _run_proto(self):
        try:
            self._devio = get_deviceio_from_uri(self._device_uri)
            self._codec = V2SerialProtocolCodec()
            baud = self._devio.get_baudrate()
            self._send_rsp((FliProtocolResp.OPENED, baud))
        except Exception as e:
            self._send_rsp((FliProtocolResp.CLOSED, e))
            self._remote_io_close()
            return

        self._logger.debug('started')
        proc_exit = False
        close_data = None

        while not proc_exit:
            try:
                while True:
                    req = self._recv_req()
                    try:
                        proc_exit = self._process_req(req)
                        if proc_exit:
                            self._devio.write_queue_drain()
                            break
                    except Exception as e:
                        self._logger.exception(e)
            except Empty:
                pass

            try:
                t, data = self._devio.read(timeout=0.001)
                if isinstance(data, Exception):
                    close_data = data
                    proc_exit = True
                    break

                for c in data:
                    dev_ts, streams, reg_vals = self._codec.push_char(c)
                    for reg_val in reg_vals:
                        if self._rtt_t0 != 0:
                            self._rtt = t - self._rtt_t0
                            self._rtt_t0 = 0
                        address = reg_val[0]
                        value = reg_val[1]
                        rtt = self._rtt
                        self._send_rsp((FliProtocolResp.REGISTER_VALUE, address, value, rtt))
                    if dev_ts is not None:
                        streams['rx_t'] = t
                        self._send_rsp((FliProtocolResp.STREAM_SAMPLE, dev_ts, streams))
            except (Empty, KeyboardInterrupt):
                pass
            except Exception as e:
                self._logger.exception(e)
                break

            self._compute_io_rates()

        self._devio.close()
        self._send_rsp((FliProtocolResp.CLOSED, close_data))
        self._remote_io_close()
        self._logger.debug('closed')


class FliProtocolMTQueue(FliProtocolBase):

    def __init__(self, device_uri):
        super().__init__(device_uri)

        self._req_q = Queue()
        self._rsp_q = Queue()
        self._thread = Thread(target=self._run_proto,
                              daemon=True)
        self._thread.start()

    def _send_req(self, req):
        self._req_q.put(req)

    def _recv_req(self):
        return self._req_q.get_nowait()

    def _send_rsp(self, rsp):
        self._rsp_q.put(rsp)

    def recv(self):
        return self._rsp_q.get()

    def join(self):
        if self._thread is not None:
            self._thread.join()
            self._thread = None


class FliProtocolMPQueue(FliProtocolBase):

    def __init__(self, device_uri):
        super().__init__(device_uri)

        self._req_q = mp.Queue()
        self._rsp_q = mp.Queue()
        self._process = mp.Process(target=self._run_proto, args=())
        self._process.daemon = True
        self._process.start()

    def _send_req(self, req):
        self._req_q.put(req)

    def _recv_req(self):
        return self._req_q.get_nowait()

    def _send_rsp(self, rsp):
        self._rsp_q.put(rsp)

    def recv(self):
        return self._rsp_q.get()

    def join(self):
        if self._process is not None:
            self._process.join()
            self._process = None


class FliProtocolMPPipe(FliProtocolBase):

    def __init__(self, device_uri):
        super().__init__(device_uri)

        self._local_pipe, self._remote_pipe = mp.Pipe(duplex=True)
        self._process = mp.Process(target=self._run_proto, args=())
        self._process.daemon = True
        self._process.start()

    def _send_req(self, req):
        self._local_pipe.send(req)

    def _recv_req(self):
        if not self._remote_pipe.poll():
            raise Empty
        return self._remote_pipe.recv()

    def _send_rsp(self, rsp):
        self._remote_pipe.send(rsp)

    def _remote_io_close(self):
        self._remote_pipe.close()

    def recv(self):
        return self._local_pipe.recv()

    def join(self):
        if self._process is not None:
            self._local_pipe.close()
            self._local_pipe = None
            self._process.join()
            self._process = None


class FliDeviceError(Exception):
    pass


CallbackType = None | Callable[[Any], None]
SidCallbackType = None | Callable[[Any, str|int], None]
FsCallbackType = None | Callable[[Any, int], None]
DataBlockType = Mapping[str|int, Sequence[float]]
BlockCallbackType = None | Callable[[Any, DataBlockType], None]
RegCallbackType = None | Callable[[Any, str|int, int], None]


class FliDevice:
    '''Generic FieldLine Industries device object.

    This is a base class with common functionality for managing data streams
    and register access to FieldLine Industries devices. It is not expected
    to be instantiated directly but used via subclasses providing device
    specific functionality.

    Args:
        device_uri: device connection string
        max_hist: max number of samples of history to keep per stream
        multiproc: use process instead of thread for device io/codec
    '''

    def __init__(self, device_uri: str,
                 max_hist: int = 1000,
                 multiproc: bool = False) -> None:
        self._device_uri = device_uri
        self._name = f'FliDevice[{device_uri}]'
        self._model = 'unknown'

        self._reg_map = FliBaseRegisterMap()
        self._stream_map = BidirectionalStrIntMap()

        self._reg_read_lock = Lock()
        self._reg_read_blocking = False
        self._reg_value_q = Queue()
        self._rtt = 0

        self._on_close = None
        self._on_close_arg = None
        self._on_reg_value = None
        self._on_reg_value_arg = None
        self._on_stream_add = None
        self._on_stream_add_arg = None
        self._on_stream_del = None
        self._on_stream_del_arg = None
        self._on_stream_block = None
        self._on_stream_block_arg = None
        self._on_stream_samplerate = None
        self._on_stream_samplerate_arg = None
        self._max_hist = max_hist
        self._fs = None
        self._samplerate_changing = False
        self._sched_base_fs = 25000

        self._stream_lock = Lock()
        self._stream_event = Event()
        self._stream_sync = False
        self._stream_n = -1
        self._stream_last_ts = None
        self._active_sids = []
        self._virtual_sids = ['n', 'rtt', 'rx_t']
        self._stream_block = None
        self._stream_block_i = 0
        self._stream_block_ids = []
        self._stream_block_q = Queue()
        self._stream_block_size = 10
        self._last_stream_block_n = 0
        self._rec_block_ids = []
        self._rec_block_q = deque(maxlen=self._max_hist//self._stream_block_size+1)

        self._drain_event = Event()

        self._max_streams_event = Event()
        self._max_streams = None

        self._stats_event = Event()
        self._stats = None

        self._logger = logging.getLogger(self._name)

        if multiproc:
            self._proto = FliProtocolMPPipe(device_uri)
        else:
            self._proto = FliProtocolMTQueue(device_uri)
        resp = self._proto.recv()
        if resp[0] == FliProtocolResp.OPENED:
            self._io_baud = resp[1]
        elif resp[0] == FliProtocolResp.CLOSED:
            if isinstance(resp[1], Exception):
                raise resp[1]
            else:
                raise FliDeviceError(f'FliProtocolProc error: {resp[1]}')

        self._thread = Thread(target=self._rx_thread,
                              name='RxThread',
                              daemon=True)
        self._thread.start()

    def get_model(self) -> str:
        '''Get the device model string.

        Current supported models:
            * 'SM200'
            * 'SM300'

        See also:
            :func:`get_ident`

        Returns:
            str: model
        '''
        return self._model

    def __str__(self):
        return self._name

    def _ts_delta(self, dev_ts: int) -> int:
        delta = 1
        if self._stream_last_ts is not None:
            delta = dev_ts - self._stream_last_ts
            if delta < 0:
                delta += 0x10000

        self._stream_last_ts = dev_ts
        return delta

    def _alloc_stream_block(self) -> None:
        '''Internal function to allocate a new block for active stream samples.
        '''
        self._stream_block_ids = self._active_sids.copy()
        self._stream_block = np.empty((len(self._stream_block_ids), self._stream_block_size), dtype=np.float64)
        self._stream_block_i = 0

    def _queue_sample_block(self) -> None:
        '''Internal function to dispatch a block of samples to the callback.

        Must be called with the stream lock held.
        '''
        if self._stream_block is not None and self._stream_block_i > 0:
            self._last_stream_block_n = self._stream_block[self._stream_block_ids.index('n'),-1]

            if self._rec_block_ids != self._stream_block_ids:
                self._rec_block_ids = self._stream_block_ids.copy()
                self._rec_block_q = deque(maxlen=self._max_hist//self._stream_block_size+1)
            self._rec_block_q.append(self._stream_block[:,:self._stream_block_i])

            if self._on_stream_block is not None:
                data = {}
                for i,sid in enumerate(self._stream_block_ids):
                    msid = self._map_sid(sid)
                    data[msid] = self._stream_block[i,:self._stream_block_i]
                self._stream_block_q.put(data)

        self._stream_block = None
        self._stream_block_i = 0

    def _process_stream_samples(self, dev_ts: int, streams: Mapping[str|int, Sequence[int|float]]) -> None:
        with self._stream_lock:
            if self._stream_sync and dev_ts == 0:
                self._stream_sync = False
                self._stream_n = -1
                self._last_stream_block_n = 0
                self._stream_block_i = 0
                self._stream_last_ts = 0xffff
                self._logger.info(f'streams synced')
                self._stream_event.set()
                if self._samplerate_changing and self._on_stream_samplerate is not None:
                    self._samplerate_changing = False
                    self._on_stream_samplerate(self._on_stream_samplerate_arg, self._fs)

            if not self._stream_sync:
                ts_delta = self._ts_delta(dev_ts)
                self._stream_n += ts_delta

                for vsid in self._virtual_sids:
                    if vsid == 'n':
                        streams[vsid] = self._stream_n
                    elif vsid == 'rtt':
                        streams[vsid] = self._rtt

                have_sids = set(self._active_sids)
                samp_sids = set(streams.keys())

                del_sids = have_sids - samp_sids
                add_sids = samp_sids - have_sids

                if ts_delta != 1:
                    msg = f'timestamp delta detected: {ts_delta}'
                    if self._fs is not None:
                        msg += f' ({ts_delta/self._fs:.3f} s)'
                    self._logger.error(msg)

                # flush sample queue before adding/removing streams
                if del_sids or add_sids or self._stream_n < self._last_stream_block_n:
                    self._queue_sample_block()

                for sid in del_sids:
                    msid = self._map_sid(sid)
                    self._logger.info(f'stream deleted: {msid}')
                    self._active_sids.remove(sid)
                    if self._on_stream_del is not None:
                        # TODO queue up stream add/remove for in-order dispatching
                        self._on_stream_del(self._on_stream_del_arg, msid)
                    self._stream_event.set()

                for sid in add_sids:
                    msid = self._map_sid(sid)
                    self._logger.info(f'stream added: {msid}')
                    self._active_sids.append(sid)
                    if self._on_stream_add is not None and sid not in ['n', 'rx_t', 'rtt']:
                        self._on_stream_add(self._on_stream_add_arg, msid)
                    self._stream_event.set()

                if del_sids or add_sids or self._stream_block is None:
                    self._alloc_stream_block()

                if len(self._active_sids) > len(self._virtual_sids):
                    for i,sid in enumerate(self._stream_block_ids):
                        self._stream_block[i,self._stream_block_i] = streams[sid]
                    self._stream_block_i += 1

                # send sample block when full
                if self._stream_block_i == self._stream_block_size:
                    self._queue_sample_block()

        # pass samples to callback without lock held
        if self._on_stream_block is not None:
            try:
                while True:
                    data = self._stream_block_q.get(timeout=0)
                    self._on_stream_block(self._on_stream_block_arg, data)
            except Empty:
                pass

    def _rx_thread(self) -> None:
        self._logger.debug(f'rx thread started')
        while True:
            try:
                resp = self._proto.recv()
            except EOFError as e:
                self._logger.exception(e)
                break

            if resp[0] == FliProtocolResp.CLOSED:
                if isinstance(resp[1], Exception):
                    self._logger.error(f'FliProtocolProc exception: {resp[1]}')
                break;

            elif resp[0] == FliProtocolResp.STREAM_SAMPLE:
                dev_ts = resp[1]
                streams = resp[2]
                self._process_stream_samples(dev_ts, streams)

            elif resp[0] == FliProtocolResp.REGISTER_VALUE:
                address = resp[1]
                value = resp[2]
                self._rtt = resp[3]

                if self._on_reg_value is not None:
                    self._on_reg_value(self._on_reg_value_arg, address, value)

                if self._reg_read_blocking:
                    self._reg_value_q.put((address, value))

            elif resp[0] == FliProtocolResp.MAX_STREAMS:
                self._max_streams = resp[1]
                self._max_streams_event.set()

            elif resp[0] == FliProtocolResp.STATS:
                self._stats = resp[1]
                self._stats_event.set()

            elif resp[0] == FliProtocolResp.WRITE_DRAINED:
                self._drain_event.set()

            else:
                self._logger.error(f'unhandled response: {resp}')

        if self._on_close:
            self._logger.debug(f'calling on_close')
            self._on_close(self._on_close_arg)

        self._proto.join()
        self._proto = None
        self._logger.debug(f'rx thread done')

    def _map_sid(self, sid: str|int) -> int|str:
        if sid in self._stream_map:
            return self._stream_map[sid]
        else:
            return sid

    def get_ident(self) -> Mapping[str, str|int]:
        '''Get device identifying information.

        See also:
            :func:`get_model`

        Returns:
            dict: device identity key/value pairs
        '''
        return {'name': str(self)}

    def close(self) -> None:
        '''Close the device.

        See also:
            :func:`on_close`
        '''
        if self._proto is not None:
            self._proto.close_req()
            self._thread.join()

    def on_close(self, callback: CallbackType = None, arg: Any = None) -> tuple[CallbackType, Any]:
        '''Set the callback function for device close.

        The callback will be invoked in IO thread context when
        the device IO channel is closed.

        See also:
            :func:`close`

        Args:
            callback: function(arg) or None to de-register

        Returns:
            (callback, arg): previously registered callback or None, None
        '''
        old_cb = self._on_close
        old_arg = self._on_close_arg
        self._on_close = callback
        self._on_close_arg = arg
        return old_cb, old_arg

    def on_stream_add(self, callback: SidCallbackType = None, arg: Any = None) -> tuple[SidCallbackType, Any]:
        '''Set the callback function for stream channel addition.

        The callback will be invoked in IO thread context each time a
        stream channel is added.

        See also:
            :func:`configure_stream`

        Args:
            callback: function(arg, stream_id) or None to de-register

        Returns:
            (callback, arg): previously registered callback or None, None
        '''
        old_cb = self._on_stream_add
        old_arg = self._on_stream_add_arg
        self._on_stream_add = callback
        self._on_stream_add_arg = arg
        return old_cb, old_arg

    def on_stream_del(self, callback: SidCallbackType = None, arg: Any = None) -> tuple[SidCallbackType, Any]:
        '''Set the callback function for stream channel removal.

        The callback will be invoked in IO thread context each time a
        stream channel is removed.

        See also:
            :func:`configure_stream`

        Args:
            callback: function(arg, stream_id) or None to de-register

        Returns:
            (callback, arg): previously registered callback or None, None
        '''
        old_cb = self._on_stream_del
        old_arg = self._on_stream_del_arg
        self._on_stream_del = callback
        self._on_stream_del_arg = arg
        return old_cb, old_arg

    def on_stream_samplerate(self, callback: FsCallbackType = None, arg: Any = None) -> tuple[FsCallbackType, Any]:
        '''Set the callback function for stream samplerate change.

        The callback will be invoked in IO thread context each time the
        stream samplerate is changed.

        See also:
            :func:`set_samplerate`

        Args:
            callback: function(arg, samplerate) or None to de-register

        Returns:
            (callback, arg): previously registered callback or None, None
        '''
        old_cb = self._on_stream_samplerate
        old_arg = self._on_stream_samplerate_arg
        self._on_stream_samplerate = callback
        self._on_stream_samplerate_arg = arg
        return old_cb, old_arg

    def on_stream_block(self,
                        callback: BlockCallbackType = None,
                        arg: Any = None) -> tuple[BlockCallbackType, Any]:
        '''Set the callback function for receiving stream data blocks.

        The callback will be invoked in IO thread context with a block of data
        containing up to the stream block size samples for each stream. The data
        block is a dict a with the following keys:

        * 'rtt': last measured round-trip-time in seconds
        * 'rx_t': system time at which the sample was received
        * 'n': running sample index (reset to 0 on sync)
        * ...: one per active stream

        Note:
            The internal sample history can be used simultaneously with
            this callback interface. See :func:`get_samples`.

        See also:
            * :func:`get_stream_block_size`
            * :func:`set_stream_block_size`

        Args:
            callback: function(arg, data) or None to de-register

        Returns:
            (callback, arg): previously registered callback or None, None
        '''
        old_cb = self._on_stream_block
        old_arg = self._on_stream_block_arg
        self._on_stream_block = callback
        self._on_stream_block_arg = arg
        return old_cb, old_arg

    def on_register_value(self, callback: RegCallbackType = None, arg: Any = None) -> tuple[RegCallbackType, Any]:
        '''Set the callback function for reading register values.

        The callback will be invoked in IO thread context for each
        register value received. After registering a callback via this
        function a read request can be sent with get_register.

        See also:
            :func:`get_register`

        Args:
            callback: function(arg, address, value) or None to de-register

        Returns:
            (callback, arg): previously registered callback or None, None
        '''
        old_cb = self._on_reg_value
        old_arg = self._on_reg_value_arg
        self._on_reg_value = callback
        self._on_reg_value_arg = arg
        return old_cb, old_arg

    def write_queue_drain(self, timeout: float = 1) -> None:
        '''Blocks until the write data queue has been drained.

        This can be used after :func:`set_register` or :func:`configure_stream`
        with non-blocking operation to ensure the request has been sent to the
        device.
        '''
        self._drain_event.clear()
        self._proto.write_drain_req()
        if not self._drain_event.wait(timeout):
            raise FliDeviceError('timed out waiting for write queue to drain')

    def set_register(self, address: str|int, value: int) -> None:
        '''Write a register value.

        See Also:
            * :func:`get_register`
            * :func:`get_register_map` for available registers

        Args:
            address: register name or address
            value: register value
        '''
        if type(address) is str:
            address = self._reg_map[address]
        elif type(address) is not int:
            raise TypeError('address must be str or int')
        if self._proto is None:
            raise FliDeviceError('closed')
        else:
            self._proto.set_register_req(address, value)

    def get_register(self, address: str|int, timeout: float = 5) -> None|int:
        '''Read a register value.

        This function performs a blocking read with timeout when timeout is nonzero.
        If a register value callback has been assigned it will be called in the
        RX thread context when the value is received. If no timeout is requested
        the command is sent and None is immediately returned.

        See also:
            * :func:`on_register_value`
            * :func:`set_register`
            * :func:`get_register_map` for available registers

        Args:
            address: register address
            timeout: blocking timeout in seconds, 0 to perform non-blocking (default 5)

        Returns:
            int value if blocking read successful, None otherwise
        '''
        if type(address) is str:
            address = self._reg_map[address]
        elif type(address) is not int:
            raise TypeError('address must be str or int')
        with self._reg_read_lock:
            read_val = None
            if timeout > 0:
                self._reg_read_blocking = True
            if self._proto is None:
                raise FliDeviceError('closed')
            else:
                self._proto.get_register_req(address)
            if timeout > 0:
                try:
                    while True:
                        read_addr, read_val = self._reg_value_q.get(block=True, timeout=timeout)
                        if address == read_addr:
                            break
                        else:
                            self._logger.debug(f'got unexpected address: {address} != {read_addr} (value={read_val})')
                except Empty:
                    raise TimeoutError()
                finally:
                    self._reg_read_blocking = False

            return read_val

    def inc_register(self, address: str|int, increment: int = 1, timeout: float = 1) -> None:
        '''Increment a register value.

        This function performs a blocking read with timeout to get the
        register value then writes the incremented value back.

        See also:
            * :func:`get_register`
            * :func:`set_register`
            * :func:`get_register_map` for available registers

        Args:
            address: register address
            timeout: blocking timeout in seconds, 0 to perform non-blocking (default 1)

        Returns:
            int value if blocking read successful, None otherwise
        '''
        value = self.get_register(address, timeout)
        self.set_register(address, value+increment)

    def get_stream_map(self) -> Mapping[str|int,int|str]:
        '''Get the device stream name to ID map.

        Returns:
            dict: stream name to ID mappings
        '''
        return self._stream_map

    def get_register_map(self) -> Mapping[str|int,int|str]:
        '''Get the device register name to ID map.

        Returns:
            dict: register name to ID mappings
        '''
        return self._reg_map

    def get_io_stats(self, timeout: float = 1) -> Mapping[str,int|float]:
        '''Get the device IO statistics.

        Args:
            timeout: timeout in seconds (default 1)

        Return:
            dict: RX/TX byte count, RX/TX rate in B/s
        '''
        if self._proto is None:
            raise FliDeviceError('closed')
        else:
            self._stats_event.clear()
            self._proto.get_stats_req()
            if not self._stats_event.wait(timeout):
                raise FliDeviceError('timed out waiting for stats')
        return self._stats

    def get_baudrate(self) -> int:
        '''Get internal device baudrate.

        Returns:
            int: baud rate (bits/s), None if N/A or unknown
        '''
        return self._io_baud

    def get_max_streams(self, baud: None|int = None, fs: None|float = None, timeout: float = 1) -> int:
        '''Compute the max number of streams supported for a given baud and samplerate.

        Args:
            baud: serial communications bitrate, defaults to current
            fs: stream samplerate, defaults to current
            timeout: timeout in seconds (default 1)

        Returns:
            int: max number of streams supportable
        '''
        if baud is None:
            baud = self.get_baudrate()
            if baud is None:
                raise ValueError('unable to determine baud rate, please specify')
        if fs is None:
            fs = self.get_samplerate()
        if self._proto is None:
            raise FliDeviceError('closed')
        else:
            self._max_streams_event.clear()
            self._proto.get_max_streams_req(baud, fs)
            if not self._max_streams_event.wait(timeout):
                raise FliDeviceError('timed out waiting for max streams')
        return self._max_streams

    def get_active_streams(self) -> Sequence[str|int]:
        '''Get list of active streams.

        Returns:
            list: stream ids
        '''
        with self._stream_lock:
            active_sids = [ self._map_sid(s) for s in self._active_sids if s not in self._virtual_sids ]

        return active_sids

    def get_samplerate(self) -> float:
        '''Get the streaming samplerate.

        See also:
            :func:`set_samplerate`

        Returns:
            float: samplerate in Hz
        '''
        if self._fs is None:
            N = self.get_register(self._reg_map['schedule_freq'])
            if N == 0:
                N = 25
            self._fs = self._sched_base_fs / N
        return self._fs

    def set_samplerate(self, fs: float) -> float:
        '''Set the streaming samplerate.

        Not all possible samplerates are supported. The closest achievable
        rate to the request will be used and returned.

        See also:
            * :func:`get_samplerate`
            * :func:`on_stream_samplerate`

        Args:
            fs: requested samplerate in Hz

        Returns:
            float: achieved samplerate in Hz
        '''
        if fs <= 0:
            raise ValueError(fs)

        N = round(self._sched_base_fs / fs)
        fs = self._sched_base_fs / N
        if self._fs != fs:
            if self.get_max_streams(fs=fs) < len(self.get_active_streams()):
                raise FliDeviceError('too many streams to support requested samplerate')
            self._fs = fs
            self._samplerate_changing = True
            self.set_register(self._reg_map['schedule_freq'], N)
            self.stream_sync()

        return self._fs

    def set_max_samplerate(self, n_streams: int = 0) -> float:
        '''Set the maximum samplerate which can achieve the desired number of streams.

        Args:
            n_streams: number of streams required, 0 for current streams

        Returns:
            float: samplerate chosen
        '''
        baud = self.get_baudrate()
        fs = self._sched_base_fs
        if n_streams == 0:
            n_streams = len(self.get_active_streams())
            if n_streams == 0:
                n_streams = 1
        for i in range(1,251):
            fs = self._sched_base_fs/i
            if self.get_max_streams(baud, fs) >= n_streams:
                break

        return self.set_samplerate(fs)

    def get_max_history(self) -> int:
        '''Get the max length of sample history.

        See also:
            * :func:`set_max_history`
            * :func:`get_stream_block_size`
            * :func:`set_stream_block_size`
            * :func:`get_samples`

        Returns:
            int: max number of samples in history buffers
        '''
        return self._max_hist

    def set_max_history(self, max_hist: int, preserve: bool = True) -> None:
        '''Set the max length of sample history.

        Allocate new sample history queues and optionally preserve
        the existing sample history.

        See also:
            * :func:`get_max_history`
            * :func:`get_stream_block_size`
            * :func:`set_stream_block_size`
            * :func:`get_samples`

        Args:
            max_hist: new max number of samples in history, None for infinite
            preserve: True to preserve the current history, False to drop
        '''
        self._max_hist = max_hist
        with self._stream_lock:
            new_q = deque(maxlen=self._max_hist//self._stream_block_size+1)
            if preserve:
                for _ in range(len(self._rec_block_q)):
                    new_q.append(self._rec_block_q.popleft())
            self._rec_block_q = new_q

    def get_stream_block_size(self) -> int:
        '''Get the size of stream blocks.

        Stream samples are internally buffered in blocks of this size. Each stream
        block is passed to the :func:`on_stream_block` callback and are queued in
        the stream history. When the history is fetched via :func:`get_samples`
        all blocks in the history are concatenated and returned.

        See also:
            * :func:`set_stream_block_size`
            * :func:`on_stream_block`
            * :func:`get_samples`
            * :func:`get_max_history`
            * :func:`set_max_history`

        Returns:
            int: max number of samples in history buffers
        '''
        return self._stream_block_size

    def set_stream_block_size(self, block_size: int = 10) -> None:
        '''Set the size of stream blocks.

        Set the size of stream sample blocks. If the size is different than the current
        block size all buffered samples are dropped and new buffers/queues allocated for
        the new size.

        See also:
            * :func:`get_stream_block_size`
            * :func:`on_stream_block`
            * :func:`get_samples`
            * :func:`get_max_history`
            * :func:`set_max_history`

        Args:
            block_size: max number of samples to hold in a block
        '''
        if type(block_size) is not int:
            raise TypeError('block_size must be an integer')
        if self._stream_block_size != block_size:
            with self._stream_lock:
                self._queue_sample_block()
                self._stream_block_size = block_size
                self._alloc_stream_block()
                self._rec_block_q = deque(maxlen=self._max_hist//self._stream_block_size+1)

    def configure_stream(self, sid: str|int, enable: bool, timeout: float = 10) -> None:
        '''Configure a data stream.

        Enable or disable a device stream. By default the call is blocking and waits
        for the stream change to take effect before returning and throws an exception
        upon timeout. If non-blocking operation is desired provide a timeout of 0, in
        which case the stream change will not be in effect when the call returns but
        will take effect at some future point in time.

        See also:
            * :func:`on_stream_add`
            * :func:`on_stream_del`
            * :func:`get_stream_map` for available streams

        Args:
            sid: stream name or id
            enable: True to enable, False to disable
            timeout: seconds to wait for stream, 0 for no wait
        '''
        active_streams = self.get_active_streams()
        if enable and (sid in active_streams or self._map_sid(sid) in active_streams):
            return
        if not enable and (sid not in active_streams and self._map_sid(sid) not in active_streams):
            return

        n_streams = len(active_streams)
        if enable and n_streams + 1 > self.get_max_streams():
            raise FliDeviceError('not enough bandwidth to enable stream')

        if type(sid) is str:
            sid = self._map_sid(sid)
        elif type(sid) is not int:
            raise TypeError('sid must be str or int')

        if self._proto is None:
            raise FliDeviceError('closed')
        else:
            self._proto.configure_stream_req(sid, enable)

        if not enable:
            # provoke a response to detect stream removal
            self.get_register(self._reg_map['schedule_freq'], 0)

        if timeout > 0:
            while True:
                with self._stream_lock:
                    if enable and sid in self._active_sids:
                        return
                    if not enable and sid not in self._active_sids:
                        return
                    self._stream_event.clear()

                if not self._stream_event.wait(timeout):
                    raise FliDeviceError('timed out waiting for stream to change')

    def stream_sync(self, reset_pps: bool = False, timeout: float = 10) -> None:
        '''Reset the streaming sample counter.

        Device streams don't have a timestamp but a sample counter which
        increments each sample regardless of the current samplerate (available
        via the 'n' stream). This function synchronizes various internal
        operations within the device and resets the sample counter to 0.

        A stream_sync typically must be performed at least once after device
        power on, but may be issued any time after that to start counting
        samples from 0 again.

        Devices with a PPS will delay the sync to the next rising PPS edge
        such that sample index 0 begins at the rising edge. The internal
        PPS clock counter can optionally be reset at the same time.

        Args:
            reset_pps: True to reset the PPS clock counter on sync
            timeout: seconds to wait for sync, 0 for no wait
        '''
        with self._stream_lock:
            value = 1
            if reset_pps and self.get_model() != 'SM200':
                value |= 0x200
            self.set_register('csr', value)
            self._stream_sync = True
            self._rec_block_q.clear()

        if timeout > 0 and len(self.get_active_streams()) > 0:
            while True:
                with self._stream_lock:
                    if not self._stream_sync:
                        return
                    self._stream_event.clear()

                if not self._stream_event.wait(timeout):
                    raise FliDeviceError('timed out waiting for stream sync')

    def reset_schedule(self) -> None:
        '''Reset the streaming schedule.

        This function disables all active streams simultaneously with
        a single operation.

        See also:
            * :func:`configure_stream`
            * :func:`stream_sync`
        '''
        self.set_register('csr', 2)
        # provoke a response to detect stream removal
        self.get_register(self._reg_map['schedule_freq'], 0)
        while len(self.get_active_streams()) > 0:
            sleep(0.01)

    def get_samples(self) -> DataBlockType:
        '''Read all buffered stream samples.

        Stream samples are automatically buffered to an internal history
        with a configurable maximum length. This function returns the
        complete history available at the time of call as a dict of numpy
        arrays of samples. Subsequent calls will return samples immediately
        following those returned by the current call, i.e. no samples are
        dropped so the results from multiple consecutive calls can be
        concatenated.

        See also:
            * :func:`on_stream_block`
            * :func:`get_max_history`
            * :func:`set_max_history`
            * :func:`get_stream_block_size`
            * :func:`set_stream_block_size`

        Returns:
            dict: key=stream id, value=np.array of samples
        '''
        data = {}
        with self._stream_lock:
            allblock_sids = self._rec_block_ids.copy()
            if len(self._rec_block_q) == 0:
                return data
            allblocks = np.concatenate(tuple(self._rec_block_q), axis=1)
            self._rec_block_q.clear()

        for i,sid in enumerate(allblock_sids):
            data[self._map_sid(sid)] = allblocks[i]

        return data

    def measure_stream_avg(self, sid: str|int, time: float = 1.0) -> float:
        '''Measure a stream's average value.

        Enable the stream if needed, record it for the specified time and
        compute it's average value. If the stream was enabled it is also
        disabled before returning.

        Note:
            This function consumes samples from the internal history so
            subsequent calls to :func:`get_samples` will begin with samples
            acquired after those used to compute the average.

        Args:
            sid: stream name or id
            time: length of time to record

        Returns:
            float: average value of stream
        '''
        sid_added = False
        active_streams = self.get_active_streams()
        if sid not in active_streams and self._map_sid(sid) not in active_streams:
            self.configure_stream(sid, True)
            sid_added = True
        _ = self.get_samples()
        sleep(time)
        data = self.get_samples()
        if sid_added:
            self.configure_stream(sid, False)
        if sid not in data:
            sid = self._stream_map[sid]
        return float(np.mean(data[sid]))

