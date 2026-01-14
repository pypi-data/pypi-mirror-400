import doctest
import k3num


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3num))
    return tests
