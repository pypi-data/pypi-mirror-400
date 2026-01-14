import doctest

import k3net


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3net))
    return tests
