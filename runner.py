import daemon
import record_and_send

def main():
    context = daemon.DaemonContext()

    with context:
        record_and_send.main()

if __name__ == "__main__":
    main()