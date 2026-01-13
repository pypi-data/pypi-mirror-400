import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import unittest

from gwaslab_agent.g_llm import extract_token_usage, accumulate_token_usage, snapshot_counters, log_run_totals


class DummyLog:
    def __init__(self):
        self.messages = []

    def write(self, msg, verbose=True):
        self.messages.append(str(msg))


class DummyMsg:
    def __init__(self, response_metadata=None, usage_metadata=None):
        self.response_metadata = response_metadata or {}
        self.usage_metadata = usage_metadata


class TestLLMUtils(unittest.TestCase):
    def test_extract_token_usage_from_response(self):
        msg = DummyMsg(response_metadata={"token_usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}})
        usage = extract_token_usage(msg)
        self.assertEqual(usage["input"], 10)
        self.assertEqual(usage["output"], 5)
        self.assertEqual(usage["total"], 15)

    def test_extract_token_usage_from_usage_metadata(self):
        msg = DummyMsg(usage_metadata={"input_tokens": 8, "output_tokens": 3, "total_tokens": 11})
        usage = extract_token_usage(msg)
        self.assertEqual(usage["input"], 8)
        self.assertEqual(usage["output"], 3)
        self.assertEqual(usage["total"], 11)

    def test_accumulate_token_usage(self):
        counter = {}
        accumulate_token_usage(counter, {"input": 2, "output": 3, "total": 5})
        accumulate_token_usage(counter, {"input": 4, "output": 1, "total": 5})
        self.assertEqual(counter["input"], 6)
        self.assertEqual(counter["output"], 4)
        self.assertEqual(counter["total"], 10)

    def test_snapshot_and_log_run_totals(self):
        counter = {"input": 100, "output": 50, "total": 150}
        start = snapshot_counters(counter)
        accumulate_token_usage(counter, {"input": 10, "output": 20, "total": 30})
        end = snapshot_counters(counter)
        log = DummyLog()
        log_run_totals(log, "test", start, end, verbose=True)
        self.assertTrue(any("This test" in m for m in log.messages))
        self.assertTrue(any("Accumulative" in m for m in log.messages))


if __name__ == "__main__":
    unittest.main()

