import doctest

import k3daemonize


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3daemonize))
    return tests
