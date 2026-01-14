import doctest

import k3stopwatch


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3stopwatch))
    return tests
