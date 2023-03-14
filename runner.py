import os
import daemon
import argparse

import script

def start():
    path = os.getcwd()
    context = daemon.DaemonContext(
        working_directory = path
    )

    with context:
        script.main()

def stop():
    os.system('pkill -x "python3 runner.py start"')
    os.system('pkill -x "python runner.py start"')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                        choices = ['start', 'stop'],
                        help = '"start" or "stop" the measurement script')
    args = parser.parse_args()

    if args.action == 'start':
        start()
    elif args.action == 'stop':
        stop()