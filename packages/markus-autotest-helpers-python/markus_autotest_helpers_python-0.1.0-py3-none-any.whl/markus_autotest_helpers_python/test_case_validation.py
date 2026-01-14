"""
Helper functions for running student test cases.
"""
from typing import Callable, Union, Any
from types import ModuleType
from unittest.mock import patch
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from os.path import sep
from doctest import DocTest, DocTestFinder
import unittest, sys, importlib
import pytest

TEST_PREFIX = "test"
TEST_CLASS_PREFIX = "Test"
PYTEST_NAME_SEPARATOR = "::"
PYTEST_ERROR_SEP = \
    "=========================== short test summary info ==========================="


class _CaseWrapper:
    """A wrapper for test cases.
    """
    name: str
    _testcase: Any
    _test_module: str

    def __init__(self, name: str, testcase: Any, test_module: str) -> None:
        """Initialize this _CaseWrapper with the given <name> and callable
        <testcase>.
        """
        self.name = name
        self._testcase = testcase
        self._test_module = test_module

    def _run(self) -> str:
        """Run this _CaseWrapper's test case and return a string.
        If the test passed, an empty string is returned. Otherwise, the error
        or failure message is returned.
        """
        if isinstance(self._testcase, unittest.TestCase):
            result_container = unittest.TestResult()
            self._testcase.run(result_container)

            # Return the failure/errors messages (if any)
            if result_container.failures:
                return result_container.failures[0][-1]
            if result_container.errors:
                return result_container.errors[0][-1]
        elif isinstance(self._testcase, str):
            # If it's a str then it's a pytest name
            test_output = StringIO()

            with redirect_stdout(test_output), \
                    redirect_stderr(test_output):
                exit_code = pytest.main([self._testcase])

            if exit_code > 0:
                pytest_output = test_output.getvalue()
                test_identifier = remove_module_from_name(self._testcase) \
                    .replace(PYTEST_NAME_SEPARATOR, ".")

                # Extract only the error message and return it
                identifier_loc = pytest_output.find(test_identifier)
                start_index = pytest_output.find('\n', identifier_loc) + 1
                end_index = pytest_output.find(PYTEST_ERROR_SEP)

                error_message = pytest_output[start_index:end_index]
                if error_message:
                    return error_message
                else:
                    # If the error message wasn't correctly obtained, just return
                    # all of the pytest output instead.
                    return pytest_output

        # The test case passed and we can return
        return ''

    def run(self, function_to_mock: str = '', function_to_use: Callable = None,
            module_to_replace: str | list = '', module_to_use: str | list = '') -> str:
        """Run this _CaseWrapper's test case and return a string.

        If function_to_mock is provided, calls to that function are replaced
        with function_to_use.

        If module_to_replace is provided, then module_to_use is used instead.

        If the test passed, an empty string is returned. Otherwise, the error
        or failure message is returned.

        Preconditions:
        - function_to_use is None iff function_to_mock is ''
          module_to_use and test_module are None iff module_to_replace is ''
        - if isinstance(module_to_replace, list) then
          len(module_to_replace) == len(module_to_use)
        """
        if module_to_replace:
            if isinstance(module_to_replace, str):
                module_to_replace = [module_to_replace]
                module_to_use = [module_to_use]

            for i in range(len(module_to_replace)):
                replaced = module_to_replace[i]
                replacement = module_to_use[i]
                # Replace the module as needed
                del sys.modules[replaced]
                sys.modules[replaced] = __import__(replacement)
                # Re-import the file containing the module, so it uses the
                # replacement
                module_imported = importlib.import_module(self._test_module)
                importlib.reload(module_imported)

        # Run the test as needed
        if not function_to_mock:
            result = self._run()
        else:
            with patch(function_to_mock, wraps=function_to_use):
                result = self._run()

        if module_to_replace:
            for i in range(len(module_to_replace)):
                replaced = module_to_replace[i]

                # Restore the original settings
                del sys.modules[replaced]
                sys.modules[replaced] = __import__(replaced)

                module_imported = importlib.import_module(self._test_module)
                importlib.reload(module_imported)

        return result


def remove_module_from_name(pytest_name: str) -> str:
    """Return pytest_name without the path and module included.

    >>> remove_module_from_name('python_helper/test/example_tests.py::test_passes_internal_buggy')
    'test_passes_internal_buggy'
    """
    separator_index = pytest_name.find(PYTEST_NAME_SEPARATOR)
    return pytest_name[separator_index + len(PYTEST_NAME_SEPARATOR):]


def get_test_cases(test_module: Union[ModuleType, Callable],
                   allow_pytest: bool = False, allow_unittest: bool = False,
                   test_module_name: str = '') -> \
        dict[str, _CaseWrapper]:
    """Return a dictionary mapping the name of test cases in <test_module>
    to a _CaseWrapper which can be used to run the tests.

    If allow_pytest is True, pytest test cases will be included.

    If allow_unittest is True, unittest test methods will be included.
    """
    discovered_tests = {}
    if not test_module_name:
        test_module_name = test_module.__name__

    # Use unittest.TestLoader to add discovered UnitTests
    discovered_unittests = {}
    test_suites = unittest.TestLoader().loadTestsFromModule(test_module)
    for suite in test_suites:
        for test_case in suite:
            test_name = test_case.id()
            if test_name.startswith(test_module_name):
                test_name = test_name[len(test_module_name) + 1:]
            discovered_unittests[test_name] = _CaseWrapper(test_name,
                                                           test_case,
                                                           test_module_name)
    if allow_unittest:
        discovered_tests.update(discovered_unittests)

    if allow_pytest:
        pytest_output = StringIO()
        module_path = test_module_name.replace(".", sep) + '.py'

        with redirect_stdout(pytest_output), \
                redirect_stderr(pytest_output):
            pytest.main(['--collect-only', '-q',
                         module_path
                         ])

        test_cases = set(test_line
                         for test_line in pytest_output.getvalue().split('\n')
                         if PYTEST_NAME_SEPARATOR in test_line)

        for test_name in test_cases:
            short_name = remove_module_from_name(test_name)
            pathed_name = module_path + PYTEST_NAME_SEPARATOR + short_name

            # Skip over any unittests
            unittest_name = short_name.replace(PYTEST_NAME_SEPARATOR, '.')
            if unittest_name not in discovered_unittests:
                discovered_tests[unittest_name] = _CaseWrapper(test_name,
                                                               pathed_name,
                                                               test_module_name)

    return discovered_tests


def get_failures(testcases: dict[str, _CaseWrapper],
                 function_to_mock: str = '', function_to_use: Callable = None,
                 module_to_replace: str | list = '',
                 module_to_use: str | list = '') -> set:
    """
    Return a set of all tests that fail in testcases. If function_to_mock is
    provided, function_to_use is used in its place.

    testcases should be a dictionary returned by get_test_cases.

    Precondition: (function_to_mock == '' and function_to_use is None) or \
                  (function_to_mock != '' and function_to_use is not None)
    """
    failures = set()
    for test_name in testcases:
        result = testcases[test_name].run(function_to_mock=function_to_mock,
                                          function_to_use=function_to_use,
                                          module_to_replace=module_to_replace,
                                          module_to_use=module_to_use)
        if result:
            failures.add(test_name)

    return failures


def _read_tests_as_dict(test_list: list[DocTest]) -> dict[str, str]:
    """
    Return a dictionary mapping unique test examples to expected outputs
    from the DocTest objects in <test_list>.

    >>> read_tests_as_dict([DOC1])
    {'func(1)': 'True', 'func(2)': '2'}
    >>> read_tests_as_dict([DOC2])
    {'func(3)': 'False', 'func(4)': '4'}
    """
    return {ex.source.strip(): ex.want.strip() for test in test_list for ex in
            test.examples}


def get_doctest_dict(function: Callable) -> dict[str, str]:
    """
    Return a dictionray mapping the doctest examples of <function> to
    their expected return value.
    """
    finder = DocTestFinder()
    func_tests = _read_tests_as_dict(finder.find(function))
    return func_tests
