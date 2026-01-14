import logging
from queue import Queue, Empty
import serial
from socket import socket, SHUT_RDWR
from threading import Thread
from time import time, sleep


class DeviceIOBase:
    '''Base class for FLI device Input/Ouput.
    '''

    def __init__(self):
        self._name = 'DeviceIOBase'
        self._running = False
        self._rx_q = Queue()
        self._tx_q = Queue()
        self._rx_count = 0
        self._tx_count = 0

    def get_name(self):
        '''Get the object name.

        Returns:
            str: object name
        '''
        return self._name

    def get_baudrate(self):
        '''Get internal device baudrate.

        Returns:
            int: baud rate (bits/s), None if N/A or unknown
        '''
        return None

    def get_rxtx_count(self):
        '''Get RX/TX byte counter values.

        Returns:
            int, int: RX count, TX count
        '''
        return self._rx_count, self._tx_count

    def write(self, data):
        '''Write data to the port.

        Data is not written directly but queued to be written by the IO
        thread when available. This function does not block.

        Args:
            data: bytes data to write
        '''
        if type(data) != bytes:
            raise ValueError(data)

        if not self._running:
            raise BrokenPipeError(f'IO thread not active')

        self._tx_q.put(data)

    def write_queue_drain(self):
        '''Blocks until the write data queue has been drained by the io thread.
        '''
        while not self._tx_q.empty():
            sleep(0.001)

    def read(self, timeout=1.0):
        '''Read data from the port.

        Data is read from a queue with timeout. If an exception is returned
        then the port is closed and should not be used again.

        Args:
            timeout: seconds to wait, 0 for non-blocking

        Returns:
            (float, object): timestamp, bytes data buffer or exception
        '''
        return self._rx_q.get(timeout=timeout)

    def close(self):
        pass


class SerialIO(DeviceIOBase):
    '''Threaded serial port input/output.
    '''
    def __init__(self, device, baudrate=921600, max_read=4096):
        '''Open a port and start IO thread.

        Args:
            device:   Serial port device (e.g. /dev/ttyUSB0 or COM1)
            baudrate: Serial port baud (default 921600)
            max_read: Max number of bytes to read at a time (default 1024)
        '''
        super().__init__()
        self._device = device
        self._baudrate = baudrate
        self._max_read = max_read

        self._name = f'SerialIO({device})'
        self._running = True
        self._logger = logging.getLogger(self._name)

        self._ser = serial.Serial(device,
                                  baudrate=baudrate,
                                  parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE,
                                  bytesize=serial.EIGHTBITS,
                                  timeout=0)
        self._ser.reset_input_buffer()
        self._logger.debug(f'opened port at {baudrate}')

        self._thread = Thread(target=self._serial_loop,
                              name=self._name,
                              daemon=True)
        self._thread.start()

    def get_baudrate(self):
        return self._baudrate

    def close(self):
        '''Stop the IO thread and close the serial port.
        '''
        self._running = False
        self._thread.join()

    def _serial_loop(self):
        self._logger.debug(f"serial thread started")
        try:
            while self._running:
                # write from the queue
                try:
                    buf = self._tx_q.get(block=False)
                    self._ser.write(buf)
                    self._tx_count += len(buf)
                    write_q_empty = False
                except Empty:
                    write_q_empty = True

                # read data if available
                buf = self._ser.read(self._max_read)
                t = time()
                if len(buf) > 0:
                    self._rx_count += len(buf)
                    self._rx_q.put((t, buf))

                # sleep if no r/w data to avoid hogging CPU
                elif write_q_empty:
                    sleep(0.01)

        except Exception as e:
            self._logger.exception(e)
            self._tx_q.queue.clear()
            self._rx_q.put((time(), e))
        else:
            self._rx_q.put((time(), BrokenPipeError('port closed')))

        self._running = False
        self._ser.close()
        self._logger.debug(f'closed port')


class TcpSerialIO(DeviceIOBase):
    '''Threaded remote serial port via TCP input/output.
    '''
    def __init__(self, host, port=7777, max_read=4096):
        '''Open a TCP connection to a remote serial port and start IO threads.

        Args:
            host:     hostname or IP address of remote TCP-UART redirector
            port:     TCP port or remote TCP-UART redirector
            max_read: Max number of bytes to read at a time (default 1024)
        '''
        super().__init__()
        self._host = host
        self._port = port
        self._max_read = max_read

        self._name = f'TcpSerialIO({host}:{port})'
        self._running = True
        self._logger = logging.getLogger(self._name)

        self._socket = socket()
        self._socket.connect((host, port))
        self._logger.debug(f'connected')

        self._rx_thread = Thread(target=self._net_recv,
                                 name=f'{self._name}RX',
                                 daemon=True)
        self._tx_thread = Thread(target=self._net_send,
                                 name=f'{self._name}TX',
                                 daemon=True)
        self._rx_thread.start()
        self._tx_thread.start()

    def close(self):
        '''Stop the IO thread and close the serial port.
        '''
        self._running = False
        self._rx_thread.join()

    def _net_send(self):
        self._logger.debug(f"TX thread started")
        try:
            while self._running:
                # write from the queue
                try:
                    buf = self._tx_q.get(timeout=0.01)
                    self._socket.sendall(buf)
                    self._tx_count += len(buf)
                except Empty:
                    pass
        except Exception as e:
            self._running = False
            self._logger.exception(e)
            self._tx_q.queue.clear()

        self._socket.shutdown(SHUT_RDWR)
        self._socket.close()
        self._logger.debug(f"TX thread complete")

    def _net_recv(self):
        self._logger.debug(f"RX thread started")
        try:
            while self._running:
                buf = self._socket.recv(self._max_read)
                t = time()
                if len(buf) > 0:
                    self._rx_count += len(buf)
                    self._rx_q.put((t, buf))
                else:
                    self._running = False
        except Exception as e:
            self._running = False
            self._logger.exception(e)
            self._rx_q.put((time(), e))
        else:
            self._rx_q.put((time(), BrokenPipeError('socket closed')))

        self._tx_thread.join()
        self._logger.debug(f"closed socket")


def get_deviceio_from_uri(dev_uri):
    '''Create a deviceio instance of appropriate type.

    Use the string URI to determine the type of deviceio instance and
    the args required to instantate one, then return this instance.

    Args:
        dev_uri: string url describing the IO device to instantiate
            Serial format: 'uart:<DEVICE>[:BAUDRATE]'
            TCP Serial format: 'tcp:<HOST_OR_IP>[:PORT]'

    Returns:
        concrete instance of DeviceIO
    '''
    uri_parts = dev_uri.split(':')
    if len(uri_parts) < 2:
        raise ValueError(f'too few URI parts: {dev_uri}')

    if uri_parts[0] == 'uart':
        kwargs = {'device': uri_parts[1]}
        if len(uri_parts) > 2:
            kwargs['baudrate'] = int(uri_parts[2])
        return SerialIO(**kwargs)

    elif uri_parts[0] == 'tcp':
        kwargs = {'host': uri_parts[1]}
        if len(uri_parts) > 2:
            kwargs['port'] = int(uri_parts[2])
        return TcpSerialIO(**kwargs)

    else:
        raise ValueError(f'unsupported device URI: {dev_uri}')
