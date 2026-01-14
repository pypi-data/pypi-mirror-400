import doctest

import k3portlock


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3portlock))
    return tests
