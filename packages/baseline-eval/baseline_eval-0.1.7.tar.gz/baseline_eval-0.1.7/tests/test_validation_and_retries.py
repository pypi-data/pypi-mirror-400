import asyncio
import tempfile
import unittest
from pathlib import Path

import yaml
from baseline.providers.base import InvocationMetrics, ProviderResponse
from baseline.runner import SuiteRunner, validate_config


class FlakyProvider:
    name = "fake"

    def __init__(self, subject_failures: int = 0, judge_failures: int = 0):
        self.subject_failures = subject_failures
        self.judge_failures = judge_failures
        self.calls = {"subject": 0, "judge": 0}

    async def chat(self, model, messages, temperature=0.0, response_format=None):  # noqa: D401
        is_judge = any(msg.get("role") == "system" and "QA grader" in str(msg.get("content", "")) for msg in messages)
        role = "judge" if is_judge else "subject"
        self.calls[role] += 1

        if role == "subject" and self.calls[role] <= self.subject_failures:
            raise RuntimeError("subject boom")
        if role == "judge" and self.calls[role] <= self.judge_failures:
            raise RuntimeError("judge boom")

        content = "ok"
        if role == "judge":
            content = '{"pass": true, "score": 9, "reason": "ok"}'

        metrics = InvocationMetrics(
            model=model,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency=0.0,
            cost=0.0,
        )
        return ProviderResponse(content=content, metrics=metrics, tool_calls=[])


class ValidationTests(unittest.TestCase):
    def test_validate_requires_tests(self):
        with self.assertRaises(ValueError):
            validate_config({"tests": []})

    def test_validate_requires_id(self):
        with self.assertRaises(ValueError):
            validate_config({"tests": [{"input": "hi", "assertion": {"type": "exact", "expected": "hi"}}]})

    def test_validate_requires_llm_criteria(self):
        with self.assertRaises(ValueError):
            validate_config(
                {
                    "tests": [
                        {
                            "id": "missing_criteria",
                            "input": "hi",
                            "assertion": {"type": "llm"},
                        }
                    ]
                }
            )


class RetryTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write_config(self, *, subject_retries=1, judge_retries=1, provider_name="fake"):
        config = {
            "system_prompt": "You are helpful.",
            "provider": provider_name,
            "judge_provider": provider_name,
            "model": "fake-model",
            "judge_model": "fake-judge",
            "subject_retries": subject_retries,
            "judge_retries": judge_retries,
            "subject_retry_backoff": 0,
            "judge_retry_backoff": 0,
            "tests": [
                {
                    "id": "t1",
                    "input": "Say ok",
                    "assertion": {"type": "llm", "expected_criteria": "be concise"},
                }
            ],
        }
        path = Path(self.tmpdir.name) / "evals.yaml"
        with open(path, "w", encoding="utf-8") as handle:
            yaml.dump(config, handle, sort_keys=False)
        return str(path)

    def test_subject_retries_and_recovers(self):
        config_path = self._write_config(subject_retries=2)
        provider = FlakyProvider(subject_failures=1)
        runner = SuiteRunner(provider=provider)

        _, results, _ = asyncio.run(runner.run_suite(config_path))

        self.assertEqual(provider.calls["subject"], 2)
        self.assertTrue(results[0].passed)

    def test_subject_retries_exhaust_and_fails(self):
        config_path = self._write_config(subject_retries=2)
        provider = FlakyProvider(subject_failures=3)
        runner = SuiteRunner(provider=provider)

        _, results, _ = asyncio.run(runner.run_suite(config_path))

        self.assertEqual(provider.calls["subject"], 2)
        self.assertFalse(results[0].passed)
        self.assertIn("Error invoking subject", results[0].reason)

    def test_judge_retries_and_recovers(self):
        config_path = self._write_config(judge_retries=2)
        provider = FlakyProvider(judge_failures=1)
        runner = SuiteRunner(provider=provider)

        _, results, _ = asyncio.run(runner.run_suite(config_path))

        self.assertEqual(provider.calls["subject"], 1)
        self.assertEqual(provider.calls["judge"], 2)
        self.assertTrue(results[0].passed)


if __name__ == "__main__":
    unittest.main()
