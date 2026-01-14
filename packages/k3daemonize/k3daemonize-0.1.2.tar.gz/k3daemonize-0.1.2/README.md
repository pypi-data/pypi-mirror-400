# k3daemonize

[![Action-CI](https://github.com/pykit3/k3daemonize/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3daemonize/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3daemonize/badge/?version=stable)](https://k3daemonize.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3daemonize)](https://pypi.org/project/k3daemonize)

It supplies a command line interface API to start/stop/restart a daemon.

k3daemonize is a component of [pykit3] project: a python3 toolkit set.


Help to create daemon process.
It supplies a command line interface API to start/stop/restart a daemon.

`daemonize` identifies a daemon by the `pid` file.
Thus two processes those are set up with the same `pid` file
can not run at the same time.




# Install

```
pip install k3daemonize
```

# Synopsis

```python

import time
import k3daemonize


def run():
    for i in range(100):
        print(i)
        time.sleep(1)


# python foo.py start
# python foo.py stop
# python foo.py restart

if __name__ == '__main__':
    # there is at most only one of several processes with the same pid path
    # that can run.
    k3daemonize.daemonize_cli(run, '/var/run/pid')

```

#   Author

Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>

#   Copyright and License

The MIT License (MIT)

Copyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>


[pykit3]: https://github.com/pykit3