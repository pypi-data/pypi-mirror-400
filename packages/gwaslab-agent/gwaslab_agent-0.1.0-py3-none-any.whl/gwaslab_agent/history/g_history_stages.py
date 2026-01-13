"""
History and archive stage constants.

These constants define the stage/phase of execution for each history and archive entry,
allowing tracking of the conversation flow and execution stages.
"""

# User interaction stages
USER_INPUT = "user_input"  # Initial user input to main orchestrator
ORCHESTRATOR_REPLY = "orchestrator_reply"  # Orchestrator's reply to user
ORCHESTRATOR_TOOL_CALL = "orchestrator_tool_call"  # Orchestrator making tool calls

# Planner stages
PLANNER_INPUT = "planner_input"  # Input to planner
PLANNER_OUTPUT = "planner_output"  # Planner's plan output

# Loader stages
LOADER_INPUT = "loader_input"  # Input to loader
LOADER_OUTPUT = "loader_output"  # Loader's output

# Loader Summarizer stages
LOADER_SUMMARIZER_INPUT = "loader_summarizer_input"  # Input to loader summarizer
LOADER_SUMMARIZER_OUTPUT = "loader_summarizer_output"  # Loader summarizer's output

# Path Manager stages
PATH_MANAGER_INPUT = "path_manager_input"  # Input to path manager
PATH_MANAGER_OUTPUT = "path_manager_output"  # Path manager's output

# Summarizer stages
SUMMARIZER_INPUT = "summarizer_input"  # Input to summarizer
SUMMARIZER_OUTPUT = "summarizer_output"  # Summarizer's output

# Tool execution stages
TOOL_EXECUTION = "tool_execution"  # Tool execution result (from wrap_main_agent_method and wrap_loader_method)
MANUAL_LOAD = "manual_load"  # Manual sumstats loading

