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

def stop():
    os.system('pkill -x "python3 runner.py start"')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                        choices = ['start', 'stop'],
                        help = '"start" or "stop" the measurement script')
    args = parser.parse_args()

    if args.action == 'start':
        main()
    elif args.action == 'stop':
        stop()