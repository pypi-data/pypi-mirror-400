"""Reporting helpers for console, JSON, and JUnit outputs."""

from __future__ import annotations

import json
from typing import Any, List
from xml.sax.saxutils import escape

from rich.console import Console
from rich.table import Table

console = Console()


def render_table(config: dict, results: List[Any]) -> None:
    table = Table(title=f"Regression Suite: {config.get('model')}")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="dim")
    table.add_column("Status")
    table.add_column("Score")
    table.add_column("Reason")
    table.add_column("Latency (s)")
    table.add_column("Tokens (p/c)")
    table.add_column("Cost ($)")

    for result in results:
        status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        latency_display = f"{result.latency:.3f}" if result.latency else "-"
        tokens_display = (
            f"{result.prompt_tokens}/{result.completion_tokens}"
            if (result.prompt_tokens or result.completion_tokens)
            else "-"
        )
        cost_display = f"{result.cost:.6f}" if result.cost else "-"
        table.add_row(
            result.id,
            result.assertion_type,
            status,
            str(result.score),
            result.reason,
            latency_display,
            tokens_display,
            cost_display,
        )
    console.print(table)


def write_json(path: str, config: dict, results: List[Any]) -> None:
    payload = {"config": config, "results": [r.to_dict() for r in results]}
    with open(path, "w") as handle:
        json.dump(payload, handle, indent=2)
    console.print(f"[blue]Wrote JSON report to {path}[/blue]")


def _xml_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    return escape(text, entities={'"': "&quot;"})


def write_junit(path: str, results: List[Any]) -> None:
    failures = sum(1 for r in results if not r.passed)
    total_time = sum(r.latency for r in results)
    testsuite_attrs = f'name="baseline" tests="{len(results)}" failures="{failures}" errors="0" time="{total_time:.3f}"'
    cases = []
    for r in results:
        testcase_name = _xml_escape(r.id)
        reason_text = _xml_escape(r.reason)
        time_attr = f'time="{r.latency:.3f}"'
        testcase = (
            f'<testcase classname="baseline" name="{testcase_name}" {time_attr}><system-out>{reason_text}</system-out>'
        )
        if not r.passed:
            testcase += f'<failure message="score={r.score}">{reason_text}</failure>'
        testcase += "</testcase>"
        cases.append(testcase)
    xml = "".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f"<testsuite {testsuite_attrs}>",
            "".join(cases),
            "</testsuite>",
        ]
    )
    with open(path, "w") as handle:
        handle.write(xml)
    console.print(f"[blue]Wrote JUnit report to {path}[/blue]")


__all__ = ["console", "render_table", "write_json", "write_junit"]
