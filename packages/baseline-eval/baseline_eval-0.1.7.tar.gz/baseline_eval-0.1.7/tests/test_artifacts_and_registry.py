import json
import tempfile
import unittest
from pathlib import Path

from baseline import artifacts
from baseline.providers.registry import create_provider


class _DummyResult:
    def __init__(self, *, id_: str, passed: bool, score: int, reason: str):
        self.id = id_
        self.passed = passed
        self.score = score
        self.reason = reason
        self.latency = 0.123
        self.prompt_tokens = 1
        self.completion_tokens = 2
        self.total_tokens = 3
        self.cost = 0.004
        self.assertion_type = "exact"
        self.actual = ""
        self.input = ""
        self.expected = ""
        self.assertion = {}
        self.tool_calls = []

    def to_dict(self):
        return {
            "id": self.id,
            "passed": self.passed,
            "score": self.score,
            "reason": self.reason,
            "latency": self.latency,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost": self.cost,
            "assertion_type": self.assertion_type,
            "actual": self.actual,
            "input": self.input,
            "expected": self.expected,
            "assertion": self.assertion,
            "tool_calls": self.tool_calls,
        }


class ArtifactTests(unittest.TestCase):
    def test_write_json_and_junit(self):
        config = {"model": "test-model"}
        results = [
            _DummyResult(id_="ok", passed=True, score=10, reason="fine"),
            _DummyResult(id_="bad", passed=False, score=0, reason="oops"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "results.json"
            junit_path = Path(tmp) / "junit.xml"

            artifacts.write_json(str(json_path), config, results)
            artifacts.write_junit(str(junit_path), results)

            data = json.loads(json_path.read_text())
            self.assertEqual(data["config"], config)
            self.assertEqual(len(data["results"]), 2)
            self.assertEqual(data["results"][1]["reason"], "oops")

            xml = junit_path.read_text()
            self.assertIn('tests="2"', xml)
            self.assertIn('failures="1"', xml)
            self.assertIn('name="bad"', xml)
            self.assertIn('<failure message="score=0">oops</failure>', xml)


class ProviderRegistryTests(unittest.TestCase):
    def test_missing_provider_key_raises(self):
        with self.assertRaises(ValueError) as ctx:
            create_provider("openai")
        self.assertIn("OPENAI_API_KEY", str(ctx.exception))

    def test_unknown_provider(self):
        with self.assertRaises(ValueError):
            create_provider("unknown")


if __name__ == "__main__":
    unittest.main()
