import doctest

import k3shell


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3shell))
    return tests
