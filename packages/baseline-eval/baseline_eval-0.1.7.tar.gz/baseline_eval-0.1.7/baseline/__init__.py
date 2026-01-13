"""Baseline regression harness core package."""

import asyncio
from typing import Any, Dict, List, Optional, Tuple

from .core import (
    SuiteRunner,
    console,
    diff_suites,
    init_project,
    render_table,
    update_config_file,
    update_test_baseline,
    write_json,
    write_junit,
)
from .providers import (
    BaseProvider,
    ChatCompletionsProvider,
    InvocationMetrics,
    ProviderResponse,
    create_provider,
)

try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("baseline-eval")
except PackageNotFoundError:
    __version__ = "0.1.7"


def run_suite(
    config_path: str = "evals.yaml",
    ids_filter: Optional[List[str]] = None,
    max_tests: int = 0,
    accept: bool = False,
    concurrency: int = 5,
    config_overrides: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], List[Any], bool]:
    """Programmatic helper mirroring the CLI run command."""
    runner = SuiteRunner()
    return asyncio.run(
        runner.run_suite(config_path, ids_filter or [], max_tests, accept, concurrency, config_overrides)
    )


__all__ = [
    "SuiteRunner",
    "BaseProvider",
    "ChatCompletionsProvider",
    "InvocationMetrics",
    "ProviderResponse",
    "create_provider",
    "console",
    "diff_suites",
    "init_project",
    "render_table",
    "run_suite",
    "update_config_file",
    "update_test_baseline",
    "write_json",
    "write_junit",
    "__version__",
]
