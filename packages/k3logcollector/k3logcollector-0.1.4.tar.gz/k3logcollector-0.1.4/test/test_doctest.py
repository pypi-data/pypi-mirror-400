import doctest

import k3logcollector


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3logcollector))
    return tests
