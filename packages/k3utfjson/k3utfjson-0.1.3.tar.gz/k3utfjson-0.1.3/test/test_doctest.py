import doctest

import k3utfjson


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3utfjson))
    return tests
