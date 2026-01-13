import asyncio
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

import yaml
from baseline.core import SuiteRunner


class TimedCompletions:
    def __init__(self, responses, delay: float):
        self._responses = list(responses)
        self.delay = delay
        self.calls = []

    async def create(self, **kwargs):
        if not self._responses:
            raise AssertionError("No more fake responses available")
        self.calls.append(kwargs)
        await asyncio.sleep(self.delay)
        content = self._responses.pop(0)
        message = SimpleNamespace(content=content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class AsyncFakeClient:
    def __init__(self, responses, delay: float = 0.05):
        self.chat = SimpleNamespace(completions=TimedCompletions(responses, delay))


class AsyncSuiteIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write_config(self, tests):
        config = {
            "system_prompt": "You are helpful.",
            "model": "gpt-4o-mini",
            "judge_model": "gpt-4o-mini",
            "tests": tests,
        }
        path = Path(self.tmpdir.name) / "evals.yaml"
        with open(path, "w", encoding="utf-8") as handle:
            yaml.dump(config, handle, sort_keys=False)
        return str(path)

    def test_parallel_subject_and_judge_runs_concurrently(self):
        config_path = self._write_config(
            [
                {
                    "id": "t1",
                    "input": "Say first",
                    "assertion": {"type": "llm", "expected_criteria": "be concise"},
                },
                {
                    "id": "t2",
                    "input": "Say second",
                    "assertion": {"type": "llm", "expected_criteria": "be concise"},
                },
            ]
        )

        responses = [
            "first output",  # subject t1
            "second output",  # subject t2
            '{"pass": true, "score": 9, "reason": "ok"}',  # judge t1
            '{"pass": true, "score": 9, "reason": "ok"}',  # judge t2
        ]
        client = AsyncFakeClient(responses, delay=0.05)

        start = time.perf_counter()
        config, results, updated = asyncio.run(SuiteRunner(client=client).run_suite(config_path, concurrency=2))
        elapsed = time.perf_counter() - start

        self.assertFalse(updated)
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.passed for r in results))
        self.assertEqual(len(client.chat.completions.calls), 4)
        # With two tests and 0.05s per call, concurrency=2 should finish well under sequential 0.2s
        self.assertLess(elapsed, 0.16)


if __name__ == "__main__":
    unittest.main()
