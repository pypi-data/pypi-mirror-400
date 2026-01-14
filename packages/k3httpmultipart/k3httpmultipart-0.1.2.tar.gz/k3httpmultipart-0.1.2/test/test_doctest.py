import doctest

import k3httpmultipart


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3httpmultipart))
    return tests
