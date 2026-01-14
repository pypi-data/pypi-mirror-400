import doctest

import k3txutil


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3txutil))
    return tests
