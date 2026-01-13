import unittest
import json
from gwaslab_agent.a_planner2 import Planner2
from gwaslab_agent.a_validator import Validator
from unittest.mock import MagicMock

class TestPlannerArchitecture(unittest.TestCase):
    def setUp(self):
        self.mock_log = MagicMock()
        self.mock_log.log_text = "Mock log"
        self.mock_tools = []
        
    def test_planner2_instantiation(self):
        # Test basic instantiation of Planner2 (mocking LLM to avoid API calls)
        mock_llm = MagicMock()
        planner = Planner2(self.mock_log, tools=self.mock_tools, llm=mock_llm)
        
        # Verify planner was created successfully
        self.assertIsNotNone(planner)
        self.assertEqual(planner.tools, self.mock_tools)
        
    def test_validator_structural_validation(self):
        validator = Validator()
        
        # 1. Valid plan
        valid_plan = {
            "plan": [
                {
                    "step_id": "1",
                    "action": "harmonize",
                    "inputs": {"sumstats": "input"},
                    "outputs": {"sumstats": "output"}
                }
            ]
        }
        result = validator.validate("req", json.dumps(valid_plan))
        self.assertEqual(result, "VALID")
        
        # 2. Invalid action
        invalid_action_plan = {
            "plan": [
                {
                    "step_id": "1",
                    "action": "non_existent_action",
                    "inputs": {},
                    "outputs": {}
                }
            ]
        }
        result = validator.validate("req", json.dumps(invalid_action_plan))
        self.assertIn("Unknown action", result)
        
        # 3. Missing inputs
        missing_input_plan = {
            "plan": [
                {
                    "step_id": "1",
                    "action": "harmonize",
                    # missing inputs
                    "outputs": {}
                }
            ]
        }
        result = validator.validate("req", json.dumps(missing_input_plan))
        self.assertIn("Missing 'inputs'", result)
        
        # 4. Markdown wrapping
        markdown_plan = """
        Here is the plan:
        ```json
        {
            "plan": [
                {
                    "step_id": "1",
                    "action": "plot_manhattan",
                    "inputs": {"sumstats": "in"},
                    "outputs": {"plot": "out"}
                }
            ]
        }
        ```
        """
        result = validator.validate("req", markdown_plan)
        self.assertEqual(result, "VALID")

if __name__ == '__main__':
    unittest.main()
