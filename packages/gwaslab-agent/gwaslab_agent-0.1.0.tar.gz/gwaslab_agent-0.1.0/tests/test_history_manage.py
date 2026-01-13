import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)
sys.path.insert(0, "/home/yunye/work/gwaslab/src")

from gwaslab_agent.g_history_manage import extract_toolcalls, extract_all_toolcalls


class TestHistoryManage(unittest.TestCase):
    def test_extract_toolcalls_dict_format(self):
        archive = [
            {"role": "assistant", "gwaslab_agent": "Plotter", "toolcalls": {"name": "plot_mqq", "args": {"sig_level": 5}}},
            {"role": "assistant", "gwaslab_agent": "Planner", "toolcalls": {"name": "infer_build", "args": {}}},
        ]
        calls_plotter = extract_toolcalls(archive, role="Plotter")
        calls_planner = extract_toolcalls(archive, role="Planner")
        self.assertEqual(calls_plotter, ["sumstats.plot_mqq(sig_level=5)"])
        self.assertEqual(calls_planner, [f"gl.infer_build()"])

    def test_extract_toolcalls_string_preserve_assignment(self):
        archive = [
            {"role": "assistant", "gwaslab_agent": "Worker_orchestrator", "toolcalls": "df_0 = sumstats.filter_in({'p': 5e-8})"},
            {"role": "assistant", "gwaslab_agent": "Worker_orchestrator", "toolcalls": "sumstats.summary()"},
        ]
        calls = extract_toolcalls(archive, role="Worker_orchestrator")
        self.assertEqual(calls[0], "df_0 = sumstats.filter_in({'p': 5e-8})")
        self.assertEqual(calls[1], "sumstats.summary()")

    def test_extract_all_toolcalls_exclude(self):
        archive = [
            {"role": "assistant", "gwaslab_agent": "Plotter", "toolcalls": {"name": "plot_mqq", "args": {"sig_level": 5}}},
            {"role": "assistant", "gwaslab_agent": "Worker_orchestrator", "toolcalls": "sumstats.filter_in({'p': 5e-8})"},
            {"role": "assistant", "gwaslab_agent": "Planner", "toolcalls": {"name": "infer_build", "args": {}}},
        ]
        calls = extract_all_toolcalls(archive, exclude=["plot_mqq", "filter_in"])
        self.assertEqual(calls, ["gl.infer_build()"])


if __name__ == "__main__":
    unittest.main()
