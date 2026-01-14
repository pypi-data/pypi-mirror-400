import doctest

import k3math


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3math))
    return tests
