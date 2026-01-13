import asyncio
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

import yaml
from baseline.core import SuiteRunner


class FakeCompletions:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    async def create(self, **kwargs):
        if not self._responses:
            raise AssertionError("No more fake responses available")
        self.calls.append(kwargs)
        item = self._responses.pop(0)
        usage = None
        tool_calls = None
        if isinstance(item, dict):
            content = item.get("content")
            usage = item.get("usage")
            tool_calls = item.get("tool_calls")
        else:
            content = item
        message = SimpleNamespace(content=content, tool_calls=tool_calls)
        choice = SimpleNamespace(message=message)
        response = SimpleNamespace(choices=[choice])
        if usage is not None:
            response.usage = usage
        return response


class FakeClient:
    def __init__(self, responses):
        self.chat = SimpleNamespace(completions=FakeCompletions(responses))


class SuiteRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write_config(self, tests):
        config = {
            "system_prompt": "You are a helpful assistant.",
            "model": "gpt-4o-mini",
            "tests": tests,
        }
        path = Path(self.tmpdir.name) / "evals.yaml"
        with open(path, "w", encoding="utf-8") as handle:
            yaml.dump(config, handle, sort_keys=False)
        return str(path)

    def test_exact_assertion_passes(self):
        config_path = self._write_config(
            [
                {
                    "id": "exact_ok",
                    "input": "Say hello",
                    "assertion": {"type": "exact", "expected": "hello"},
                }
            ]
        )
        runner = SuiteRunner(client=FakeClient(["hello"]))

        config, results, updated = asyncio.run(runner.run_suite(config_path))

        self.assertFalse(updated)
        self.assertEqual(config["tests"][0]["assertion"]["expected"], "hello")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].passed)
        self.assertEqual(results[0].assertion_type, "exact")

    def test_accept_mode_converts_contains_to_exact(self):
        config_path = self._write_config(
            [
                {
                    "id": "contains_update",
                    "input": "Respond with a status",
                    "assertion": {"type": "contains", "expected": "ok"},
                }
            ]
        )
        client = FakeClient(["All systems nominal"])
        runner = SuiteRunner(client=client)

        config, results, updated = asyncio.run(runner.run_suite(config_path, accept=True))

        self.assertTrue(updated)
        self.assertFalse(results[0].passed)
        assertion = config["tests"][0]["assertion"]
        self.assertEqual(assertion["type"], "exact")
        self.assertEqual(assertion["expected"], "All systems nominal")

    def test_records_latency_tokens_and_cost(self):
        config_path = self._write_config(
            [
                {
                    "id": "metrics",
                    "input": "Say hello",
                    "assertion": {"type": "exact", "expected": "hello"},
                }
            ]
        )

        usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        responses = [{"content": "hello", "usage": usage}]
        runner = SuiteRunner(client=FakeClient(responses))

        start = time.perf_counter()
        _, results, _ = asyncio.run(runner.run_suite(config_path))
        elapsed = time.perf_counter() - start

        result = results[0]
        self.assertEqual(result.prompt_tokens, 10)
        self.assertEqual(result.completion_tokens, 20)
        self.assertEqual(result.total_tokens, 30)
        self.assertGreater(result.latency, 0.0)
        self.assertLessEqual(result.latency, elapsed)
        expected_cost = (10 / 1000) * 0.00015 + (20 / 1000) * 0.0006
        self.assertAlmostEqual(result.cost, expected_cost, places=9)

    def test_ids_filter_limits_invocations(self):
        config_path = self._write_config(
            [
                {
                    "id": "first",
                    "input": "Say first",
                    "assertion": {"type": "exact", "expected": "one"},
                },
                {
                    "id": "second",
                    "input": "Say second",
                    "assertion": {"type": "exact", "expected": "two"},
                },
            ]
        )
        client = FakeClient(["one", "two"])
        runner = SuiteRunner(client=client)

        config, results, updated = asyncio.run(runner.run_suite(config_path, ids_filter=["second"]))

        self.assertFalse(updated)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "second")
        self.assertEqual(len(client.chat.completions.calls), 1)

    def test_mock_response_shortcuts_provider(self):
        tests = [
            {
                "id": "mocked",
                "input": "hi",
                "mock_response": {"content": "hey", "tool_calls": [{"name": "noop"}]},
                "assertion": {"type": "exact", "expected": "hey"},
            }
        ]
        config_path = self._write_config(tests)
        client = FakeClient(["should_not_be_used"])

        _, results, _ = asyncio.run(SuiteRunner(client=client).run_suite(config_path))

        self.assertTrue(results[0].passed)
        self.assertEqual(len(client.chat.completions.calls), 0)
        self.assertEqual(results[0].tool_calls[0]["name"], "noop")

    def test_mock_response_function_style_tool_calls_are_normalized(self):
        tests = [
            {
                "id": "mocked_func",
                "input": "hi",
                "mock_response": {
                    "content": "hey",
                    "tool_calls": [{"function": {"name": "lookup_customer", "arguments": '{"user_id": "1"}'}}],
                },
                "assertion": {
                    "type": "trajectory",
                    "expected_trajectory": [{"name": "lookup_customer", "arguments": {"user_id": "1"}}],
                },
            }
        ]
        config_path = self._write_config(tests)

        runner = SuiteRunner(client=FakeClient(["skip"]))
        _, results, _ = asyncio.run(runner.run_suite(config_path))

        self.assertTrue(results[0].passed)
        self.assertEqual(results[0].tool_calls[0]["name"], "lookup_customer")

    def test_messages_list_is_used_for_multi_turn(self):
        tests = [
            {
                "id": "multi_turn",
                "messages": [
                    {"role": "user", "content": "hi"},
                    {"role": "assistant", "content": "hello"},
                    {"role": "user", "content": "how are you?"},
                ],
                "assertion": {"type": "exact", "expected": "I am well"},
            }
        ]
        config_path = self._write_config(tests)
        client = FakeClient(["I am well"])

        _, results, _ = asyncio.run(SuiteRunner(client=client).run_suite(config_path))

        self.assertTrue(results[0].passed)
        call_messages = client.chat.completions.calls[0]["messages"]
        self.assertEqual(call_messages[0]["role"], "system")
        self.assertEqual(call_messages[1]["content"], "hi")
        self.assertEqual(call_messages[3]["content"], "how are you?")

    def test_trajectory_assertion_passes(self):
        tests = [
            {
                "id": "trajectory_ok",
                "input": "Check balance",
                "assertion": {
                    "type": "trajectory",
                    "expected_trajectory": [
                        {"name": "lookup_customer", "arguments": {"user_id": "123"}},
                        {"name": "fetch_balance"},
                    ],
                },
            }
        ]
        tool_calls = [
            {"function": {"name": "lookup_customer", "arguments": '{"user_id": "123"}'}},
            {"function": {"name": "fetch_balance", "arguments": "{}"}},
        ]
        responses = [
            {"content": "Here you go", "tool_calls": tool_calls},
        ]
        client = FakeClient(responses)

        _, results, _ = asyncio.run(SuiteRunner(client=client).run_suite(self._write_config(tests)))

        self.assertTrue(results[0].passed)
        self.assertEqual(results[0].tool_calls[0]["name"], "lookup_customer")

    def test_trajectory_assertion_fails_on_mismatch(self):
        tests = [
            {
                "id": "trajectory_bad",
                "input": "Check balance",
                "assertion": {
                    "type": "trajectory",
                    "expected_trajectory": [
                        {"name": "fetch_balance"},
                    ],
                },
            }
        ]
        responses = [
            {"content": "Here you go", "tool_calls": [{"function": {"name": "other"}}]},
        ]
        client = FakeClient(responses)

        _, results, _ = asyncio.run(SuiteRunner(client=client).run_suite(self._write_config(tests)))

        self.assertFalse(results[0].passed)
        self.assertIn("Expected fetch_balance", results[0].reason)

    def test_json_assertion_passes_with_schema(self):
        tests = [
            {
                "id": "json_ok",
                "input": "Return profile",
                "assertion": {
                    "type": "json",
                    "schema": {
                        "type": "object",
                        "required": ["name", "age"],
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer"},
                        },
                    },
                },
            }
        ]
        response = {"content": '{"name": "Ada", "age": 25}'}
        runner = SuiteRunner(client=FakeClient([response]))

        _, results, _ = asyncio.run(runner.run_suite(self._write_config(tests)))

        self.assertTrue(results[0].passed)
        self.assertEqual(results[0].reason, "Valid JSON")

    def test_json_assertion_fails_on_schema(self):
        tests = [
            {
                "id": "json_bad",
                "input": "Return profile",
                "assertion": {
                    "type": "json",
                    "schema": {
                        "type": "object",
                        "required": ["name", "age"],
                        "properties": {
                            "name": {"type": "string"},
                            "age": {"type": "integer"},
                        },
                    },
                },
            }
        ]
        response = {"content": '{"name": "Ada", "age": "old"}'}
        runner = SuiteRunner(client=FakeClient([response]))

        _, results, _ = asyncio.run(runner.run_suite(self._write_config(tests)))

        self.assertFalse(results[0].passed)
        self.assertIn("Schema validation failed", results[0].reason)

    def test_json_assertion_fails_on_invalid_json(self):
        tests = [
            {
                "id": "json_syntax",
                "input": "Return profile",
                "assertion": {"type": "json"},
            }
        ]
        response = {"content": "{not valid json"}
        runner = SuiteRunner(client=FakeClient([response]))

        _, results, _ = asyncio.run(runner.run_suite(self._write_config(tests)))

        self.assertFalse(results[0].passed)
        self.assertEqual(results[0].reason, "Invalid JSON syntax")


if __name__ == "__main__":
    unittest.main()
