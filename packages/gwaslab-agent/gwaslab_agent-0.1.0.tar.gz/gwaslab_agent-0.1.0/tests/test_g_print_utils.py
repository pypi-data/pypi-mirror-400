import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
sys.path.insert(0, "/home/yunye/work/gwaslab/src")

import unittest

from gwaslab_agent.g_print import _is_df_expr, _format_value_python, _format_args_python, ensure_string


class TestPrintUtils(unittest.TestCase):
    def test_is_df_expr(self):
        self.assertTrue(_is_df_expr("df_1.col"))
        self.assertFalse(_is_df_expr("df_x.col"))
        self.assertFalse(_is_df_expr("plain"))

    def test_format_value_python(self):
        self.assertEqual(_format_value_python("abc"), '"abc"')
        self.assertEqual(_format_value_python(True), "True")
        self.assertEqual(_format_value_python(None), "None")
        self.assertEqual(_format_value_python(1.23), "1.23")
        self.assertEqual(_format_value_python([1, "a", False]), '[1, "a", False]')

    def test_format_args_python(self):
        s = _format_args_python({"x": 1, "y": "a"})
        self.assertIn("x=1", s)
        self.assertIn('y="a"', s)

    def test_ensure_string_none(self):
        self.assertEqual(ensure_string(None), "")

    def test_ensure_string_bytes(self):
        self.assertEqual(ensure_string(b"abc"), "abc")

    def test_ensure_string_list(self):
        self.assertEqual(ensure_string(["a", {"text": "b"}, 123]), "ab123")

    def test_ensure_string_dict_text(self):
        self.assertEqual(ensure_string({"text": "hello"}), "hello")

    def test_ensure_string_dict_json(self):
        s = ensure_string({"a": 1})
        self.assertTrue(s.startswith("{"))
        self.assertIn('"a": 1', s)


if __name__ == "__main__":
    unittest.main()
