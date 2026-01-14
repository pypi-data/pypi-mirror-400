import doctest
import k3time


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3time))
    return tests
