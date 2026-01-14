import doctest

import k3http


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3http))
    return tests
