"""Suite orchestration, validation, and persistence."""

# mypy: disable-error-code=import-untyped

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, cast

import yaml
from rich.table import Table

from baseline.artifacts import console
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
from baseline.providers import (
    BaseProvider,
    ChatCompletionsProvider,
    InvocationMetrics,
    ProviderResponse,
    _normalize_tool_calls,
    create_provider,
)

logger = logging.getLogger("baseline.runner")

try:
    from ruamel.yaml import YAML

    HAS_RUAMEL = True
except ImportError:  # pragma: no cover - optional dependency
    HAS_RUAMEL = False
    YAML = None  # type: ignore


@dataclass
class TestResult:
    id: str
    assertion_type: str
    passed: bool
    score: int
    reason: str
    actual: str
    input: str
    expected: str
    assertion: Dict[str, Any]
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency: float = 0.0
    cost: float = 0.0
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(payload: Dict[str, Any]) -> "TestResult":
        return TestResult(
            id=payload.get("id", ""),
            assertion_type=payload.get("assertion_type", payload.get("type", "llm")),
            passed=payload.get("passed", False),
            score=payload.get("score", 0),
            reason=payload.get("reason", ""),
            actual=payload.get("actual", ""),
            input=payload.get("input", ""),
            expected=payload.get("expected", ""),
            assertion=payload.get("assertion", {}),
            model=payload.get("model", ""),
            prompt_tokens=int(payload.get("prompt_tokens", 0) or 0),
            completion_tokens=int(payload.get("completion_tokens", 0) or 0),
            total_tokens=int(payload.get("total_tokens", 0) or 0),
            latency=float(payload.get("latency", 0.0) or 0.0),
            cost=float(payload.get("cost", 0.0) or 0.0),
            tool_calls=payload.get("tool_calls", []) or [],
        )


def validate_config(config: Dict[str, Any]) -> None:
    if not isinstance(config, dict):
        raise ValueError("Config must be a mapping")
    tests = config.get("tests")
    if not isinstance(tests, list) or not tests:
        raise ValueError("Config must include a non-empty 'tests' list")
    for test in tests:
        if not isinstance(test, dict):
            raise ValueError("Each test entry must be a mapping")
        if not test.get("id"):
            raise ValueError("Each test requires an 'id'")
        assertion = test.get("assertion", {})
        if not isinstance(assertion, dict):
            raise ValueError(f"Test {test.get('id')} has invalid assertion")
        assertion_type = assertion.get("type", "llm")
        if assertion_type not in {"exact", "contains", "regex", "llm", "trajectory", "json"}:
            raise ValueError(f"Test {test.get('id')} has unsupported assertion type '{assertion_type}'")
        if assertion_type == "llm" and not assertion.get("expected_criteria") and not test.get("expected_criteria"):
            raise ValueError(f"Test {test.get('id')} missing expected_criteria for llm assertion")


class SuiteRunner:
    """Encapsulated orchestrator for loading configs and evaluating suites."""

    def __init__(
        self,
        client: Optional[Any] = None,
        provider: Optional[BaseProvider] = None,
        output: Optional[Any] = None,
    ):
        self._client = client
        self._provider = provider
        self._provider_name: Optional[str] = getattr(provider, "name", None)
        self._provider_override = provider is not None
        self._providers: Dict[str, BaseProvider] = {}
        if provider and self._provider_name:
            self._providers[self._provider_name] = provider
        self.console = output or console
        self._handlers = self._build_handlers()
        self._semaphore: Optional[asyncio.Semaphore] = None

    def _get_provider(self, config: Dict[str, Any], role: str = "subject") -> BaseProvider:
        base_provider = str(config.get("provider", "openai") or "openai").lower()
        provider_name = (
            base_provider
            if role == "subject"
            else str(config.get("judge_provider", base_provider) or base_provider).lower()
        )

        if self._provider_override and self._provider is not None:
            if role == "subject" or provider_name == self._provider_name:
                return self._provider

        if provider_name in self._providers:
            return self._providers[provider_name]

        provider: BaseProvider
        if self._client is not None and provider_name == (self._provider_name or base_provider):
            provider = ChatCompletionsProvider(self._client, default_model=config.get("model", ""))
        else:
            provider = create_provider(provider_name)

        self._providers[provider_name] = provider
        if role == "subject":
            self._provider = provider
            self._provider_name = provider_name
        return provider

    def _build_handlers(self) -> Dict[str, AssertionHandler]:
        return {
            "exact": AssertionHandler(
                name="exact",
                evaluate=lambda _self, test, observed, _config: check_exact(
                    observed.get("content", ""), str(test.get("assertion", {}).get("expected", ""))
                ),
                accept_update=self._accept_exact,
                expected_value=self._expected_exact,
            ),
            "contains": AssertionHandler(
                name="contains",
                evaluate=lambda _self, test, observed, _config: check_contains(
                    observed.get("content", ""), str(test.get("assertion", {}).get("expected", ""))
                ),
                accept_update=self._accept_contains,
                expected_value=self._expected_contains,
            ),
            "regex": AssertionHandler(
                name="regex",
                evaluate=self._evaluate_regex,
                accept_update=lambda *_: False,
                expected_value=self._expected_regex,
            ),
            "llm": AssertionHandler(
                name="llm",
                evaluate=self._evaluate_llm,
                accept_update=lambda *_: False,
                expected_value=self._expected_llm,
            ),
            "json": AssertionHandler(
                name="json",
                evaluate=lambda _self, test, observed, _config: check_json(
                    observed.get("content", ""), test.get("assertion", {}).get("schema")
                ),
                accept_update=lambda *_: False,
                expected_value=self._expected_json,
            ),
            "trajectory": AssertionHandler(
                name="trajectory",
                evaluate=self._evaluate_trajectory,
                accept_update=lambda *_: False,
                expected_value=self._expected_trajectory,
            ),
        }

    async def run_suite(
        self,
        config_path: str,
        ids_filter: Optional[List[str]] = None,
        max_tests: int = 0,
        accept: bool = False,
        concurrency: int = 5,
        config_overrides: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], List[TestResult], bool]:
        with open(config_path, "r") as handle:
            config = yaml.safe_load(handle)

        if config_overrides:
            config.update(config_overrides)

        validate_config(config)

        results: List[TestResult] = []
        config_updated = False
        ids_filter = ids_filter or []
        tests_to_run: List[Dict[str, Any]] = []
        for test in config.get("tests", []):
            if ids_filter and test.get("id") not in ids_filter:
                continue
            tests_to_run.append(test)
            if max_tests and len(tests_to_run) >= max_tests:
                break

        semaphore = asyncio.Semaphore(concurrency) if concurrency > 0 else None
        self._semaphore = semaphore

        provider = self._get_provider(config)

        async def execute_test(test: Dict[str, Any]) -> Tuple[TestResult, bool]:
            handler = self._handlers.get(test.get("assertion", {}).get("type", "llm"), self._handlers["llm"])
            try:
                if semaphore is not None:
                    async with semaphore:
                        response = await self._invoke_subject(provider, config, test)
                else:
                    response = await self._invoke_subject(provider, config, test)
                observed = {"content": str(response.content), "tool_calls": response.tool_calls or []}
                metrics = response.metrics
            except Exception as exc:  # noqa: BLE001
                expected = handler.expected_value(test, config)
                primary_input = test.get("input", "")
                if not primary_input and isinstance(test.get("messages"), list):
                    for message in test["messages"]:
                        if message.get("role") == "user":
                            primary_input = message.get("content", "")
                            break
                result = TestResult(
                    id=test.get("id", ""),
                    assertion_type=handler.name,
                    passed=False,
                    score=0,
                    reason=f"Error invoking subject: {exc}",
                    actual="",
                    input=primary_input,
                    expected=expected,
                    assertion=test.get("assertion", {}),
                    model=config.get("model", ""),
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    latency=0.0,
                    cost=0.0,
                    tool_calls=[],
                )
                return result, False

            outcome_or_coro = handler.evaluate(self, test, observed, config)
            if asyncio.iscoroutine(outcome_or_coro):
                awaited = await outcome_or_coro
                outcome = cast(AssertionOutcome, awaited)
            else:
                outcome = cast(AssertionOutcome, outcome_or_coro)

            updated = False
            actual_content = str(observed.get("content", ""))
            tool_calls = cast(List[Dict[str, Any]], observed.get("tool_calls", []))

            if accept and not outcome.passed:
                updated = handler.accept_update(self, test, actual_content)

            expected = handler.expected_value(test, config)
            primary_input = test.get("input", "")
            if not primary_input and isinstance(test.get("messages"), list):
                for message in test["messages"]:
                    if message.get("role") == "user":
                        primary_input = message.get("content", "")
                        break
            result = TestResult(
                id=test.get("id", ""),
                assertion_type=handler.name,
                passed=outcome.passed,
                score=outcome.score,
                reason=outcome.reason,
                actual=actual_content,
                input=primary_input,
                expected=expected,
                assertion=test.get("assertion", {}),
                model=metrics.model,
                prompt_tokens=metrics.prompt_tokens,
                completion_tokens=metrics.completion_tokens,
                total_tokens=metrics.total_tokens,
                latency=metrics.latency,
                cost=metrics.cost,
                tool_calls=tool_calls,
            )
            return result, updated

        if not tests_to_run:
            return config, [], False

        try:
            executed = await asyncio.gather(*(execute_test(test) for test in tests_to_run))
            for result, updated in executed:
                results.append(result)
                config_updated |= updated
        finally:
            self._semaphore = None

        return config, results, config_updated

    def _build_messages(self, config: Dict[str, Any], test: Dict[str, Any]) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = []
        system_prompt = config.get("system_prompt")
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if isinstance(test.get("messages"), list):
            messages.extend(test["messages"])
        else:
            messages.append({"role": "user", "content": test.get("input", "")})

        return messages

    async def _invoke_subject(
        self,
        provider: BaseProvider,
        config: Dict[str, Any],
        test: Dict[str, Any],
    ) -> ProviderResponse:
        mock_response = test.get("mock_response")
        if mock_response is not None:
            content = str(mock_response.get("content", "")) if isinstance(mock_response, dict) else str(mock_response)
            tool_calls = []
            if isinstance(mock_response, dict):
                tool_calls = _normalize_tool_calls(mock_response.get("tool_calls", []) or [])
            metrics = InvocationMetrics(
                model=str(config.get("model", "")),
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency=0.0,
                cost=0.0,
            )
            return ProviderResponse(content=content, metrics=metrics, tool_calls=tool_calls)

        messages = self._build_messages(config, test)
        timeout = float(config.get("subject_timeout", 60) or 60)
        attempts = max(1, int(config.get("subject_retries", 1) or 1))
        backoff = float(config.get("subject_retry_backoff", 0.5) or 0.0)
        return await self._invoke_with_retries(
            label="subject",
            coro_factory=lambda: provider.chat(
                model=config["model"],
                messages=messages,
                temperature=float(config.get("subject_temperature", 0)),
            ),
            timeout=timeout,
            attempts=attempts,
            backoff=backoff,
        )

    def _evaluate_regex(
        self,
        _runner: "SuiteRunner",
        test: Dict[str, Any],
        observed: Dict[str, Any],
        _config: Dict[str, Any],
    ) -> AssertionOutcome:
        assertion = test.get("assertion", {})
        pattern = assertion.get("pattern") or assertion.get("expected")
        if not pattern:
            raise ValueError(f"Test {test.get('id')} missing regex pattern")
        return check_regex(observed.get("content", ""), str(pattern))

    async def _evaluate_llm(
        self,
        _runner: "SuiteRunner",
        test: Dict[str, Any],
        observed: Dict[str, Any],
        config: Dict[str, Any],
    ) -> AssertionOutcome:
        criteria = test.get("assertion", {}).get("expected_criteria") or test.get("expected_criteria")
        if not criteria:
            raise ValueError(f"Test {test.get('id')} missing expected_criteria for llm assertion")
        return await self._run_judge(
            user_input=test.get("input", ""),
            actual_output=observed.get("content", ""),
            criteria=criteria,
            model=config.get("judge_model", "gpt-4o-mini"),
            temperature=float(config.get("judge_temperature", 0)),
            max_retries=int(config.get("judge_retries", 1)),
            config=config,
        )

    def _evaluate_trajectory(
        self,
        _runner: "SuiteRunner",
        test: Dict[str, Any],
        observed: Dict[str, Any],
        _config: Dict[str, Any],
    ) -> AssertionOutcome:
        assertion = test.get("assertion", {})
        expected_raw = assertion.get("expected_trajectory", assertion.get("expected", []))
        expected = _normalize_expected_trajectory(expected_raw)
        max_calls = assertion.get("max_calls")
        max_calls_int = None
        if isinstance(max_calls, int):
            max_calls_int = max_calls
        elif isinstance(max_calls, str) and max_calls.isdigit():
            max_calls_int = int(max_calls)
        return check_trajectory(observed.get("tool_calls", []), expected, max_calls_int)

    async def _run_judge(
        self,
        user_input: str,
        actual_output: str,
        criteria: str,
        model: str,
        temperature: float,
        max_retries: int,
        config: Dict[str, Any],
    ) -> AssertionOutcome:
        provider = self._get_provider(config, role="judge")
        judge_payload = {
            "input": user_input,
            "output": actual_output,
            "criteria": criteria,
            "instruction": "Return JSON with keys: pass (bool), score (0-10 int), reason (string <=200 chars)",
        }
        judge_messages = [
            {"role": "system", "content": "You are a QA grader. Return compact JSON only."},
            {"role": "user", "content": json.dumps(judge_payload)},
        ]
        judge_timeout = float(config.get("judge_timeout", 30) or 30)
        judge_attempts = max(1, int(config.get("judge_retries", 1) or 1))
        backoff = float(config.get("judge_retry_backoff", 0.5) or 0.0)

        try:

            async def _call() -> ProviderResponse:
                return await provider.chat(
                    model=model,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                    messages=judge_messages,
                )

            if self._semaphore is not None:
                async with self._semaphore:
                    response = await self._invoke_with_retries(
                        label="judge",
                        coro_factory=_call,
                        timeout=judge_timeout,
                        attempts=judge_attempts,
                        backoff=backoff,
                    )
            else:
                response = await self._invoke_with_retries(
                    label="judge",
                    coro_factory=_call,
                    timeout=judge_timeout,
                    attempts=judge_attempts,
                    backoff=backoff,
                )

            data = json.loads(response.content)
            if not isinstance(data, dict):
                raise ValueError("Judge response was not an object")
            passed_value = bool(data.get("pass"))
            score_value = int(data.get("score", 0))
            reason_text = str(data.get("reason", "")) or "No reason provided"
            score_value = max(0, min(score_value, 10))
            return AssertionOutcome(
                passed=passed_value,
                score=score_value,
                reason=reason_text,
            )
        except Exception as exc:  # noqa: BLE001
            return AssertionOutcome(False, 0, f"Judge Error: {exc}")

    async def _call_with_timeout(self, coro: Any, timeout: float, label: str) -> Any:
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError as exc:
            raise TimeoutError(f"{label} call timed out after {timeout} seconds") from exc

    async def _invoke_with_retries(
        self,
        label: str,
        coro_factory: Callable[[], Any],
        timeout: float,
        attempts: int,
        backoff: float,
    ) -> Any:
        attempts = max(1, attempts)
        delay = backoff
        last_exc: Optional[Exception] = None
        for attempt in range(1, attempts + 1):
            try:
                return await self._call_with_timeout(coro_factory(), timeout, label)
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
                logger.warning("%s attempt %s/%s failed: %s", label, attempt, attempts, exc)
                if attempt >= attempts:
                    raise
                if delay > 0:
                    await asyncio.sleep(delay)
                    delay *= 2
        if last_exc:
            raise last_exc
        raise RuntimeError(f"{label} failed without exception")

    def _accept_exact(self, _runner: "SuiteRunner", test: Dict[str, Any], actual: str) -> bool:
        assertion = test.setdefault("assertion", {})
        assertion["expected"] = actual
        self.console.print(f"[bold yellow]📝 Updated baseline for {test.get('id')} (exact)[/bold yellow]")
        return True

    def _accept_contains(self, _runner: "SuiteRunner", test: Dict[str, Any], actual: str) -> bool:
        assertion = test.setdefault("assertion", {})
        assertion["type"] = "exact"
        assertion["expected"] = actual
        self.console.print(f"[bold yellow]📝 Converted {test.get('id')} to exact match with new baseline[/bold yellow]")
        return True

    @staticmethod
    def _expected_exact(test: Dict[str, Any], _config: Dict[str, Any]) -> str:
        return str(test.get("assertion", {}).get("expected", ""))

    @staticmethod
    def _expected_contains(test: Dict[str, Any], _config: Dict[str, Any]) -> str:
        return str(test.get("assertion", {}).get("expected", ""))

    @staticmethod
    def _expected_regex(test: Dict[str, Any], _config: Dict[str, Any]) -> str:
        assertion = test.get("assertion", {})
        return str(assertion.get("pattern", assertion.get("expected", "")))

    @staticmethod
    def _expected_llm(test: Dict[str, Any], _config: Dict[str, Any]) -> str:
        assertion = test.get("assertion", {})
        return str(assertion.get("expected_criteria", test.get("expected_criteria", "")))

    @staticmethod
    def _expected_trajectory(test: Dict[str, Any], _config: Dict[str, Any]) -> str:
        assertion = test.get("assertion", {})
        expected_raw = assertion.get("expected_trajectory", assertion.get("expected", []))
        return json.dumps(_normalize_expected_trajectory(expected_raw))

    @staticmethod
    def _expected_json(test: Dict[str, Any], _config: Dict[str, Any]) -> str:
        schema = test.get("assertion", {}).get("schema")
        if schema is None:
            return "Valid JSON"
        try:
            return json.dumps(schema)
        except Exception:  # noqa: BLE001
            return str(schema)


def init_project(path: str = "evals.yaml") -> None:
    sample_config = {
        "system_prompt": "You are a helpful assistant.",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "judge_model": "gpt-4o-mini",
        "tests": [
            {
                "id": "sanity_contains",
                "input": "Say 'hello world'",
                "assertion": {"type": "contains", "expected": "hello world"},
            },
            {
                "id": "sanity_exact",
                "input": "Respond only with the word banana",
                "assertion": {"type": "exact", "expected": "banana"},
            },
            {
                "id": "sanity_regex",
                "input": "Provide a US zip code",
                "assertion": {"type": "regex", "pattern": r"\b\d{5}\b"},
            },
            {
                "id": "tone_llm",
                "input": "Explain quantum physics to a 5yo",
                "assertion": {
                    "type": "llm",
                    "expected_criteria": "Must use a metaphor. Must be under 50 words.",
                },
            },
        ],
    }
    with open(path, "w") as handle:
        yaml.dump(sample_config, handle, sort_keys=False)
    console.print(f"[bold green]✅ Created {path}. Run 'python main.py' to test.[/bold green]")


def update_config_file(path: str, config: Dict[str, Any]) -> None:
    if HAS_RUAMEL and YAML is not None:
        yaml_handler = YAML()
        yaml_handler.preserve_quotes = True
        yaml_handler.default_flow_style = False
        with open(path, "w") as handle:
            yaml_handler.dump(config, handle)
    else:
        with open(path, "w") as handle:
            yaml.dump(config, handle, sort_keys=False, default_flow_style=False)
    console.print(f"[bold green]✅ Baseline updated in {path}[/bold green]")


def update_test_baseline(config_path: str, test_id: str, new_value: str) -> bool:
    yaml_handler = None
    if HAS_RUAMEL and YAML is not None:
        yaml_handler = YAML()
        yaml_handler.preserve_quotes = True
        yaml_handler.default_flow_style = False
        with open(config_path, "r") as handle:
            config = yaml_handler.load(handle)
    else:
        with open(config_path, "r") as handle:
            config = yaml.safe_load(handle)

    updated = False
    for test in config.get("tests", []):
        if test.get("id") == test_id:
            assertion = test.get("assertion", {})
            assertion_type = assertion.get("type", "llm")
            if assertion_type in {"exact", "contains"}:
                if assertion_type == "contains":
                    assertion["type"] = "exact"
                assertion["expected"] = new_value
                updated = True
            elif assertion_type == "llm":
                assertion["expected_criteria"] = new_value
                updated = True
            break

    if updated:
        if HAS_RUAMEL and yaml_handler is not None:
            with open(config_path, "w") as handle:
                yaml_handler.dump(config, handle)
        else:
            with open(config_path, "w") as handle:
                yaml.dump(config, handle, sort_keys=False, default_flow_style=False)
    return updated


def load_suite_results(
    path: str,
    ids_filter: Optional[List[str]],
    max_tests: int,
    runner: Optional[SuiteRunner] = None,
) -> Tuple[Dict[str, Any], List[TestResult]]:
    _, ext = os.path.splitext(path)
    if ext.lower() == ".json":
        with open(path, "r") as handle:
            payload = json.load(handle)
        config = payload.get("config", {}) or {}
        raw_results = payload.get("results", []) or []
        filtered: List[TestResult] = []
        ids_filter = ids_filter or []
        for raw in raw_results:
            candidate = TestResult.from_dict(raw)
            if ids_filter and candidate.id not in ids_filter:
                continue
            filtered.append(candidate)
            if max_tests and len(filtered) >= max_tests:
                break
        return config, filtered

    console.print(f"[yellow]⚠️ {path} is not a JSON results file; re-running tests to compute diff.[/yellow]")
    runner = runner or SuiteRunner()
    config, results, _ = asyncio.run(runner.run_suite(path, ids_filter, max_tests))
    return config, results


def diff_suites(before_path: str, after_path: str, ids_filter: List[str], max_tests: int) -> None:
    runner = SuiteRunner()
    _, before_results = load_suite_results(before_path, ids_filter, max_tests, runner)
    _, after_results = load_suite_results(after_path, ids_filter, max_tests, runner)

    before_map = {r.id: r for r in before_results}
    after_map = {r.id: r for r in after_results}

    table = Table(title="Baseline Diff")
    table.add_column("ID", style="cyan")
    table.add_column("Before", style="dim")
    table.add_column("After", style="dim")
    table.add_column("Delta")

    all_ids = sorted(set(before_map) | set(after_map))
    for tid in all_ids:
        b = before_map.get(tid)
        a = after_map.get(tid)
        b_score = b.score if b else "-"
        a_score = a.score if a else "-"
        delta = "-" if not (b and a) else a.score - b.score
        table.add_row(tid, str(b_score), str(a_score), str(delta))

    console.print(table)


__all__ = [
    "SuiteRunner",
    "TestResult",
    "init_project",
    "update_config_file",
    "update_test_baseline",
    "load_suite_results",
    "diff_suites",
    "validate_config",
]
