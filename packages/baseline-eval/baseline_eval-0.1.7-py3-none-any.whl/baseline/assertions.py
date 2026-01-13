"""Assertion helpers and shared evaluation utilities."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

import jsonschema
from jsonschema import ValidationError


@dataclass
class AssertionOutcome:
    passed: bool
    score: int
    reason: str


@dataclass
class AssertionHandler:
    name: str
    evaluate: Callable[
        [Any, Dict[str, Any], Dict[str, Any], Dict[str, Any]],
        Union[AssertionOutcome, Awaitable[AssertionOutcome]],
    ]
    accept_update: Callable[[Any, Dict[str, Any], str], bool]
    expected_value: Callable[[Dict[str, Any], Dict[str, Any]], str]


def check_exact(actual: str, expected: str) -> AssertionOutcome:
    passed = actual.strip() == expected.strip()
    reason = "Exact match" if passed else "Output did not match expected"
    return AssertionOutcome(passed, 10 if passed else 0, reason)


def check_contains(actual: str, expected: str) -> AssertionOutcome:
    passed = expected.lower() in actual.lower()
    reason = f"Found '{expected}'" if passed else f"Missing '{expected}'"
    return AssertionOutcome(passed, 10 if passed else 0, reason)


def check_regex(actual: str, pattern: str) -> AssertionOutcome:
    matched = re.search(pattern, actual) is not None
    reason = "Matched pattern" if matched else "Did not match pattern"
    return AssertionOutcome(matched, 10 if matched else 0, reason)


def check_json(actual: str, schema: Optional[Dict[str, Any]] = None) -> AssertionOutcome:
    try:
        parsed = json.loads(actual)
    except Exception:  # noqa: BLE001
        return AssertionOutcome(False, 0, "Invalid JSON syntax")

    if schema:
        try:
            jsonschema.validate(instance=parsed, schema=schema)
        except ValidationError as exc:
            return AssertionOutcome(False, 0, f"Schema validation failed: {exc.message}")
        except Exception as exc:  # noqa: BLE001
            return AssertionOutcome(False, 0, f"Schema validation failed: {exc}")

    return AssertionOutcome(True, 10, "Valid JSON")


def _coerce_to_dict(value: Any) -> Optional[Dict[str, Any]]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else None
        except Exception:  # noqa: BLE001
            return None
    return None


def _normalize_expected_trajectory(raw: Any) -> List[Dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    normalized = []
    for item in raw:
        if isinstance(item, dict):
            normalized.append({"name": str(item.get("name", "")), "arguments": item.get("arguments")})
        else:
            normalized.append({"name": str(item), "arguments": None})
    return normalized


def _arguments_match(expected_args: Any, actual_args: Any) -> bool:
    if expected_args is None:
        return True

    if isinstance(expected_args, dict):
        actual_dict = _coerce_to_dict(actual_args)
        if not isinstance(actual_dict, dict):
            return False
        for key, value in expected_args.items():
            if str(actual_dict.get(key)) != str(value):
                return False
        return True

    return str(expected_args) in str(actual_args)


def check_trajectory(
    actual: List[Dict[str, Any]],
    expected: List[Dict[str, Any]],
    max_calls: Optional[int] = None,
) -> AssertionOutcome:
    if not expected:
        return AssertionOutcome(False, 0, "No expected_trajectory provided")

    if not actual:
        return AssertionOutcome(False, 0, "No tool calls observed")

    if max_calls is not None and len(actual) > max_calls:
        return AssertionOutcome(False, 0, f"Observed {len(actual)} calls, over limit {max_calls}")

    mismatches: List[str] = []
    for idx, expected_call in enumerate(expected):
        if idx >= len(actual):
            mismatches.append(f"Missing call {expected_call.get('name', '')} at position {idx}")
            break

        actual_call = actual[idx]
        expected_name = expected_call.get("name", "")
        actual_name = actual_call.get("name", "")
        if expected_name != actual_name:
            mismatches.append(f"Expected {expected_name} at {idx}, got {actual_name}")
            continue

        if not _arguments_match(expected_call.get("arguments"), actual_call.get("arguments")):
            mismatches.append(f"Argument mismatch for {expected_name} at {idx}")

    if len(actual) > len(expected):
        mismatches.append(f"Observed {len(actual)} calls, expected {len(expected)}")

    if mismatches:
        return AssertionOutcome(False, 0, "; ".join(mismatches))

    return AssertionOutcome(True, 10, "Trajectory matched")


__all__ = [
    "AssertionOutcome",
    "AssertionHandler",
    "check_exact",
    "check_contains",
    "check_regex",
    "check_json",
    "check_trajectory",
    "_normalize_expected_trajectory",
]
