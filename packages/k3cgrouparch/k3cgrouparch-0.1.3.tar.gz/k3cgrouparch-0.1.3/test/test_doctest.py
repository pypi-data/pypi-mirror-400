import doctest

import k3cgrouparch


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3cgrouparch))
    return tests
