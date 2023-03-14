import os
import daemon
import record_and_send

def main():
    path = os.getcwd()
    context = daemon.DaemonContext(
        working_directory = path
    )

    with context:
        record_and_send.main()

if __name__ == "__main__":
    main()