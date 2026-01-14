import coverage
import json
import os
import importlib
import sys
import pytest
from types import ModuleType
from .test_case_validation import get_test_cases, get_failures

COVERAGE_TEMP_FILE = "python_helper_coverage_analysis_output.json"


class CoverageResults:
    """A summary of a file's coverage results.

    Attributes:
        - filename: the name of the file for which coverage was checked
        - executed_lines: a list of the lines executed in the file
        - missing_lines: a list of the lines missing
        - excluded_lines: a list of the excluded lines
        - covered_lines: the number of lines covered
        - num_statements: the number of statements in the file
        - percent_covered: the percentage of coverage
    """
    filename: str
    executed_lines: list
    missing_lines: list
    excluded_lines: list
    covered_lines: int
    num_statements: int
    percent_covered: float

    def __init__(self, filename: str, json_summary: dict):
        """Initialize this CoverageResults with the data from json_summary.

        json_summary is the dictionary containing the summary for filename.
        """
        self.filename = filename
        self.executed_lines = json_summary['executed_lines']
        self.missing_lines = json_summary['missing_lines']
        self.excluded_lines = json_summary['excluded_lines']
        self.covered_lines = json_summary['summary']['covered_lines']
        self.num_statements = json_summary['summary']['num_statements']
        self.percent_covered = json_summary['summary']['percent_covered']


def get_test_coverage_dict(test_module: ModuleType,
                           modules_to_check: list[str],
                           modules_to_replace: dict[str, str] = None,
                           allow_pytest: bool = True,
                           allow_unittest: bool = True,
                           ) -> dict[str, CoverageResults]:
    """Return a dictionary mapping a module to a CoverageResult object formed
    by running the tests in test_module.

    modules_to_check is a list of modules to check coverage of.

    modules_to_replace is a dictionary mapping the name of a module to replace
    with the name of its replacement.
    """
    if modules_to_replace is None:
        modules_to_replace = {}

    # Run coverage and replace modules as needed
    to_replace = []
    replacements = []
    for module in modules_to_replace:
        to_replace.append(module)
        replacements.append(modules_to_replace[module])

    cov = coverage.Coverage(include=modules_to_check)
    cov.start()

    # Delete any cached version of modules that need to be checked
    for mod in modules_to_check:
        try:
            to_delete = mod[:-3]  # Remove .py from the name
            del sys.modules[to_delete]
        except:
            # In the case of a module that could not be deleted, just skip
            # it. The work-around is to just replace the module with itself.
            pass

    # Reload the module
    importlib.reload(test_module)

    test_cases = get_test_cases(test_module,
                                allow_pytest=allow_pytest,
                                allow_unittest=allow_unittest)
    _ = get_failures(test_cases,
                     module_to_replace=to_replace,
                     module_to_use=replacements
                     )
    cov.stop()
    cov.save()

    # Currently, it seems like the easiest way to get all of the coverage
    # details is through the JSON report. The API doesn't seem to give
    # a way to access the same summary.
    cov.json_report(outfile=COVERAGE_TEMP_FILE)
    with open(COVERAGE_TEMP_FILE) as f:
        coverage_report = json.load(f)

    # Delete the JSON file once read
    if os.path.isfile(COVERAGE_TEMP_FILE):
        os.remove(COVERAGE_TEMP_FILE)

    results = {filename: CoverageResults(filename,
                                         coverage_report['files'][filename])
               for filename in coverage_report['files']
               }

    return results


def make_test_coverage_fixture(test_module: ModuleType,
                               modules_to_check: list[str],
                               modules_to_replace: dict[str, str] = None,
                               allow_pytest: bool = True,
                               allow_unittest: bool = True,
                               ):
    """Return a fixture that returns the dictionary mapping a module to a
    CoverageResult object.

    modules_to_check is a list of modules to check coverage of.

    modules_to_replace is a dictionary mapping the name of a module to replace
    with the name of its replacement.
    """

    @pytest.fixture(scope="module")
    def coverage_fixture():
        cd = get_test_coverage_dict(test_module,
                                    modules_to_check,
                                    modules_to_replace,
                                    allow_pytest,
                                    allow_unittest,
                                    )
        return cd

    return coverage_fixture
