import doctest

import k3fnmatch
import k3fnmatch.fnmatch


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(k3fnmatch))
    tests.addTests(doctest.DocTestSuite(k3fnmatch.fnmatch))
    return tests
