from collections import deque
from enum import Enum
import logging
import numpy as np
from threading import Lock
from time import perf_counter, sleep

from .device import FliDevice


class FliDeviceGroupError(Exception):
    '''General purpose exception for FliDeviceGroup errors.
    '''
    pass


class SyncState(Enum):
    '''State of stream synchronization for devices in a group.
    '''
    UNSYNCED = 0
    SYNCING = 1
    SYNCED = 2


class FliDeviceGroup:
    '''Group of FliDevice objects to be treated as a single unit.

    A device group is primarily used to synchronize data streams from multiple
    FliDevice objects which are physically sharing a PPS signal. These devices
    may have PPS inputs and PPS outputs daisy-chained together, or they may be
    independently driven by PPS signals which themselves are synchronized, e.g.
    from GPS modules. The problem of clock drift between devices is not solved
    live, but the streams are synchronized to a common point in time after which
    blocks of samples can be read from all devices easily. The data streams can
    be resampled separately using the pps_clock_count stream as a reference
    against which device specific clock drifts can be computed and corrected for.

    When using a device group to manage multiple FliDevice objects the streaming
    configuration should only be altered via the device group rather than
    configuring streams directly on the individual devices in the group.
    '''

    def __init__(self):
        self._lock = Lock()
        self._devices = {}
        self._fs = None
        self._sync_state = SyncState.UNSYNCED
        self._logger = logging.getLogger('FliDeviceGroup')

    def _on_close(self, dev_id):
        self.del_device(dev_id)

    def _on_stream_add(self, dev_id, sid):
        self._set_sync_state(SyncState.UNSYNCED)

    def _on_stream_del(self, dev_id, sid):
        self._set_sync_state(SyncState.UNSYNCED)

    def _on_stream_samplerate(self, dev_id, fs):
        if fs != self._fs:
            self._set_sync_state(SyncState.UNSYNCED)

    def _on_stream_block(self, dev_id, data):
        dev_data = self._devices[dev_id]
        if self._sync_state == SyncState.SYNCING:
            if data['n'][0] == 0:
                dev_data['block_q'].clear()
                dev_data['synced'] = True
                with self._lock:
                    all_synced = True
                    for d in self._devices.values():
                        if not d['synced']:
                            all_synced = False
                            break
                    if all_synced:
                        self._sync_state = SyncState.SYNCED

        if dev_data['synced']:
            dev_data['block_q'].append(data)

    def __len__(self):
        return len(self._devices)

    def _set_sync_state(self, state):
        if state != self._sync_state:
            with self._lock:
                if self._sync_state == SyncState.SYNCED:
                    for d in self._devices.values():
                        d['synced'] = False
                self._logger.info(f'sync state change: {self._sync_state} -> {state}')
                self._sync_state = state

    def add_device(self, dev, stream_block_size=10):
        '''Add a device to the group.

        Args:
            dev: FliDevice object
            stream_block_size: streaming data block size

        Returns:
            str: device ID in group
        '''
        if not isinstance(dev, FliDevice):
            raise FliDeviceGroupError(f'{dev} not an FliDevice')

        try:
            dev_id = dev.get_sensor_serial()
        except:
            dev_id = str(dev)
        with self._lock:
            self._sync_state = SyncState.UNSYNCED
            self._devices[dev_id] = {
                'dev': dev,
                'synced': False,
                'block_q': deque()
            }
            if self._fs is None:
                self._fs = dev.get_samplerate()
            dev.on_close(self._on_close, dev_id)
            dev.on_stream_add(self._on_stream_add, dev_id)
            dev.on_stream_del(self._on_stream_del, dev_id)
            dev.on_stream_samplerate(self._on_stream_samplerate, dev_id)
            dev.on_stream_block(self._on_stream_block, dev_id)
            dev.set_stream_block_size(stream_block_size)

        self._logger.info(f'device added: {dev_id}')
        return dev_id

    def del_device(self, dev_id):
        ''' Delete a device from the group.

        Args:
            dev_id: device ID to delete
        '''
        if dev_id in self._devices:
            with self._lock:
                dev = self._devices[dev_id]['dev']
                dev.on_close()
                dev.on_stream_add()
                dev.on_stream_del()
                dev.on_stream_samplerate()
                dev.on_stream_block()
                del self._devices[dev_id]
                if len(self._devices) == 0:
                    self._fs = None
                    self._sync_state = SyncState.UNSYNCED
            self._logger.info(f'device deleted: {dev_id}')
        else:
            self._logger.warn(f'device not in group: {dev_id}')

    def get_devices(self):
        '''Get a list of devices in the group.

        Returns:
            list(str): list of device IDs
        '''
        with self._lock:
            dev_list = list(self._devices.keys())
        return dev_list

    def get_sync_state(self):
        '''Get the group synchronization state.

        Returns:
            SyncState: state of group sync
        '''
        return self._sync_state

    def stream_sync(self, timeout=10, additional_devices=[]):
        '''Perform a stream synchronization on all devices in the group.

        Args:
            timeout: time in seconds to wait for sync
            additional_devices: list of additional FliDevice objects to sync
        '''
        t0 = perf_counter()
        self._set_sync_state(SyncState.UNSYNCED)

        with self._lock:
            dev_list = list(self._devices.keys())
            self._logger.info(f'initial sync to {dev_list[0]} PPS...')
            self._devices[dev_list[0]]['dev'].stream_sync()
            self._sync_state = SyncState.SYNCING
            for dev_id in dev_list:
                self._logger.info(f'requesting sync on {dev_id}')
                self._devices[dev_id]['dev'].stream_sync(True, 0)
            for dev in additional_devices:
                self._logger.info(f'requesting sync on {dev}')
                dev.stream_sync(True, 0)

        if timeout == 0:
            return

        while perf_counter()-t0 < timeout:
            if self._sync_state == SyncState.SYNCED:
                self._logger.info(f'all devices synced')
                return
            sleep(0.01)

        self._logger.error(f'timed out waiting for sync')
        raise FliDeviceGroupError('timed out waiting for sync')

    def get_samples(self):
        '''Read all buffered stream samples.

        Stream blocks from all devices are collated by sample index and
        returned in one dict for all devices streams when this function
        is called.

        Returns:
            dict: key=dev_id:stream_id, value=np.array of samples
        '''
        data = {}
        n_key = None
        with self._lock:
            N = min([ len(d['block_q']) for d in self._devices.values() ])
            if N > 0:
                for dev_id,d in self._devices.items():
                    b0 = d['block_q'][0]
                    sids = list(b0.keys())
                    for sid in sids:
                        key = f'{dev_id}:{sid}'
                        if n_key is None and sid == 'n':
                            n_key = key
                        data[key] = []
                    for _ in range(N):
                        block = d['block_q'].popleft()
                        for sid,v in block.items():
                            data[f'{dev_id}:{sid}'].extend(v)

        if n_key is not None:
            n = np.array(data[n_key])
            for k in list(data.keys()):
                data[k] = np.array(data[k])
                if k.endswith(':n'):
                    if not np.all(data[k] == n):
                        raise FliDeviceGroupError(f'stream n mismatch: {k}')
                    del data[k]
            data['n'] = n

        return data

    def get_samplerate(self):
        '''Get the streaming samplerate.

        Returns:
            float: samplerate in Hz
        '''
        return self._fs

    def set_samplerate(self, fs):
        '''Set the streaming samplerate of all devices.

        Args:
            fs: requested samplerate in Hz
        '''
        self._fs = fs
        for v in self._devices.values():
            v['dev'].set_samplerate(fs)

    def configure_stream(self, sid, enable, timeout=10):
        '''Configure a data stream on all devices.

        Args:
            sid: stream name or id
            enable: True to enable, False to disable
            timeout: seconds to wait for stream, 0 for no wait
        '''
        for v in self._devices.values():
            v['dev'].configure_stream(sid, enable, timeout)

    def reset_schedule(self):
        '''Reset the streaming schedule on all devices.
        '''
        for v in self._devices.values():
            v['dev'].reset_schedule()

    def set_register(self, address, value):
        '''Write a register value on all devices.

        Args:
            address: register name or address
            value: register value
        '''
        for v in self._devices.values():
            v['dev'].set_register(address, value)
