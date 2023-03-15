import os
import daemon
import daemon.pidfile
import argparse

import script

DAEMONPIDFILE = 'daemon.pid'

def start() -> None:
    path = os.getcwd()
    context = daemon.DaemonContext(
        working_directory = path,
        pidfile = daemon.pidfile.TimeoutPIDLockFile(f'{path}/{DAEMONPIDFILE}')
    )

    with context:
        script.main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                        choices = ['start', 'stop'],
                        help = '"start" or "stop" the measurement script')
    args = parser.parse_args()

    if args.action == 'start':
        start()
    elif args.action == 'stop':
        os.system(f'cat {DAEMONPIDFILE} | xargs kill')