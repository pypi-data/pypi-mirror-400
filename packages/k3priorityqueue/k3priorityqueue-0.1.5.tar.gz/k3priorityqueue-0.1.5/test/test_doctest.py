import doctest

import k3priorityqueue


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3priorityqueue))
    return tests
