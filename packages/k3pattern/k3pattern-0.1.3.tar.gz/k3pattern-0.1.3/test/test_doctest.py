import doctest

import k3pattern


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3pattern))
    return tests
