import doctest

import k3color


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3color))
    return tests
