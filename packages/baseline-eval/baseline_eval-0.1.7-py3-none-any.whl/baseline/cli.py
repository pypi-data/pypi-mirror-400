"""Command-line interface for baseline."""

from __future__ import annotations

import argparse
import asyncio
from typing import List

from baseline.core import (
    SuiteRunner,
    console,
    diff_suites,
    init_project,
    render_table,
    update_config_file,
    write_json,
    write_junit,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="baseline - minimal LLM regression harness")
    parser.add_argument("command", nargs="?", default="run", choices=["run", "init", "diff"], help="run|init|diff")
    parser.add_argument("--config", default="evals.yaml")
    parser.add_argument("--provider", help="Override provider for this run")
    parser.add_argument("--model", help="Override model for this run")
    parser.add_argument("--judge-model", help="Override judge_model for this run")
    parser.add_argument("--judge-provider", help="Override judge_provider for this run")
    parser.add_argument("--subject-timeout", type=float, help="Subject call timeout (seconds)")
    parser.add_argument("--judge-timeout", type=float, help="Judge call timeout (seconds)")
    parser.add_argument("--before", help="Config path or JSON results for diff before")
    parser.add_argument("--after", help="Config path or JSON results for diff after")
    parser.add_argument("--filter", help="Comma-separated test ids to run")
    parser.add_argument("--max-tests", type=int, default=0, help="Max number of tests to run")
    parser.add_argument("--concurrency", type=int, default=5, help="Max in-flight LLM calls; 0 for unlimited")
    parser.add_argument("--json-output", help="Path to write JSON results")
    parser.add_argument("--junit-output", help="Path to write JUnit XML")
    parser.add_argument(
        "--accept",
        action="store_true",
        help="Automatically update evals.yaml with new outputs for failed tests",
    )
    return parser.parse_args()


def run_suite(
    config_path: str = "evals.yaml",
    ids_filter: List[str] | None = None,
    max_tests: int = 0,
    accept: bool = False,
    concurrency: int = 5,
):
    """Programmatic entrypoint mirroring the CLI run command."""
    runner = SuiteRunner()
    return asyncio.run(runner.run_suite(config_path, ids_filter or [], max_tests, accept, concurrency))


def main() -> None:
    args = parse_args()

    ids_filter: List[str] = args.filter.split(",") if args.filter else []
    max_tests = args.max_tests

    if args.command == "init":
        init_project(args.config)
        return

    if args.command == "diff":
        if not args.before or not args.after:
            console.print("[red]Provide --before and --after inputs for diff[/red]")
            return
        diff_suites(args.before, args.after, ids_filter, max_tests)
        return

    runner = SuiteRunner()
    overrides = {
        key: value
        for key, value in {
            "provider": args.provider,
            "model": args.model,
            "judge_model": args.judge_model,
            "judge_provider": args.judge_provider,
            "subject_timeout": args.subject_timeout,
            "judge_timeout": args.judge_timeout,
        }.items()
        if value is not None
    }
    config, results, config_updated = asyncio.run(
        runner.run_suite(args.config, ids_filter, max_tests, args.accept, args.concurrency, overrides or None)
    )
    render_table(config, results)

    if args.accept and config_updated:
        update_config_file(args.config, config)

    if args.json_output:
        write_json(args.json_output, config, results)
    if args.junit_output:
        write_junit(args.junit_output, results)


if __name__ == "__main__":
    main()
