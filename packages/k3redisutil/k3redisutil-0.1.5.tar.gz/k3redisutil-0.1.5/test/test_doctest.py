import doctest

import k3redisutil


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3redisutil))
    return tests
