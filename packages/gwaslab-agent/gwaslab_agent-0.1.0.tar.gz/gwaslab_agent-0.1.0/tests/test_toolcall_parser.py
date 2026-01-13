import unittest
import sys
import os

# Add src to path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from gwaslab_agent.g_toolcall_parser import _format_args_python

class TestToolCallParser(unittest.TestCase):
    def test_format_args_python_simple_slice(self):
        args = {"highlight": "df_1.snpid[:10]"}
        formatted = _format_args_python(args)
        self.assertEqual(formatted, "highlight=df_1.snpid[:10].to_list()")

    def test_format_args_python_extended_slice(self):
        args = {"lead_rs": "df_2.rsid[0:1]"}
        formatted = _format_args_python(args)
        self.assertEqual(formatted, "lead_rs=df_2.rsid[0:1].to_list()")

    def test_format_args_python_query_form(self):
        args = {"data": "df_0.query(CHR>1).snpid[:10]"}
        formatted = _format_args_python(args)
        self.assertEqual(formatted, "data=df_0.query(CHR>1).snpid[:10].to_list()")

    def test_format_args_python_scalar_method_chain(self):
        args = {"region_end": "df_3.POS.max()"}
        formatted = _format_args_python(args)
        self.assertEqual(formatted, "region_end=df_3.POS.max()")

    def test_format_args_python_bracketed_list(self):
        args = {"ids": "[df_4.rsid[:50]]"}
        formatted = _format_args_python(args)
        self.assertEqual(formatted, "ids=[df_4.rsid[:50]]")

    def test_format_args_python_list_iloc(self):
        args = {"highlight": '["df_0.SNPID.iloc[0]"]'}
        formatted = _format_args_python(args)
        self.assertEqual(formatted, "highlight=[df_0.SNPID.iloc[0]]")

    def test_format_args_python_scalar_iloc(self):
        args = {"lead_rs": "df_0.SNPID.iloc[0]"}
        formatted = _format_args_python(args)
        self.assertEqual(formatted, "lead_rs=df_0.SNPID.iloc[0]")

    def test_format_args_python_standard_string(self):
        args = {"title": "My Plot"}
        formatted = _format_args_python(args)
        self.assertEqual(formatted, 'title="My Plot"')

    def test_format_args_python_mixed_args(self):
        args = {
            "title": "GWAS",
            "highlight": "df_1.snpid[:10]",
            "threshold": 5e-8
        }
        formatted = _format_args_python(args)
        # Dictionary order is preserved in Python 3.7+
        expected_parts = [
            'title="GWAS"',
            "highlight=df_1.snpid[:10].to_list()",
            "threshold=5e-08"
        ]
        self.assertEqual(formatted, ", ".join(expected_parts))

if __name__ == "__main__":
    unittest.main()
