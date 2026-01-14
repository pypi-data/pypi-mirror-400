import logging
import struct


class V2SerialProtocolCodec:
    '''Encoder/decoder for FLI serial protocol version 2.
    '''

    def __init__(self):
        self.logger = logging.getLogger('V2SerialProtocolCodec')
        self.data = b''
        self.esc_char = False
        self.valid_packet = False
        self.dt_reg_read = 0x3

    def push_char(self, in_char):
        '''Push a received char to the decoder.

        The decoder maintains state between calls and only returns data
        values when the char completes a received packet to decode.

        Args:
            in_char: received char

        Returns:
            timestamp: device sample counter on complete packet, None otherwise
            streams: dict of decoded stream values
            reg_vals: list of register (address, value) tuples
        '''
        timestamp = None
        streams = dict()
        reg_vals = []
        if not self.esc_char and in_char == 0x1B:
            self.esc_char = True
        elif self.esc_char:
            self.esc_char = False
            self.data += bytes([in_char])
        elif in_char == 0x0A:
            self.valid_packet = True
            self.data = b''
        elif self.valid_packet and in_char == 0x0D:
            if len(self.data) < 7:
                self.logger.error(f'not enough bytes in packet: {len(self.data)}')
                self.data = b''
            else:
                timestamp = int.from_bytes(self.data[0:2], byteorder='big')
                streams = dict()
                self.data = self.data[2:]
                while len(self.data):
                    datatype = int.from_bytes(self.data[0:1], byteorder='big')
                    try:
                        dataval = struct.unpack('>i', self.data[1:5])[0]
                        if datatype == self.dt_reg_read:
                            raw_reg = (dataval >> 16) & 0xFFFF
                            raw_val = dataval & 0xFFFF
                            reg_vals.append((raw_reg, raw_val))
                        else:
                            streams[datatype] = dataval
                    except struct.error as e:
                        self.logger.error(f'failed to unpack int: {e}')
                        timestamp = None
                        streams = dict()
                        reg_vals = []
                        self.data = b''
                        self.valid_packet = False
                        break
                    self.data = self.data[5:]
                    self.valid_packet = False
        elif self.valid_packet:
            self.data += bytes([in_char])
        elif self.data != b'':
            self.logger.warning(f'partial data read detected! self.data: {self.data}')

        return timestamp, streams, reg_vals

    def get_max_streams(self, baud, fs, crc=False):
        '''Compute the max number of streams supported for a given baud and samplerate.

        Args:
            baud: serial communications bitrate
            fs: stream samplerate
            crc: bool indicating state of CRC enable

        Returns:
            int: max number of streams supportable
        '''
        bits_per_byte = 10 # 8 data, 1 start, 1 stop
        overhead_bytes = 4 # framing and timestamp
        if crc:
            overhead_bytes += 2 # CRC-16
        bytes_per_stream = 5   # 1 stream ID, 4 stream value

        bytes_per_sample_avail = int(baud / bits_per_byte / fs) - overhead_bytes

        return int(bytes_per_sample_avail/bytes_per_stream)

    def int_to_hex_bytes(self, value, nbytes=2):
        '''Convert integer to ascii encoded hex bytes array.

        Args:
            value: integer value
            nbytes: number of hex bytes to output (0-padded on left)

        Returns:
            bytes: encoded value
        '''
        if type(value) != int:
            raise TypeError(value)
        if value < 0 or value > 2**(nbytes*4)-1:
            raise ValueError(value)
        return f'{value:0{nbytes}X}'.encode('ascii')

    def _one_time_read(self):
        return b'#' + self.int_to_hex_bytes(3) + b'FFFF'

    def one_time_read_cmd(self, address):
        '''Build a command for one-time-read of a register.

        Args:
            address: register address to read

        Returns:
            bytes: encoded command
        '''
        cmd = b'@' + self.int_to_hex_bytes(3)
        cmd += self.int_to_hex_bytes(address, nbytes=4)
        cmd += self._one_time_read()
        return cmd

    def reg_write_cmd(self, address, value):
        '''Build a command to write a register value.

        Args:
            address: register address
            value: register value

        Returns:
            bytes: encoded command
        '''
        cmd = b'@' + self.int_to_hex_bytes(address)
        cmd += self.int_to_hex_bytes(value, nbytes=4)
        return cmd

    def config_stream_cmd(self, sid, enable):
        '''Build a command to configure a stream.

        Args:
            sid: stream id
            enable: True to enable, False to disable

        Returns:
            bytes: encoded command
        '''
        cmd = b'#' + self.int_to_hex_bytes(sid)
        cmd += self.int_to_hex_bytes(1 if enable else 0, nbytes=4)
        return cmd
