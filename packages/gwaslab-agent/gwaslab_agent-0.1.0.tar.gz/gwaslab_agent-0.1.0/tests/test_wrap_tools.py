import os
import sys
import json
import unittest
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

sys.path.insert(0, "/home/yunye/work/gwaslab/src")

from gwaslab_agent.g_wrap_tools import wrap_main_agent_method, wrap_loader_method, _resolve_df_value
from gwaslab_agent.g_build_tools import RESULTS
from gwaslab_agent.d_data_registry import DataRegistry


class FakeLog:
    def __init__(self):
        self.log_text = ""

    def write(self, text, verbose=True):
        self.log_text += (text or "")

    def getvalue(self):
        return self.log_text

    def combine(self, other_log, pre=False):
        try:
            self.log_text += getattr(other_log, 'log_text', '')
        except Exception:
            pass


class FakeSelf:
    def __init__(self):
        self.log = FakeLog()
        self.RESULTS = RESULTS
        self.archive = []
        self.last_kwargs = None


class TestWrapTools(unittest.TestCase):
    def test_wrap_main_agent_method_inplace_injection_and_dataframe(self):
        fs = FakeSelf()

        def method_with_inplace(a, inplace=True):
            fs.last_kwargs = {"a": a, "inplace": inplace}
            return pd.DataFrame({"x": [1, 2], "y": [3, 4]})

        wrapped = wrap_main_agent_method(fs, "filter_p_threshold", method_with_inplace)
        out = wrapped(a=123)
        payload = json.loads(out)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["type"], "DataFrame")
        self.assertIn("df_id", payload["data"])  # registered in RESULTS
        # inplace should be injected to False by wrapper
        self.assertEqual(fs.last_kwargs["inplace"], False)

    def test_wrap_main_agent_method_kwargs_resolution_via_df_registry(self):
        fs = FakeSelf()
        df = pd.DataFrame({"col": [10, 20, 30, 40]})
        df_id = fs.RESULTS.put(df)

        def echo_kwargs(values=None):
            return {"values": values}

        wrapped = wrap_main_agent_method(fs, "any_method", echo_kwargs)
        # Pass reference string; expect resolution to list of first 2 values
        out = wrapped(values=f"{df_id}.col[:2]")
        payload = json.loads(out)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["type"], "dict")
        self.assertEqual(payload["data"]["values"], [10, 20])

    def test_log_scrubbing_removes_usage_lines(self):
        fs = FakeSelf()

        def method_noop():
            fs.log.write("[USAGE] This call: prompt=10, completion=5, total=15")
            return "ok"

        wrapped = wrap_main_agent_method(fs, "noop", method_noop)
        out = wrapped()
        payload = json.loads(out)
        self.assertEqual(payload["status"], "success")
        # Scrubber should remove usage line; log becomes empty string
        self.assertEqual(payload["log"], "")

    def test_wrap_loader_method_dataframe_and_none(self):
        fs = FakeSelf()

        def loader_df():
            return pd.DataFrame({"a": [1, 2, 3]})

        def loader_none():
            # simulate successful execution with no return value
            return None

        wrapped_df = wrap_loader_method(fs, "load_df", loader_df)
        payload_df = json.loads(wrapped_df())
        self.assertEqual(payload_df["status"], "success")
        self.assertEqual(payload_df["type"], "DataFrame")
        self.assertIn("rows", payload_df["data"])  # has preview metadata

        wrapped_none = wrap_loader_method(fs, "load_none", loader_none)
        payload_none = json.loads(wrapped_none())
        self.assertEqual(payload_none["status"], "success")
        self.assertEqual(payload_none["type"], "none")
        self.assertIn("Executed successfully", payload_none["data"])

    def test_resolve_df_value_dict_highlight_query(self):
        fs = FakeSelf()
        fs.RESULTS = DataRegistry()
        df = pd.DataFrame({
            "CHR": [1, 2, 3, 4],
            "SNPID": ["rs1", "rs2", "rs3", "rs4"]
        })
        df_id = fs.RESULTS.put(df)  # should be df_0
        self.assertEqual(df_id, "df_0")
        v = {"highlight": 'df_0.query("CHR % 2 == 0").SNPID'}
        out = _resolve_df_value(fs, v)
        self.assertEqual(out["highlight"], ["rs2", "rs4"])

    def test_resolve_df_value_query_modulo_odd(self):
        fs = FakeSelf()
        fs.RESULTS = DataRegistry()
        df = pd.DataFrame({
            "CHR": [1, 2, 3, 4],
            "SNPID": ["rs1", "rs2", "rs3", "rs4"]
        })
        df_id = fs.RESULTS.put(df)
        self.assertEqual(df_id, "df_0")
        out = _resolve_df_value(fs, 'df_0.query("CHR % 2 == 1").SNPID')
        self.assertEqual(out, ["rs1", "rs3"])

    def test_resolve_df_value_list_and_string_simple(self):
        fs = FakeSelf()
        fs.RESULTS = DataRegistry()
        df = pd.DataFrame({
            "CHR": [1, 2, 3],
            "SNPID": ["a", "b", "c"]
        })
        df_id = fs.RESULTS.put(df)  # df_0
        self.assertEqual(df_id, "df_0")
        out_list = _resolve_df_value(fs, ['df_0.SNPID[:2]', 'x'])
        self.assertEqual(out_list[0], ["a", "b"])
        self.assertEqual(out_list[1], "x")
        out_str = _resolve_df_value(fs, 'df_0.SNPID')
        self.assertEqual(out_str, ["a", "b", "c"])

    def test_resolve_df_value_column_case_insensitive(self):
        fs = FakeSelf()
        fs.RESULTS = DataRegistry()
        df = pd.DataFrame({
            "CHR": [1, 2, 3],
            "SNPID": ["a", "b", "c"]
        })
        df_id = fs.RESULTS.put(df)  # df_0
        self.assertEqual(df_id, "df_0")
        out_lower = _resolve_df_value(fs, 'df_0.snpid')
        self.assertEqual(out_lower, ["a", "b", "c"])
        out_mixed = _resolve_df_value(fs, 'df_0.SnPiD[:2]')
        self.assertEqual(out_mixed, ["a", "b"])

    def test_resolve_df_value_query_single_quote_and_slice(self):
        fs = FakeSelf()
        fs.RESULTS = DataRegistry()
        df = pd.DataFrame({
            "CHR": [1, 2, 3, 4],
            "SNPID": ["rs1", "rs2", "rs3", "rs4"]
        })
        df_id = fs.RESULTS.put(df)  # df_0
        self.assertEqual(df_id, "df_0")
        out = _resolve_df_value(fs, "df_0.query('CHR > 2').SNPID[:1]")
        self.assertEqual(out, ["rs3"])

    def test_resolve_df_value_nested_dict(self):
        fs = FakeSelf()
        fs.RESULTS = DataRegistry()
        df = pd.DataFrame({
            "CHR": [1, 2, 3],
            "SNPID": ["a", "b", "c"]
        })
        fs.RESULTS.put(df)  # df_0
        v = {"outer": {"inner": "df_0.SNPID[:2]"}}
        out = _resolve_df_value(fs, v)
        self.assertEqual(out["outer"]["inner"], ["a", "b"])

    def test_resolve_df_value_non_expr_passthrough(self):
        fs = FakeSelf()
        v = "not_an_expr"
        out = _resolve_df_value(fs, v)
        self.assertEqual(out, "not_an_expr")

    def test_resolve_df_value_invalid_query_raises(self):
        fs = FakeSelf()
        fs.RESULTS = DataRegistry()
        df = pd.DataFrame({
            "CHR": [1, 2, 3],
            "SNPID": ["a", "b", "c"]
        })
        fs.RESULTS.put(df)  # df_0
        with self.assertRaises(Exception):
            _resolve_df_value(fs, 'df_0.query("NOPE > 2").SNPID')

    def test_resolve_df_value_query_string_in_list(self):
        fs = FakeSelf()
        fs.RESULTS = DataRegistry()
        df = pd.DataFrame({
            "CHR": [1, 2, 3, 4],
            "SNPID": ["rs1", "rs2", "rs3", "rs4"]
        })
        df_id = fs.RESULTS.put(df)  # df_0
        self.assertEqual(df_id, "df_0")
        values_str = '["df_0.query(\\"CHR % 2 == 0\\").SNPID"]'
        out = _resolve_df_value(fs, values_str)
        self.assertEqual(out[0], ["rs2", "rs4"])

    def test_wrap_loader_method_error_traceback(self):
        fs = FakeSelf()
        def loader_fail():
            raise ValueError("loader failed")
        wrapped = wrap_loader_method(fs, "loader_fail", loader_fail)
        payload = json.loads(wrapped())
        self.assertEqual(payload["status"], "error")
        self.assertIn("traceback", payload)
        self.assertIn("ValueError", payload["traceback"])

    def test_wrap_main_agent_method_error_traceback(self):
        fs = FakeSelf()
        def main_fail():
            raise RuntimeError("main failed")
        wrapped = wrap_main_agent_method(fs, "main_fail", main_fail)
        payload = json.loads(wrapped())
        self.assertEqual(payload["status"], "error")
        self.assertIn("traceback", payload)
        self.assertIn("RuntimeError", payload["traceback"])

if __name__ == "__main__":
    unittest.main()
