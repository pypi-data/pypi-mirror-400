"""Thin facade re-exporting runner, assertions, and artifact helpers.

Keeps backward compatibility for callers importing SuiteRunner and helpers
from baseline.core without maintaining duplicate implementations.
"""

from baseline.artifacts import console, render_table, write_json, write_junit
from baseline.assertions import (
    AssertionHandler,
    AssertionOutcome,
    _normalize_expected_trajectory,
    check_contains,
    check_exact,
    check_json,
    check_regex,
    check_trajectory,
)
from baseline.runner import (
    SuiteRunner,
    TestResult,
    diff_suites,
    init_project,
    load_suite_results,
    update_config_file,
    update_test_baseline,
    validate_config,
)

__all__ = [
    "SuiteRunner",
    "TestResult",
    "diff_suites",
    "init_project",
    "load_suite_results",
    "update_config_file",
    "update_test_baseline",
    "validate_config",
    "console",
    "render_table",
    "write_json",
    "write_junit",
    "AssertionOutcome",
    "AssertionHandler",
    "check_exact",
    "check_contains",
    "check_json",
    "check_regex",
    "check_trajectory",
    "_normalize_expected_trajectory",
]
