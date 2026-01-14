#!/usr/bin/env python
# coding: utf-8

import os
import time
import unittest
import k3daemonize
import k3proc
import k3ut

dd = k3ut.dd

this_base = os.path.dirname(__file__)


def subproc(script, env=None):
    if env is None:
        env = dict(
            PYTHONPATH=this_base + "/../..",
        )

    return k3proc.shell_script(script, env=env)


def read_file(fn):
    try:
        with open(fn, "r") as f:
            cont = f.read()
            return cont
    except EnvironmentError:
        return None


class TestDaemonize(unittest.TestCase):
    foo_fn = "/tmp/foo"
    bar_fn = "/tmp/bar"
    pidfn = "/tmp/test_daemonize.pid"

    def _clean(self):
        # kill foo.py and kill bar.py
        # bar.py might be waiting for foo.py to release lock-file.
        try:
            subproc("python {b}/foo.py stop".format(b=this_base))
        except Exception as e:
            dd(repr(e))

        time.sleep(0.1)

        try:
            subproc("python {b}/bar.py stop".format(b=this_base))
        except Exception as e:
            dd(repr(e))

        # remove written file

        try:
            os.unlink(self.foo_fn)
        except EnvironmentError:
            pass

        try:
            os.unlink(self.bar_fn)
        except EnvironmentError:
            pass

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def test_start(self):
        subproc("python {b}/foo.py start".format(b=this_base))
        time.sleep(0.2)

        self.assertEqual("foo-before", read_file(self.foo_fn))
        time.sleep(1)
        self.assertEqual("foo-after", read_file(self.foo_fn))

    def test_stop(self):
        subproc("python {b}/foo.py start".format(b=this_base))
        time.sleep(0.2)

        self.assertEqual("foo-before", read_file(self.foo_fn), "foo started")

        subproc("python {b}/foo.py stop".format(b=this_base))
        time.sleep(0.2)

        self.assertEqual("foo-before", read_file(self.foo_fn), "process has been kill thus no content is updated")

    def test_restart(self):
        subproc("python {b}/foo.py start".format(b=this_base))
        time.sleep(0.2)

        self.assertEqual("foo-before", read_file(self.foo_fn))

        os.unlink(self.foo_fn)
        self.assertEqual(None, read_file(self.foo_fn))

        subproc("python {b}/foo.py restart".format(b=this_base))
        time.sleep(0.2)

        self.assertEqual("foo-before", read_file(self.foo_fn), "restarted and rewritten to the file")

    def test_exclusive_pid(self):
        subproc("python {b}/foo.py start".format(b=this_base))
        time.sleep(0.1)
        subproc("python {b}/bar.py start".format(b=this_base))
        time.sleep(0.1)

        self.assertEqual(None, read_file(self.bar_fn), "bar.py not started or run")

    def test_default_pid_file(self):
        d = k3daemonize.Daemon()
        # pid file is based on __main__.__file__ which varies by invocation method
        self.assertTrue(d.pidfile.startswith("/var/run/"))

    def test_close_fds(self):
        env = dict(PYTHONPATH="{path_daemonize}".format(path_daemonize=this_base + "/../.."))

        code, out, err = subproc("python {b}/close_fds.py close".format(b=this_base), env=env)

        dd("close_fds.py close result:")
        dd(code)
        dd("out:")
        for line in out.split("\n"):
            dd("  ", line)
        dd("err:")
        for line in err.split("\n"):
            dd("  ", line)

        time.sleep(1)

        fds = read_file(self.foo_fn)
        dd("fds:", fds)

        self.assertNotIn(self.bar_fn, fds)

        self._clean()

        code, out, err = subproc("python {b}/close_fds.py open".format(b=this_base), env=env)

        dd("close_fds.py open result:")
        dd(code)
        dd("out:")
        for line in out.split("\n"):
            dd("  ", line)
        dd("err:")
        for line in err.split("\n"):
            dd("  ", line)

        time.sleep(1)

        fds = read_file(self.foo_fn)
        dd("fds:", fds)

        self.assertIn(self.bar_fn, fds)
