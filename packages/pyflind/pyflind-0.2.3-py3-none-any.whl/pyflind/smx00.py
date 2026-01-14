from collections.abc import Mapping, Sequence
from collections import deque
from enum import Enum
import logging
from time import time, sleep

from .bidirmap import BidirectionalStrIntMap
from .device import FliDevice
from .util import version_uint32_to_str, crc8, int_to_base36


class SM200RegisterMap(BidirectionalStrIntMap):
    '''SM200 register name to id mapper.
    '''
    def __init__(self):
        self._dict = {
            'csr':                          0x00,
            'pcb_id':                       0x02,
            'read_reg':                     0x03,
            'scratch':                      0x04,
            'schedule_freq':                0x17, # 23
            'checksum_and_state_mon':       0x43, # 67
            'uart_rate':                    0x44, # 68
            'logic_module_ctrl':            0x4d, # 77
            'autogain_enable':              0x65, # 101
            'led_ctrl':                     0x6e, # 110
            'sensor_serial_0':              0x7C, # 124
            'sensor_serial_1':              0x7D, # 125
            'sensor_serial_2':              0x7E, # 126
            'sensor_serial_3':              0x7F, # 127
        }


class SM200StreamMap(BidirectionalStrIntMap):
    '''SM200 data stream name to id mapper.
    '''
    def __init__(self):
        self._dict = {
            'fw_version':                   0x06,
            'sensor_serial_lo':             0x07,
            'sensor_serial_hi':             0x08,
            'larmor_freq':                  0x12, # 18
            'mag':                          0x17, # 23
            'logic_module_state':           0x23, # 35
        }


class SM300RegisterMap(BidirectionalStrIntMap):
    '''SM300 register name to id mapper.
    '''
    def __init__(self):
        self._dict = {
            'csr':                          0x00,
            'pcb_id':                       0x02,
            'read_reg':                     0x03,
            'scratch':                      0x04,
            'schedule_freq':                0x17, # 23
            'checksum_and_state_mon':       0x43, # 67
            'uart_rate':                    0x44, # 68
            'logic_module_ctrl':            0x4D, # 77
            'autogain_enable':              0x65, # 101
            'led_ctrl':                     0x6E, # 110
            'sensor_serial_0':              0x7C, # 124
            'sensor_serial_1':              0x7D, # 125
            'sensor_serial_2':              0x7E, # 126
            'sensor_serial_3':              0x7F, # 127
            'fw_version_lo':                0x80, # 128
            'fw_version_hi':                0x81, # 129
            'electronics_serial_0':         0x82, # 130
            'electronics_serial_1':         0x83, # 131
            'electronics_serial_2':         0x84, # 132
            'electronics_serial_3':         0x85, # 133
        }


class SM300StreamMap(BidirectionalStrIntMap):
    '''SM300 data stream name to id mapper.
    '''
    def __init__(self):
        self._dict = {
            'fw_version':                   0x06,
            'sensor_serial_lo':             0x07,
            'sensor_serial_hi':             0x08,
            'electronics_rev':              0x0D, # 13
            'larmor_freq':                  0x12, # 18
            'mag':                          0x17, # 23
            'logic_module_state':           0x23, # 35
            'electronics_2_serial_lo':      0x35, # 53
            'electronics_2_serial_hi':      0x36, # 54
            'electronics_serial_lo':        0x37, # 55
            'electronics_serial_hi':        0x38, # 56
            'pps_clock_count':              0x3D, # 61
            'pps_raw_output':               0x43, # 67
            'pps_raw_input':                0x44, # 68
        }


class SMx00StateMap(BidirectionalStrIntMap):
    '''SMx00 state name to id mapper.

    Can be used to interpret the logic_module_state stream value.
    '''

    def __init__(self):
        self._dict = {
            'off':              0,
            'laser_check':      1,
            'warm_up':          2,
            'optical_scan':     3,
            'heat_stabilize':   4,
            'magnetic_scan':    5,
            'magnetic_lock':    6,
        }


class SMx00LEDColor(Enum):
    '''SMx00 LED colors
    '''
    off = 0
    red = 1
    orange = 2
    yellow = 3
    lime = 4
    cyan = 5
    blue = 6
    purple = 7
    pink = 8
    white = 9


class SMx00Error(Exception):
    '''General purpose exception for SMx00 errors.
    '''
    pass


class SMx00(FliDevice):
    '''FieldLine Industries Scalar Magnetometer device object.

    An FliDevice for all scalar magnetometer products. The generation of
    device is automatically detected and appropriate stream and register
    maps provided upon instantiation.

    Args:
        device_uri: device connection string (see :doc:`/device_comm`)
        max_hist: max number of samples of history to keep per stream
        lm_state_hist: max number of logic module state transitions to track
        multiproc: use process instead of thread for device io/codec
    '''

    #: Rubidium 87 gyromagnetic ratio in Hz/T
    Rb87_GYROMAG_RATIO = 6.99583e9

    #: Conversion factor for larmor_freq stream to Hz
    LARMOR_FREQ_RATIO = 4e6/(2**32-1)

    LM_CMD_START = 0x1F
    LM_CMD_STOP = 0x00

    def __init__(self, device_uri: str,
                 max_hist: int = 1000,
                 lm_state_hist: int = 120,
                 multiproc: bool = False) -> None:
        self._baud_list = [
            115200,
            230400,
            460800,
            921600,
            1036800,
            1152000,
            1267200,
            1382400,
            1497600,
            1612800,
            1728000,
            1843200,
            1958400,
            2000000,
            2500000,
            4000000,
            3686400 ]
        self._lm_cur_state = None
        self._lm_last_n = -1
        self._lm_state_q = deque(maxlen=lm_state_hist)
        self._lm_state_sid = SM200StreamMap()['logic_module_state']
        self._fw_version = None
        self._sensor_serial = None
        self._electronics_serial = None

        super().__init__(device_uri=device_uri, max_hist=max_hist, multiproc=multiproc)

        # start with SM300 registers/streams to detect
        self._reg_map = SM300RegisterMap()
        self._stream_map = SM300StreamMap()

        self._detect_model()

    def _detect_model(self) -> None:
        self._model = None
        if self.get_max_streams() - len(self.get_active_streams()) < 2:
            self.set_samplerate(1000)
        try:
            self.get_electronics_serial()
            self._model = 'SM300'
        except:
            self._model = 'SM200'

        try:
            self.get_sensor_serial()
        except:
            pass

        self._name = self._model
        if self._sensor_serial is not None:
            self._name += f'[{self._sensor_serial}]'
        else:
            self._name += f'[{self._device_uri}]'
        self._logger = logging.getLogger(self._name)

        if self._model == 'SM200':
            self._reg_map = SM200RegisterMap()
            self._stream_map = SM200StreamMap()
        elif self._model == 'SM300':
            self._reg_map = SM300RegisterMap()
            self._stream_map = SM300StreamMap()

        self._state_map = SMx00StateMap()

    def _queue_sample_block(self) -> None:
        '''Override parent sample block handler for sensor state tracking.
        '''
        if self._stream_block is not None and self._stream_block_i > 0 and self._lm_state_sid in self._stream_block_ids:
            lm_state_idx = self._stream_block_ids.index(self._lm_state_sid)
            n_idx = self._stream_block_ids.index('n')

            for i in range(self._stream_block_i):
                if int(self._stream_block[lm_state_idx,i]) != self._lm_cur_state:
                    self._lm_cur_state = int(self._stream_block[lm_state_idx,i])
                    self._lm_last_n = int(self._stream_block[n_idx,i])
                    self._lm_state_q.append((self._lm_cur_state, self._lm_last_n))
        else:
            self._lm_cur_state = None
            self._lm_last_n = -1

        # call parent for default sample handling
        super()._queue_sample_block()

    def get_ident(self) -> Mapping[str, str|int]:
        ident = {}
        ident['model'] = self.get_model()
        ident['fw_version'] = self.get_fw_version()
        try:
            ident['sensor_serial'] = self.get_sensor_serial()
        except:
            ident['sensor_serial'] = ''
        if ident['model'] == 'SM300':
            ident['electronics_serial'] = self.get_electronics_serial()
        return ident

    def get_fw_version_raw_reg(self) -> int:
        '''Get the device firmware version in raw 32-bit format from registers.

        Returns:
            int: 32-bit firmware version
        '''
        version_lo = self.get_register('fw_version_lo')
        version_hi = self.get_register('fw_version_hi')
        return ((version_hi << 16) & 0xffff0000) | version_lo

    def get_fw_version_raw_stream(self) -> int:
        '''Get the device firmware version in raw 32-bit format from stream.

        Returns:
            int: 32-bit firmware version
        '''
        self.configure_stream('fw_version', True)
        data = self.get_samples()
        while 'fw_version' not in data:
            sleep(0.01)
            data = self.get_samples()
        self.configure_stream('fw_version', False)
        return int(data['fw_version'][-1])

    def get_fw_version(self, version_int: None|int = None) -> str:
        '''Get or convert a firmware version int to string format.

        Args:
            version_int: convert raw version if supplied, read version if None (default)

        Returns:
            str: human readable firmware version
        '''
        if self._fw_version is not None and version_int is None:
            return self._fw_version

        if version_int is None:
            try:
                version_int = self.get_fw_version_raw_reg()
                if version_int == 0xffffffff or (version_int >> 26) & 0x1f < 2:
                    raise ValueError(version_int)
            except:
                version_int = self.get_fw_version_raw_stream()

        # TODO handle old v2 firmware format
        self._fw_version = version_uint32_to_str(version_int)
        return self._fw_version

    def get_serial_raw_reg(self, prefix: str) -> int:
        '''Get a raw integer serial number from registers.

        Args:
            prefix: register prefix to read

        Returns:
            int: sensor serial
        '''
        sn_raw = 0
        for i in range(4):
            sn_raw |= self.get_register(f'{prefix}_serial_{i}') << (16 * i)
        sn_bytes = sn_raw.to_bytes(8, 'little')
        if sn_raw == 0:
            raise SMx00Error(f'invalid serial number: 0x{sn_raw:x}')
        if crc8(sn_bytes) != 0:
            raise SMx00Error(f'serial number crc check failed: 0x{sn_raw:x}')
        return sn_raw

    def get_serial_raw_stream(self, prefix: str) -> int:
        '''Get a raw integer serial number from streams.

        Args:
            prefix: stream prefix to read

        Returns:
            int: sensor serial
        '''
        sn_raw = 0
        if len(self.get_active_streams()) + 1 < self.get_max_streams():
            self.reset_schedule()
        self.configure_stream(f'{prefix}_serial_lo', True)
        data = self.get_samples()
        while f'{prefix}_serial_lo' not in data:
            sleep(0.01)
            data = self.get_samples()
        self.configure_stream(f'{prefix}_serial_lo', False)
        sn_lo = int(data[f'{prefix}_serial_lo'][-1])
        self.configure_stream(f'{prefix}_serial_hi', True)
        data = self.get_samples()
        while f'{prefix}_serial_hi' not in data:
            sleep(0.01)
            data = self.get_samples()
        self.configure_stream(f'{prefix}_serial_hi', False)
        sn_hi = int(data[f'{prefix}_serial_hi'][-1])
        sn_raw = (sn_hi & 0xffffffff) << 32
        sn_raw |= sn_lo & 0xffffffff
        sn_bytes = sn_raw.to_bytes(8, 'little')
        if sn_raw == 0:
            raise SMx00Error(f'invalid serial number: 0x{sn_raw:x}')
        if crc8(sn_bytes) != 0:
            raise SMx00Error(f'serial number crc check failed: 0x{sn_raw:x}')
        return sn_raw

    def get_sensor_serial(self, serial_raw: None|int = None) -> str:
        '''Get or convert the sensor serial number to string format.

        Args:
            serial_raw: convert raw serial if supplied, read if None (default)

        Returns:
            str: base-36 encoded sensor serial number
        '''
        if self._sensor_serial is not None:
            return self._sensor_serial

        if serial_raw is None:
            try:
                serial_raw = self.get_serial_raw_reg('sensor')
            except:
                serial_raw = self.get_serial_raw_stream('sensor')

        self._sensor_serial = int_to_base36((serial_raw >> 8) & 0xffffffff)
        return self._sensor_serial

    def get_electronics_serial(self, serial_raw: None|int = None) -> int:
        '''Get or convert the electronics serial number to string format.

        Args:
            serial_raw: convert raw serial if supplied, read if None (default)

        Returns:
            str: base-36 encoded electronics serial number
        '''
        if self._electronics_serial is not None:
            return self._electronics_serial

        if self._model == 'SM200':
            raise SMx00Error('SM200 has no electronics serial number')

        if serial_raw is None:
            try:
                serial_raw = self.get_serial_raw_reg('electronics')
            except:
                serial_raw = self.get_serial_raw_stream('electronics')

        self._electronics_serial = serial_raw
        return self._electronics_serial

    def get_baudrate(self) -> int:
        baud = super().get_baudrate()
        if baud is None:
            baud_idx = self.get_register('uart_rate')
            baud = self._baud_list[baud_idx]
        return baud

    def set_baudrate(self, baud: int) -> None:
        '''Set the device serial baudrate.

        This function only changes the device baudrate via the uart_rate register
        to the requested value using the existing serial interface. It will be
        required to close the connection to the device and establish a new one at
        this requested baud before communication can continue. It is recommended
        to reset the streaming schedule prior to a baudrate change to avoid
        decoding errors around the transition.

        Args:
            baud: uart baudrate
        '''
        if baud not in self._baud_list:
            raise SMx00Error(f'baudrate {baud} unsupported')
        baud_idx = self._baud_list.index(baud)
        self.set_register('uart_rate', baud_idx)
        self.write_queue_drain()

    def get_logic_module_state(self) -> None|str:
        '''Get the current logic module state.

        Returns:
            None|str: None if logic_module_state stream is disabled, current logic_module_state if stream is enabled
        '''
        if self._lm_cur_state is not None:
            return self._state_map[self._lm_cur_state]
        return None

    def get_logic_module_state_history(self) -> Sequence[tuple[str,int]]:
        '''Get the logic module state history.

        Any time the logic_module_state stream is enabled it is monitored for
        state changes and the sample index of state changes is logged in a
        queue. This function empties and returns the queue when called.

        Returns:
            list((state, n))
        '''
        state_hist = []
        for _ in range(len(self._lm_state_q)):
            item = self._lm_state_q.popleft()
            state_hist.append((self._state_map[item[0]], item[1]))
        return state_hist

    def start_sensor(self, timeout: float = 0) -> tuple[bool,Mapping[str,float]]:
        '''Start the sensor.

        By default the function returns immediately after requesting the sensor
        start. If a nonzero timeout is provided the logic_module_state stream
        will be monitored and the function will only return when the magnetic_lock
        state is entered or the timeout elapses. When waiting for startup the time
        spent in each startup state is also tracked and returned.

        Args:
            timeout: seconds to wait for sensor to lock, 0 for non-blocking

        Returns:
            bool, dict:
                True if timeout == 0 or if sensor entered magnetic_lock False otherwise
                dict of times spent in each state during startup
        '''
        success = False
        lm_state_dict = dict()
        stream_started = False

        if timeout > 0 and 'logic_module_state' not in self.get_active_streams():
            self.configure_stream('logic_module_state', True)
            stream_started = True
            sleep(0.1)

        if self.get_logic_module_state() == 'magnetic_lock':
            if stream_started:
                self.configure_stream('logic_module_state', False)
            self._logger.info('sensor already started')
            return True, lm_state_dict

        self._logger.info('starting sensor')
        self._lm_state_q.clear()
        self.set_register(self._reg_map['logic_module_ctrl'], self.LM_CMD_START)
        if timeout <= 0:
            return True, lm_state_dict

        t_start = time()
        while time()-t_start < timeout and self.get_logic_module_state() != 'magnetic_lock':
            sleep(0.1)

        fs = self.get_samplerate()
        state_hist = self.get_logic_module_state_history()
        for i in range(len(state_hist)-1):
            state, n = state_hist[i]
            next_n = state_hist[i+1][1]
            if state not in lm_state_dict:
                lm_state_dict[state] = 0
            lm_state_dict[state] += (next_n - n)/fs
        last_state = state_hist[-1]

        success = False
        while time()-t_start < timeout:
            sleep(2)
            state_hist = self.get_logic_module_state_history()
            if len(state_hist) == 0 and last_state[0] == 'magnetic_lock':
                success = True
                break

            if len(state_hist) > 0:
                state, n = last_state
                if state not in lm_state_dict:
                    lm_state_dict[state] = 0
                lm_state_dict[state] += (state_hist[0][1] - n)/fs

                for i in range(len(state_hist)-1):
                    state, n = state_hist[i]
                    next_n = state_hist[i+1][1]
                    if state not in lm_state_dict:
                        lm_state_dict[state] = 0
                    lm_state_dict[state] += (next_n - n)/fs

                last_state = state_hist[-1]

        if success:
            self._logger.info('sensor started')
        else:
            self._logger.error('sensor failed to reach magnetic_lock state')

        if stream_started:
            self.configure_stream('logic_module_state', False)

        return success, lm_state_dict

    def stop_sensor(self) -> None:
        '''Stop the sensor.
        '''
        self.set_register(self._reg_map['logic_module_ctrl'], self.LM_CMD_STOP)
        self._logger.info('sensor stopped')

    def set_led(self,
                color: SMx00LEDColor,
                blink: bool = False,
                brightness: int = 8,
                manual_ctrl: bool = True) -> None:
        '''Set the LED configuration

        By default the device LED color and blinking is set automatically
        to indicate the active state of the sensor. In this automatic mode
        the brightness is still configurable, or complete manual control
        can be enabled.

        Args:
            color: :class:`SMx00LEDColor` to set, ignored if manual_ctrl is False
            blink: True to blink the LED, False for solid. Ignored if manual_ctrl is False
            brightness: 0-255 brightness value
            manual_ctrl: True to ignore state and set the color/blink, False to track state
        '''
        led_ctrl = (brightness & 0xff) << 8
        led_ctrl |= (color.value & 0xf) << 4
        led_ctrl |= 0x2 if blink else 0
        led_ctrl |= 0x1 if manual_ctrl else 0
        self.set_register('led_ctrl', led_ctrl)

