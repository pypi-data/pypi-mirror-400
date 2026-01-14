import doctest

import k3rangeset


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3rangeset))
    return tests
