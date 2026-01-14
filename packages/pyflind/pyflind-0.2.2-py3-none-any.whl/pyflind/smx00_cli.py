#!/usr/bin/env python3

import argparse
import logging
import signal
import sys
from time import sleep

try:
    from pyflint.smx00 import SMx00
except:
    from pyflind.smx00 import SMx00

from pyflind.recording import CsvRecorder


_NOARG = object()

def parse_args():
    parser = argparse.ArgumentParser(description='FieldLine Industries SMx00 command line interface',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('device', nargs='+', help='Device URI: e.g. uart:/dev/ttyUSB0:921600 or tcp:HOST:PORT')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable DEBUG logging')
    parser.add_argument('-b', '--baud', type=int, choices=[115200, 230400, 460800, 921600, 1843200],
                        help='Change baud rate to this value after connecting to the device')
    parser.add_argument('-i', '--ident', action='store_true', help='Identify the device')
    parser.add_argument('-f', '--fs', type=float, nargs='?', const=_NOARG, default=None,
                        help='get/set the samplerate in Hz')
    parser.add_argument('-r', '--register', help='Get/set a register, supply addr[:value]')
    parser.add_argument('-e', '--enable', nargs='+', default=[], help='Enable stream(s)')
    parser.add_argument('-d', '--disable', nargs='+', default=[], help='Disable stream(s)')
    parser.add_argument('-a', '--active_streams', action='store_true', help='List active streams')
    parser.add_argument('-s', '--stream_sync', action='store_true', help='Perform stream sync')
    parser.add_argument('--reset_schedule', action='store_true', help='Reset the streaming schedule')
    parser.add_argument('--ls_registers', action='store_true', help='List available device registers')
    parser.add_argument('--ls_streams', action='store_true', help='List available device streams')
    parser.add_argument('--start', action='store_true', help='Start the sensor')
    parser.add_argument('--stop', action='store_true', help='Stop the sensor')
    parser.add_argument('--record', help='Record active streams to specified csv file (only supports single device)')

    return parser.parse_args()


pending_sig = None

def sig_handler(signum, frame):
    global pending_sig
    print(f'Signal received: {signum}')
    pending_sig = signum


def main():
    global pending_sig
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    args = parse_args()

    logger = logging.getLogger('smx00-cli')
    logging.basicConfig(
            level=logging.DEBUG if args.verbose else logging.INFO,
            format='[%(asctime)s.%(msecs)03d|%(levelname)s|%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

    devices = []
    for uri in args.device:
        dev = SMx00(uri)
        logger.info(f'Connected to device {dev}')
        devices.append(dev)

    if args.ident:
        for dev in devices:
            logger.info('Identity:')
            for k,v in dev.get_ident().items():
                if type(v) is int:
                    v = hex(v)
                logger.info(f'  {k}: {v}')

    if args.register is not None:
        addr, value = None, None
        if ':' in args.register:
            addr, value = args.register.split(':')
            value = int(value, 0)
        else:
            addr = args.register
        try:
            addr = int(addr, 0)
        except:
            pass
        if value is not None:
            for dev in devices:
                dev.set_register(addr, value)
        for dev in devices:
            value = dev.get_register(addr)
            logger.info(f'{addr} = {hex(value)}')

    if args.ls_registers:
        logger.info(devices[0].get_register_map())

    if args.ls_streams:
        logger.info(devices[0].get_stream_map())

    if len(args.disable) > 0:
        for sid in args.disable:
            try:
                sid = int(sid, 0)
            except:
                pass
            for dev in devices:
                dev.configure_stream(sid, False)

    if len(args.enable) > 0:
        for sid in args.enable:
            try:
                sid = int(sid, 0)
            except:
                pass
            for dev in devices:
                dev.configure_stream(sid, True)

    if args.active_streams:
        for dev in devices:
            logger.info(f'Active streams on {dev.get_sensor_serial()}:')
            for sid in dev.get_active_streams():
                logger.info(f'  {sid}')

    if args.stream_sync:
        for dev in devices:
            dev.stream_sync()

    if args.reset_schedule:
        for dev in devices:
            dev.reset_schedule()

    if args.fs is not None:
        for dev in devices:
            if args.fs != _NOARG:
                fs = dev.set_samplerate(args.fs)
            else:
                fs = dev.get_samplerate()
        logger.info(f'samplerate: {round(fs,3)} Hz')

    if args.baud is not None:
        for dev in devices:
            dev.set_baudrate(args.baud)
            logger.info(f'set baud rate to {args.baud}')
            dev.close()
        return 0

    if args.start:
        for dev in devices:
            dev.start_sensor()

    if args.stop:
        for dev in devices:
            dev.stop_sensor()

    if args.record:
        if len(devices) != 1:
            logger.error('recording currently only supported on a single device')
        else:
            dev = devices[0]
            fs = dev.get_samplerate()
            dev.set_max_history(round(fs * 5))
            rec = CsvRecorder(args.record)
            logger.info(f'recording to {args.record} until interrupted...')
            n_samples = 0
            while pending_sig is None:
                sleep(1)
                data = dev.get_samples()
                if len(data.keys()) == 0:
                    continue
                rec.write_data(data)
                n_samples += len(data['n'])
            rec.close()
            logger.info(f'recorded {n_samples} samples')

    for dev in devices:
        dev.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
