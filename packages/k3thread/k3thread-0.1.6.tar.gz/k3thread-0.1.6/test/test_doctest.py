import doctest

import k3thread


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3thread))
    return tests
