import doctest

import k3jobq


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3jobq))
    return tests
