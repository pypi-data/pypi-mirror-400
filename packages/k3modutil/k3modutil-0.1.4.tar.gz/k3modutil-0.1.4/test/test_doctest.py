import doctest

import k3modutil


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3modutil))
    return tests
