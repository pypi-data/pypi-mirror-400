import time
import k3daemonize


def run():
    for i in range(100):
        print(i)
        time.sleep(1)


# python foo.py start
# python foo.py stop
# python foo.py restart

if __name__ == "__main__":
    # there is at most only one of several processes with the same pid path
    # that can run.
    k3daemonize.daemonize_cli(run, "/var/run/pid")
