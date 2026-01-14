import doctest

import k3dict


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3dict))
    return tests
