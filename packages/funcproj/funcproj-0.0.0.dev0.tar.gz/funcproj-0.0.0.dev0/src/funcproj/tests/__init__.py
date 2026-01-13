import unittest

__all__ = ["test"]


def test() -> unittest.TextTestRunner:
    "This function runs all the tests."
    loader: unittest.TestLoader
    suite: unittest.TestSuite
    runner: unittest.TextTestRunner
    result: unittest.TextTestResult
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="funcproj.tests")
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    return result
