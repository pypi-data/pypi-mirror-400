from __future__ import annotations
from .test_case_validation import get_test_cases, get_failures
from typing import Callable
from types import ModuleType
import pytest


class ResultsGrid:
    """
    A collection of test cases and the results of running them when
    mocked with various functions/modules.

    Attributes:
    - _mock_names: The names of the mocked functions/modules, in the order
                   they were originally provided.
    - _results: A dictionary mapping test case names to their results.
    """
    _mock_names: list[str]
    _results: dict[str, ResultsRow]

    def __init__(self, testcases: dict,
                 function_to_mock: str = '',
                 functions_to_use: list[Callable] | None = None,
                 module_to_replace: str = '',
                 modules_to_use: list[str] | None = None
                 ):
        """Initialize this ResultsGrid."""
        results = {test_name: {} for test_name in testcases}
        self._mock_names = []

        if functions_to_use is not None:
            for fn in functions_to_use:
                failures = get_failures(testcases,
                                        function_to_mock=function_to_mock,
                                        function_to_use=fn)

                for test_name in results:
                    results[test_name][fn.__name__] = False if test_name in failures else True
                    self._mock_names.append(fn.__name__)

        if modules_to_use is not None:
            for mod in modules_to_use:
                failures = get_failures(testcases,
                                        module_to_replace=module_to_replace,
                                        module_to_use=mod)

                for test_name in results:
                    results[test_name][mod] = False if test_name in failures else True
                    self._mock_names.append(mod)

        self._results = {test_name: ResultsRow(test_name, results[test_name])
                         for test_name in results}

    def get_mock_names(self) -> set[str]:
        """Return a set of names of the modules/functions that were used
        in generating these results.
        """
        return set(self._mock_names)

    def filter(self, must_pass: set[str] = None,
               must_fail: set[str] = None,
               exclusions: set[str] = None) -> set[str]:
        """Return a set of test names that pass on all tests in
        must_pass, fail on all tests in must_fail, and are not in exclusions.
        """
        exclusions = exclusions if exclusions else set()
        return {test_name for test_name in self._results
                if test_name not in exclusions and
                self._results[test_name].matches(must_pass=must_pass,
                                                 must_fail=must_fail)
                }

    def __getitem__(self, item):
        """Return the results for the test case with name item.
        """
        return self._results[item]

    def __iter__(self):
        """Return an iterator that loops through each of the rows
        in this ResultsGrid.
        """
        rows = [self._results[name] for name in self._results]
        return rows.__iter__()

    def __len__(self):
        """Return the number of test cases that were tested.
        """
        return len(self._results)


class ResultsRow:
    """
    A row of test case results.

    Attributes:
    - test_name: The name of the test case
    - _results: A dictionary mapping the name of the version of the
                mocked module/function that this test case was run
                with, to a boolean representing whether the test case
                passed or failed.
    """
    test_name: str
    _results: dict[str, bool]

    def __init__(self, test_name: str, results: dict[str, bool]):
        """Initialize this row with the given name and results"""
        self.test_name = test_name
        self._results = results

    def matches(self, must_pass: set[str] = None,
                must_fail: set[str] = None) -> bool:
        """Return True iff these results pass all tests in must_pass
        and fails all tests in must_fail.
        """
        must_pass = must_pass if must_pass else set()
        must_fail = must_fail if must_fail else set()
        return all(self._results[name] is True for name in must_pass) and \
               all(self._results[name] is False for name in must_fail)

    def __getitem__(self, item) -> bool:
        """Return whether this result passed or failed when run on item.
        """
        if hasattr(item, '__name__'):
            item = item.__name__
        return self._results[item]

    def __iter__(self):
        """Return an iterator for all the (test name, result) pairs"""
        results = [(name, self._results[name]) for name in self._results]
        return results.__iter__()


def make_test_results_fixture(test_module: ModuleType | Callable,
                              function_to_mock: str = '',
                              functions_to_use: list[Callable] | None = None,
                              module_to_replace: str = '',
                              modules_to_use: list[str] | None = None,
                              allow_pytest: bool = False,
                              allow_unittest: bool = False,
                              test_module_name: str = '',
                              exclusions: set[str] = None):
    """Return a fixture that returns the results of running the tests in
    test_module with the various versions of functions/modules provided.
    """

    @pytest.fixture(scope="module")
    def results():
        test_cases = get_test_cases(test_module, allow_pytest=allow_pytest,
                                    allow_unittest=allow_unittest,
                                    test_module_name=test_module_name
                                    )
        if exclusions:
            for exclusion in exclusions:
                test_cases.pop(exclusion)
        test_results = ResultsGrid(test_cases,
                                   function_to_mock=function_to_mock,
                                   functions_to_use=functions_to_use,
                                   module_to_replace=module_to_replace,
                                   modules_to_use=modules_to_use
                                   )
        return test_results

    return results
