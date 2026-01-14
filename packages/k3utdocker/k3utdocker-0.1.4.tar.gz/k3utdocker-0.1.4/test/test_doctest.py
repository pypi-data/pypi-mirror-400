import doctest

import k3utdocker


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3utdocker))
    return tests
