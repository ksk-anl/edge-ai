import os
import daemon
import argparse

import record_and_send

def main():
    path = os.getcwd()
    context = daemon.DaemonContext(
        working_directory = path
    )

    with context:
        record_and_send.main()

def run_infinite():
    context = daemon.DaemonContext()

    with context:
        while True:
            pass

def stop():
    os.system('pkill -x "python3 runner"')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                        choices = ['start', 'stop', 'test'],
                        required = True,
                        help = '"start" or "stop" the measurement script')
    args = parser.parse_args()

    if args.action == 'start':
        main()
    elif args.action == 'stop':
        stop()
    elif args.action == 'test':
        run_infinite()