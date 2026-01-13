# ================================
# Standard Library
# ================================
import os
# ================================
# GWASLab
# ================================
import gwaslab as gl
from gwaslab.info.g_Log import Log
# ================================
# Third-Party Libraries
# ================================
from langchain.agents import create_agent

# ================================
# GWASLab-Agent Modules
# ================================
from gwaslab_agent.agents.a_loader import SmartLoader
from gwaslab_agent.agents.a_path_manager import PathManager
from gwaslab_agent.agents.a_planner import Planner
from gwaslab_agent.agents.a_summarizer import Summarizer
from gwaslab_agent.agents.a_validator import Validator
from gwaslab_agent.tools.g_build_tools import (
    RESULTS,
)
from gwaslab_agent.core.g_console import console
from gwaslab_agent.core.g_llm import get_llm, snapshot_counters, log_run_totals
from gwaslab_agent.core.g_sys_prompt import system_prompt
from gwaslab_agent.history.g_history_stages import (
    MANUAL_LOAD
)
from gwaslab_agent.tools.g_wrap_tools import wrap_main_agent_method
from gwaslab_agent.core.g_version import _show_version
from gwaslab_agent.history.g_toolcall_extractor import extract_all_toolcalls
from gwaslab_agent.core.g_middleware import MiddlewareManager
from gwaslab_agent.tools.g_toolcall_parser import _format_args_python
from gwaslab_agent.execution.s_script_execution import (
    execute_planner_script,
)
# New imports for refactored architecture
from gwaslab_agent.core.g_session_state import SessionState
from gwaslab_agent.core.g_agent_capabilities import AgentCapabilities
from gwaslab_agent.core.g_errors import LoadingError

# Workflow Overview
# path → Loader → Sumstats
# Sumstats → build tools → Agent init
# Planner → plan (Python script) → Validator → Execute script directly
# Tools layer → wrap_main_agent_method → structured JSON(data, log); images redacted; filtered Sumstats → subset_id via RESULTS
# Summarizer ← final message/log → methods text + reproducible script

"""
SmartSumstats Class - Method Descriptions
==========================================

This module contains the SmartSumstats class, which extends gwaslab.Sumstats with LLM-powered
agent capabilities. Below is a comprehensive description of all methods organized by section.

SECTION 1: Graph Visualization
--------------------------------
display_graph(output_format="mermaid", save_path=None)
    Display or save the LangGraph workflow visualization.
    - output_format: "mermaid", "ascii", or "png"
    - save_path: Optional path to save visualization
    - Returns: Visualization string or None

SECTION 2: Agent & Graph Setup (Internal)
------------------------------------------
_wrap_method(name, method)
    Wrap a method for LLM-safe, structured output serialization.
    Used internally by tool building system.

_build_graph()
    Build the LangGraph workflow for SmartSumstats.
    Returns the configured graph instance.

_init_agent()
    Initialize the internal LLM agent with tools and middleware.
    Returns the configured LangChain agent.

_reload_after_loading(verbose=True)
    Reload agent capabilities, tools, and agent after sumstats has been loaded.
    Called automatically after loading sumstats via chat().

_build_middleware_list()
    Build the list of middleware for the agent.
    Returns middleware configuration list.

set_middleware_options(todos=None, summarization=None, tool_retry=None, model_retry=None, 
                      summarization_trigger=None, summarization_keep=None)
    Configure middleware options for the agent.
    Rebuilds the agent after configuration changes.

_adjust_middleware_for_mode()
    Adjust middleware settings based on current execution mode.
    Rebuilds the agent after adjustment.

SECTION 3: History Management & Tool Calls
-------------------------------------------
all_toolcalls (property)
    Returns a comprehensive list of tool calls from all sub-agents.
    Excludes certain utility calls like "get_reference_file_path".

get_history_stats() -> dict
    Get statistics about current history including:
    - total_messages, archive_messages, estimated_tokens
    - max_tokens, max_messages
    - by_agent, by_stage, by_priority

SECTION 4: Public API Methods
------------------------------
clear(pl=True, w=True, pm=False, s=True, fs=True, dr=True)
    Clear various histories in the agent.
    - pl: Clear planner history
    - w: Clear worker (main agent) history
    - pm: Clear path manager history
    - s: Clear summarizer history
    - fs: Clear filtered Sumstats registry
    - dr: Clear data registry

chat(message, verbose=True, verbose_return=False, return_message=False, clear=False)
    Single entry point for all user interactions using LangGraph-based workflow.
    Routes queries to appropriate sub-agents:
    - Path queries → PathManager
    - Planning queries → Planner
    - Loading queries → SmartLoader
    - Summarization queries → Summarizer
    - General queries → Full workflow (Planner → Validator → Executor → Summarizer)
    Returns: Final message if return_message=True, otherwise None

SECTION 5: Utility Methods (Internal Helpers)
----------------------------------------------
_validate_sumstats_loaded(route, message, return_message, verbose)
    Validate that sumstats is loaded for routes that require it.
    Returns error message if validation fails, None otherwise.

_handle_path_manager_route(route_result, message, return_message, verbose)
    Handle path manager routing.
    Processes path-related queries and returns result message.

_handle_loader_route(message, return_message, verbose)
    Handle loader routing and sumstats loading.
    Manages sumstats loading via SmartLoader and updates internal state.

_update_sumstats_after_loading(loaded_sumstats, message, return_message, verbose)
    Update self.sumstats after successful loading.
    Reloads agent capabilities and tools with new sumstats data.

_handle_summarizer_route(route_result, message, verbose)
    Handle summarizer routing.
    Processes summarization queries and generates summaries.

_handle_planner_route(route_result, message, return_message, verbose)
    Handle planner routing.
    Processes planning queries and generates Python scripts.

_handle_graph_workflow(route, message, return_message, verbose)
    Handle graph-based workflow execution.
    Executes the full LangGraph workflow for complex queries.

_extract_result_from_state(final_state, verbose)
    Extract result message from graph final state.
    Returns formatted result message based on execution outcome.

_execute_planner_script(script, user_message)
    Execute the validated Python script generated by Planner.
    Wrapper for execute_planner_script from s_script_execution module.
"""

class SmartSumstats():
    """
    Extended version of gwaslab.Sumstats that:
      - Behaves exactly like the original Sumstats
      - Can build JSON Schemas for its methods using a parameter table
      - Embeds an internal LLM agent that can call its own methods via chat
    
    Class Organization:
    ------------------
    The class is organized into the following sections:
    
    1. __init__: Initialization and setup
       - LLM configuration
       - SessionState initialization
       - Data loading (SmartLoader or direct gl.Sumstats)
       - AgentCapabilities initialization
       - Agent and graph setup
    
    2. Graph Visualization: Methods for displaying workflow graphs
    
    3. Agent & Graph Setup: Internal methods for agent/graph initialization
    
    6. History Management: History tracking and tool call extraction
    
    7. Public API Methods: Main interaction methods (chat, run, plan_run, etc.)
    
    8. Utility Methods: Internal helper methods
    """

    def __init__(self, path: str = None, llm_configuration=None, provider=None, model=None, verbose=True, 
                 history=None, archive=None,
                 history_max_tokens: int = 50000,
                 history_min_messages: int = 3,
                 history_max_messages: int = 12,
                 archive_max_entries: int = 1000,
                 # Dependency injection factories (for testing)
                 session_state_factory=None,
                 agent_capabilities_factory=None,
                 planner_factory=None,
                 validator_factory=None,
                 loader_factory=None,
                 pathmanager_factory=None,
                 summarizer_factory=None,
                 **kwargs):
        """
        Initialize SmartSumstats with optional LLM provider/model selection.

        Args:
            path: Optional path to sumstats file or instruction string for SmartLoader.
                  If None, creates an empty SmartSumstats that can be loaded later via chat().
            llm_configuration: Optional dict or list[dict] LLM configuration (overrides LLM_KEY file)
            provider: Optional provider name to select from multiple profiles in LLM_KEY
            model: Optional model name to select from multiple profiles in LLM_KEY
            verbose: Whether to log messages
            history: Optional shared history list (for multi-sumstats scenarios)
            archive: Optional shared archive list (for multi-sumstats scenarios)
            history_max_tokens: Maximum estimated tokens to keep in history (default: 50000)
            history_min_messages: Minimum number of messages to always keep (default: 3)
            history_max_messages: Maximum number of messages to keep (default: 12)
            archive_max_entries: Maximum archive entries before compression (default: 1000)
            session_state_factory: Optional factory for SessionState (for testing)
            agent_capabilities_factory: Optional factory for AgentCapabilities (for testing)
            planner_factory: Optional factory for Planner (for testing)
            validator_factory: Optional factory for Validator (for testing)
            loader_factory: Optional factory for SmartLoader (for testing)
            pathmanager_factory: Optional factory for PathManager (for testing)
            summarizer_factory: Optional factory for Summarizer (for testing)
            **kwargs: Additional arguments passed to gl.Sumstats when path exists
        """
        self.log = Log()
        """
        Logger instance for tracking and recording events throughout the agent's operation.
        """

        self.log.write("Initiating GWASLab Agent...", verbose=verbose, tag="agent")
        _show_version(self.log, verbose=verbose)

        self.llm = get_llm(self.log, llm_configuration=llm_configuration, provider=provider, model=model, verbose=verbose)
        """
        Large Language Model instance used for powering the agent's conversational capabilities.
        """
        
        # Initialize SessionState (centralized state management)
        if session_state_factory:
            self.session_state = session_state_factory(
                history_max_tokens=history_max_tokens,
                history_min_messages=history_min_messages,
                history_max_messages=history_max_messages,
                archive_max_entries=archive_max_entries,
                llm=self.llm,
                enable_summarization=True
            )
        else:
            self.session_state = SessionState(
                history_max_tokens=history_max_tokens,
                history_min_messages=history_min_messages,
                history_max_messages=history_max_messages,
                archive_max_entries=archive_max_entries,
                llm=self.llm,
                enable_summarization=True
            )
        
        # If shared history/archive provided, use them (for multi-sumstats scenarios)
        if history is not None and archive is not None:
            self.session_state.history = history
            self.session_state.archive = archive
            # Update HistoryManager to use shared lists
            self.session_state.history_manager.history = history
            self.session_state.history_manager.archive = archive
        
        # Expose history and archive as properties
        self.history = self.session_state.history
        self.archive = self.session_state.archive
        """
        List to store records of tool calls made by the agent for auditing and debugging purposes.
        Managed by SessionState/HistoryManager for intelligent pruning and compression.
        """

        # Store loader factory for later use
        self._loader_factory = loader_factory

        # Load sumstats data
        if path is None:
            # No path provided - create empty sumstats that can be loaded later
            import pandas as pd
            empty_data = pd.DataFrame()
            self.sumstats = gl.Sumstats(empty_data, verbose=False)
            self.sumstats.log.combine(self.log)
            self.log = self.sumstats.log
            self._sumstats_loaded = False
        elif not os.path.exists(path):
            # Use SmartLoader for non-file paths
            try:
                loader = (loader_factory or SmartLoader)(
                    llm=self.llm,
                    history=self.history,
                    archive=self.archive,
                    verbose=verbose
                )
                loaded_sumstats = loader.run(path)
                # Use the loaded_sumstats from return value - it has the actual loading log from __preformat
                # This is the sumstats object created during loading with all the loading messages
                if loaded_sumstats is not None:
                    self.sumstats = loaded_sumstats
                else:
                    # Fallback to loader.sumstats if return value is None
                    self.sumstats = loader.sumstats
                if not self.sumstats or (hasattr(self.sumstats, 'data') and self.sumstats.data is None):
                    raise LoadingError(f"Failed to load sumstats from: {path}", path=path)
                # Combine logs: add SmartSumstats initial log to sumstats.log (which contains the loading log)
                # The sumstats.log already has the full loading log from __preformat
                # Then make self.log point to the combined log so planner can access it
                self.sumstats.log.combine(self.log)
                self.log = self.sumstats.log
                # Add loader messages to history
                for msg in loader.history:
                    self.session_state.history_manager.add_message(msg)
                self._sumstats_loaded = True
            except Exception as e:
                raise LoadingError(f"Error loading sumstats: {str(e)}", path=path) from e
        else:
            # Direct file path - load with gl.Sumstats
            try:
                self.sumstats = gl.Sumstats(path, verbose=verbose, **kwargs)
                # Combine logs: add SmartSumstats initial log to sumstats.log (which contains the loading log)
                # Then make self.log point to the combined log so planner can access it
                self.sumstats.log.combine(self.log)
                self.log = self.sumstats.log
                _fmt = _format_args_python(kwargs)
                call_str = f'sumstats = gl.Sumstats("{path}", {_fmt})' if _fmt else f'sumstats = gl.Sumstats("{path}")'
                msg = {"role": "assistant", "gwaslab_agent": "Worker_orchestrator", "toolcalls": call_str, "content": f"Manually loaded Sumstats from: {path}", "stage": MANUAL_LOAD}
                self.session_state.history_manager.add_message(msg)
                self._sumstats_loaded = True
            except Exception as e:
                raise LoadingError(f"Error loading sumstats file: {str(e)}", path=path) from e

        self.config = gl.options
        
        # Token count now managed by SessionState
        self.token_count = self.session_state.token_tracker

        self.RESULTS = self.session_state.results

        # full args schema for tools (will be populated by AgentCapabilities)
        self.full_schema = {}
        self.tool_docs = {}

        self.log.write("Initiating GWASLab Agent Worker_orchestrator...", verbose=verbose, tag="agent")
        
        # Initialize AgentCapabilities (separated agent logic)
        # Note: Pass self (SmartSumstats wrapper) for tool building and agent access
        # Note: Don't pass **kwargs to AgentCapabilities - they're only for gl.Sumstats()
        # Agent factories are passed explicitly, not via kwargs
        if agent_capabilities_factory:
            self.agent_capabilities = agent_capabilities_factory(
                sumstats_wrapper=self,  # Pass self for tool building
                session_state=self.session_state,
                llm=self.llm,
                verbose=verbose,
                planner_factory=planner_factory,
                validator_factory=validator_factory,
                loader_factory=loader_factory,
                pathmanager_factory=pathmanager_factory,
                summarizer_factory=summarizer_factory
            )
        else:
            self.agent_capabilities = AgentCapabilities(
                sumstats_wrapper=self,  # Pass self for tool building
                session_state=self.session_state,
                llm=self.llm,
                verbose=verbose,
                planner_factory=planner_factory,
                validator_factory=validator_factory,
                loader_factory=loader_factory,
                pathmanager_factory=pathmanager_factory,
                summarizer_factory=summarizer_factory
            )
        
        # Expose sub-agents
        self.planner = self.agent_capabilities.planner
        self.validator = self.agent_capabilities.validator
        self.pathmanager = self.agent_capabilities.pathmanager
        self.summarizer = self.agent_capabilities.summarizer
        self.tools = self.agent_capabilities.tools
        self.full_schema = self.agent_capabilities.full_schema
        self.tool_docs = self.agent_capabilities.tool_docs

        self.middleware_manager = MiddlewareManager(self.llm)
        self.middleware_manager.set_options(summarization_trigger=("tokens", 120000))

        self._current_mode = None
        
        self.agent = self._init_agent()
        """
        The internal LLM agent responsible for processing user queries and executing tools.
        """

        self.log.write("Finished loading...", verbose=verbose, tag="agent")
        
        self.graph = self._build_graph()
    
    # ============================================================================
    # SECTION 1: Graph Visualization
    # ============================================================================
    
    def display_graph(self, output_format="mermaid", save_path=None):
        """
        Display or save the LangGraph workflow visualization.
        
        Parameters
        ----------
        output_format : str, default "mermaid"
            Format for visualization. Options:
            - "mermaid": Mermaid diagram (can be rendered in markdown)
            - "ascii": ASCII art representation
            - "png": PNG image (requires pygraphviz)
        save_path : str, optional
            If provided, save the visualization to this path. Otherwise, print to console.
        
        Returns
        -------
        str or None
            The visualization string if output_format is "mermaid" or "ascii", None otherwise.
        """
        from gwaslab_agent.graph.display_graph import display_graph as _display_graph
        return _display_graph(self.graph, self.log, output_format=output_format, save_path=save_path)

    def _wrap_method(self, name, method):
        """Wrap a method for LLM-safe, structured output serialization."""
        return wrap_main_agent_method(self, name, method)

    # ============================================================================
    # SECTION 4: Agent & Graph Setup
    # ============================================================================
    
    def _build_graph(self):
        from gwaslab_agent.graph.g_graph import build_sumstats_graph
        return build_sumstats_graph(self)
    
    def _init_agent(self):
        return  create_agent(       model=self.llm,
                                    tools=self.tools,
                                    middleware=self._build_middleware_list(),
                                    system_prompt=system_prompt
                                )
    
    def _reload_after_loading(self, verbose=True):
        """
        Reload agent capabilities, tools, and agent after sumstats has been loaded.
        This is called after loading sumstats via chat() to rebuild tools and agent.
        """
        # Suppress reload messages when loading via chat
        # self.log.write("Reloading agent capabilities after loading sumstats...", verbose=verbose)
        
        # Rebuild agent capabilities with the new sumstats
        self.agent_capabilities = AgentCapabilities(
            sumstats_wrapper=self,
            session_state=self.session_state,
            llm=self.llm,
            verbose=verbose,
            planner_factory=None,  # Use defaults
            validator_factory=None,
            loader_factory=self._loader_factory,
            pathmanager_factory=None,
            summarizer_factory=None
        )
        
        # Update exposed sub-agents
        self.planner = self.agent_capabilities.planner
        self.validator = self.agent_capabilities.validator
        self.pathmanager = self.agent_capabilities.pathmanager
        self.summarizer = self.agent_capabilities.summarizer
        self.tools = self.agent_capabilities.tools
        self.full_schema = self.agent_capabilities.full_schema
        self.tool_docs = self.agent_capabilities.tool_docs
        
        # Rebuild graph and agent
        self.graph = self._build_graph()
        self.agent = self._init_agent()
        
        # Suppress reload messages when loading via chat
        # self.log.write("Agent capabilities reloaded successfully", verbose=verbose)
    
    def _build_middleware_list(self):
        return self.middleware_manager.build()
    
    def set_middleware_options(self, todos=None, summarization=None, tool_retry=None, model_retry=None, summarization_trigger=None, summarization_keep=None):
        self.middleware_manager.set_options(
            todos=todos,
            summarization=summarization,
            tool_retry=tool_retry,
            model_retry=model_retry,
            summarization_trigger=summarization_trigger,
            summarization_keep=summarization_keep,
        )
        self.agent = self._init_agent()
    
    def _adjust_middleware_for_mode(self):
        m = getattr(self, "_current_mode", None)
        steps = getattr(self, "_last_plan_steps", 0)
        self.middleware_manager.adjust_for_mode(m, last_plan_steps=steps)

        self.agent = self._init_agent()

    # ============================================================================
    # SECTION 5: History Management & Tool Calls
    # ============================================================================
    
    @property
    def all_toolcalls(self):
        excluded = {"get_reference_file_path"}
        return extract_all_toolcalls(self.archive, exclude=excluded)
    
    def get_history_stats(self) -> dict:
        """
        Get statistics about current history.
        
        Returns
        -------
        dict
            Dictionary containing history statistics including:
            - total_messages: Number of messages in history
            - archive_messages: Number of messages in archive
            - estimated_tokens: Estimated token count
            - max_tokens: Maximum token limit
            - max_messages: Maximum message limit
            - by_agent: Count of messages by agent type
            - by_stage: Count of messages by stage
            - by_priority: Count of messages by priority (high/medium/low)
        """
        return self.session_state.history_manager.get_history_stats()

    # ============================================================================
    # SECTION 6: Public API Methods (Main Interaction Methods)
    # ============================================================================

    def clear(self, pl=True, w=True, pm=False, s=True, fs=True, dr=True):
        """
        Clear various histories in the agent.

        Parameters
        ----------
        pl : bool, default True
            Whether to clear the planner history.
        w : bool, default True
            Whether to clear the worker (main agent) history.
        pm : bool, default False
            Whether to clear the path manager history.
        s : bool, default True
            Whether to clear the summarizer history.
        fs : bool, default True
            Whether to clear filtered Sumstats registry.
        dr : bool, default True
            Whether to clear data registry.
        """
        if pl and hasattr(self, "planner"):
            self.session_state.history_manager.clear_history(agent_types=["Planner"])
        if w:
            self.session_state.history_manager.clear_history(agent_types=["Worker", "Worker_orchestrator"])
        if s and hasattr(self, "summarizer"):
            self.session_state.history_manager.clear_history(agent_types=["Summarizer"])
        if fs and hasattr(self, "RESULTS") and hasattr(self.RESULTS, "objects"):
            self.RESULTS.objects.clear()
        if dr and hasattr(self, "RESULTS") and hasattr(self.RESULTS, "objects"):
            self.RESULTS.objects.clear()
    
    def chat(self, message: str, verbose=True, verbose_return=False, return_message=False, clear: bool=False, yes: bool=False):
        """
        Single entry point for all user interactions using LangGraph-based workflow.

        This method uses a LangGraph workflow that:
        1. Interprets the user message using QueryRouter
        2. Extracts script instructions for Planner
        3. Extracts summary instructions for Summarizer (if needed)
        4. Routes through the appropriate workflow:
           - Path-related queries → PathManager
           - Planning queries → Planner (script generation only)
           - Loading queries → SmartLoader
           - Summarization queries → Summarizer
           - General queries → Planner → Validator → Executor → Summarizer (if needed)

        Parameters
        ----------
        message : str
            The input message or query for the agent to process.
        verbose : bool, default True
            Whether to print verbose output.
        verbose_return : bool, default False
            Whether to return verbose messages.
        return_message : bool, default False
            Whether to return the final message.
        clear : bool, default False
            Whether to clear history before processing.
        yes : bool, default False
            If True, skip user confirmation for planner and proceed automatically.

        Returns
        -------
        str or None
            The final message from the agent if return_message is True, otherwise None.
        """
        from gwaslab_agent.agents.a_router import QueryRouter
        
        _start = snapshot_counters(self.token_count)

        # Clear history if requested
        if clear:
            self.clear(pl=True, w=True, pm=False, s=True)

        # Route the message
        router = QueryRouter(self)
        route_result = router.route(message, verbose=verbose)
        route = route_result.get('route', 'plan_run')
        
        # Validate sumstats is loaded (for non-loading routes)
        validation_result = self._validate_sumstats_loaded(route, message, return_message, verbose)
        if validation_result is not None:
            return validation_result
        
        # Handle route-specific logic
        result = None
        if route == 'path_manager' and 'handler' in route_result:
            result = self._handle_path_manager_route(route_result, message, return_message, verbose)
        elif route == 'loader':
            # Loader route: handle directly regardless of handler presence
            # We can always get loader from agent_capabilities
            result = self._handle_loader_route(message, return_message, verbose)
        elif route == 'summarizer' and 'handler' in route_result:
            result = self._handle_summarizer_route(route_result, message, verbose)
        elif route == 'planner' and 'handler' in route_result:
            result = self._handle_planner_route(route_result, message, return_message, verbose, yes=yes)
        else:
            result = self._handle_graph_workflow(route, message, return_message, verbose, yes=yes)

        # Log token usage and return result
        _end = snapshot_counters(self.token_count)
        log_run_totals(self.log, "chat", _start, _end, verbose=verbose)
        
        return result if return_message else None


    # ============================================================================
    # SECTION 7: Utility Methods (Internal Helpers)
    # ============================================================================
    
    def _validate_sumstats_loaded(self, route: str, message: str, return_message: bool, verbose: bool):
        """
        Validate that sumstats is loaded for routes that require it.
        
        Parameters
        ----------
        route : str
            The route determined by QueryRouter
        message : str
            The user message
        return_message : bool
            Whether to return a message
        verbose : bool
            Verbose flag
            
        Returns
        -------
        str or None
            Error message if validation fails, None otherwise
        """
        # Skip validation for routes that don't need sumstats
        if route in ('loader', 'path_manager'):
            return None
        
        # Check if sumstats is actually loaded (has data)
        # Use object.__getattribute__ to avoid triggering __getattr__ recursion
        try:
            sumstats = object.__getattribute__(self, 'sumstats')
            if sumstats is None:
                sumstats_has_data = False
            else:
                try:
                    data = object.__getattribute__(sumstats, 'data')
                    # Check if data is a DataFrame by checking its type name
                    # This avoids triggering __getattr__ on Sumstats objects
                    if data is None:
                        sumstats_has_data = False
                    else:
                        # Check if it's a DataFrame by type name (avoids import and __getattr__)
                        data_type_name = type(data).__name__
                        if data_type_name == 'DataFrame':
                            # Safe to access .empty on DataFrame
                            try:
                                empty_attr = object.__getattribute__(data, 'empty')
                                sumstats_has_data = not empty_attr
                            except AttributeError:
                                sumstats_has_data = False
                        else:
                            # Not a DataFrame, so it doesn't have .empty
                            sumstats_has_data = False
                except AttributeError:
                    sumstats_has_data = False
        except AttributeError:
            sumstats_has_data = False
        
        if not sumstats_has_data:
            # Try to detect if this is actually a loading request
            message_lower = message.lower()
            load_keywords = ['load', 'download', 'fetch', 'get data', 'import', 'read file', 'open file']
            if not any(keyword in message_lower for keyword in load_keywords):
                # Not a loading request and sumstats is not loaded
                if return_message:
                    return "No sumstats loaded yet. Please load sumstats first using: sumstats.chat('load <path>')"
                else:
                    self.log.write("Warning: No sumstats loaded. User should load sumstats first.", verbose=verbose, tag="agent")
                    return None
        
        return None
    
    def _handle_path_manager_route(self, route_result: dict, message: str, return_message: bool, verbose: bool):
        """
        Handle path manager routing.
        
        Parameters
        ----------
        route_result : dict
            Result from QueryRouter
        message : str
            User message
        return_message : bool
            Whether to return a message
        verbose : bool
            Verbose flag
            
        Returns
        -------
        str or None
            Result message
        """
        self.log.write("Routing to PathManager", verbose=verbose, tag="agent")
        handler_result = route_result['handler'](message, verbose=verbose, return_message=return_message)
        
        if return_message:
            if isinstance(handler_result, dict):
                return handler_result.get('message', 'Path query processed')
            return str(handler_result)
        return "Path query processed."
    
    def _handle_loader_route(self, message: str, return_message: bool, verbose: bool):
        """
        Handle loader routing and sumstats loading.
        
        Parameters
        ----------
        message : str
            User message
        return_message : bool
            Whether to return a message
        verbose : bool
            Verbose flag
            
        Returns
        -------
        str or None
            Result message
        """
        self.log.write("Routing to SmartLoader", verbose=verbose, tag="agent")
        
        # Get or create loader
        loader = self.agent_capabilities.get_or_create_loader()
        
        # Run the loader
        loaded_sumstats = loader.run(message, verbose=verbose)
        
        # Check if we successfully loaded sumstats
        # Use object.__getattribute__ to avoid triggering __getattr__ recursion
        if loaded_sumstats is not None:
            try:
                data = object.__getattribute__(loaded_sumstats, 'data')
                if data is not None:
                    # Check if it's a DataFrame by type name
                    data_type_name = type(data).__name__
                    if data_type_name == 'DataFrame':
                        try:
                            empty_attr = object.__getattribute__(data, 'empty')
                            if not empty_attr:
                                return self._update_sumstats_after_loading(loaded_sumstats, message, return_message, verbose)
                        except AttributeError:
                            pass
            except AttributeError:
                pass
        
        # Check if loader's sumstats was updated
        if hasattr(loader, 'sumstats') and loader.sumstats is not None:
            try:
                data = object.__getattribute__(loader.sumstats, 'data')
                if data is not None:
                    # Check if it's a DataFrame by type name
                    data_type_name = type(data).__name__
                    if data_type_name == 'DataFrame':
                        try:
                            empty_attr = object.__getattribute__(data, 'empty')
                            if not empty_attr:
                                return self._update_sumstats_after_loading(loader.sumstats, message, return_message, verbose)
                        except AttributeError:
                            pass
            except AttributeError:
                pass
        
        # Loading failed
        if return_message:
            if hasattr(loader, 'sumstats') and loader.sumstats is not None:
                return "Loading attempted but no data was loaded."
            return "Loading attempted but no sumstats was created."
        return "Loading query processed."
    
    def _update_sumstats_after_loading(self, loaded_sumstats, message: str, return_message: bool, verbose: bool):
        """
        Update self.sumstats after successful loading.
        
        Parameters
        ----------
        loaded_sumstats
            The loaded sumstats object
        message : str
            Original user message
        return_message : bool
            Whether to return a message
        verbose : bool
            Verbose flag
            
        Returns
        -------
        str
            Result message
        """
        # Update self.sumstats with loaded data
        self.sumstats = loaded_sumstats
        self.sumstats.log.combine(self.log)
        self.log = self.sumstats.log
        self._sumstats_loaded = True
        
        # Reload agent capabilities, tools, and agent after loading
        self._reload_after_loading(verbose=verbose)
        
        if return_message:
            return f"Successfully loaded sumstats from: {message}"
        return "Loading query processed."
    
    def _handle_summarizer_route(self, route_result: dict, message: str, verbose: bool):
        """
        Handle summarizer routing.
        
        Parameters
        ----------
        route_result : dict
            Result from QueryRouter
        message : str
            User message
        verbose : bool
            Verbose flag
            
        Returns
        -------
        str
            Result message
        """
        self.log.write("Routing to Summarizer", verbose=verbose, tag="agent")
        route_result['handler'](message, verbose=verbose)
        return "Summary generated."
    
    def _handle_planner_route(self, route_result: dict, message: str, return_message: bool, verbose: bool, yes: bool=False):
        """
        Handle planner routing.
        
        Parameters
        ----------
        route_result : dict
            Result from QueryRouter
        message : str
            User message
        return_message : bool
            Whether to return a message
        verbose : bool
            Verbose flag
        yes : bool, default False
            If True, skip user confirmation for planner
            
        Returns
        -------
        str or None
            Result message
        """
        self.log.write("Routing to Planner", verbose=verbose, tag="agent")
        
        # Prepare data for planner
        head = ""
        meta = {}
        try:
            sumstats = object.__getattribute__(self, 'sumstats')
            if sumstats is not None:
                try:
                    data = object.__getattribute__(sumstats, 'data')
                    if data is not None and hasattr(data, 'head'):
                        head = data.head().to_markdown()
                except AttributeError:
                    pass
                try:
                    meta_obj = object.__getattribute__(sumstats, 'meta')
                    if meta_obj is not None:
                        meta = meta_obj.get("gwaslab", {})
                except AttributeError:
                    pass
        except AttributeError:
            pass
        
        script = route_result['handler'](
            message,
            head=head,
            meta=meta,
            return_message=True,
            yes=yes
        )
        
        if return_message:
            return f"Generated script:\n{script}" if script else "Script generation completed."
        return None
    
    def _handle_graph_workflow(self, route: str, message: str, return_message: bool, verbose: bool, yes: bool=False):
        """
        Handle graph-based workflow execution.
        
        Parameters
        ----------
        route : str
            The route determined by QueryRouter
        message : str
            User message
        return_message : bool
            Whether to return a message
        verbose : bool
            Verbose flag
        yes : bool, default False
            If True, skip user confirmation for planner
            
        Returns
        -------
        str or None
            Result message
        """
        # Determine if summary is needed
        needs_summary = route not in ("plan", "planner", "path_manager", "loader", "summarizer")
        
        # Initialize graph state
        initial_state = {
            "message": message,
            "original_message": message,
            "route": route,
            "mode": "plan_run",
            "script_instructions": None,
            "summary_instructions": None,
            "needs_summary": needs_summary,
            "script": None,
            "resolved_script": None,
            "validated_script": None,
            "exec_message": None,
            "step_index": 0,
            "yes": yes
        }
        
        # Run the graph
        try:
            self.log.write("Invoking graph workflow...", verbose=verbose, tag="agent")
            final_state = self.graph.invoke(initial_state)
            # Suppress redundant completion message
            # self.log.write("Graph workflow completed", verbose=verbose)
            
            # Extract result from final state
            if return_message:
                return self._extract_result_from_state(final_state, verbose)
            return None
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            self.log.write(f"Error in graph execution: {str(e)}", verbose=verbose, tag="agent")
            self.log.write(f"Traceback: {error_trace}", verbose=verbose, tag="agent")
            if return_message:
                return f"Error: {str(e)}"
            return None
    
    def _extract_result_from_state(self, final_state: dict, verbose: bool):
        """
        Extract result message from graph final state.
        
        Parameters
        ----------
        final_state : dict
            Final state from graph execution
        verbose : bool
            Verbose flag
            
        Returns
        -------
        str
            Result message
        """
        exec_message = final_state.get("exec_message")
        script = final_state.get("script")
        validated_script = final_state.get("validated_script")
        
        self.log.write(
            f"Final state - exec_message: {exec_message is not None}, "
            f"script: {script is not None}, "
            f"validated_script: {validated_script is not None}",
            verbose=verbose,
            tag="agent"
        )
        
        if exec_message:
            return exec_message
        elif validated_script:
            return f"Generated and validated script:\n{validated_script}"
        elif script:
            return f"Generated script:\n{script}"
        else:
            return "Workflow completed."
    
    
    def _execute_planner_script(self, script: str, user_message: str):
        """Wrapper for execute_planner_script from s_script_execution module."""
        execute_planner_script(
            script=script,
            user_message=user_message,
            sumstats=self.sumstats,
            results=self.RESULTS,
            log=self.log,
            history=self.history,
            archive=self.archive
        )
