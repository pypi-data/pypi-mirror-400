import doctest

import k3awssign


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3awssign))
    return tests
