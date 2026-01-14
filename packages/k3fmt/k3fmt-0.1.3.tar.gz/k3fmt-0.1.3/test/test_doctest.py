import doctest

import k3fmt


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3fmt))
    return tests
