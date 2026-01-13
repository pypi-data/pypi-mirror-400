"""
Agent Capabilities - Separated Agent Logic

This module separates agent orchestration logic from the SmartSumstats wrapper,
improving testability and maintainability.
"""

from typing import Optional, Dict, Any, Callable
from gwaslab.info.g_Log import Log
from gwaslab_agent.core.g_session_state import SessionState
from gwaslab_agent.core.g_base_agent import BaseAgent
from gwaslab_agent.core.g_errors import AgentError, ConfigurationError


class AgentCapabilities:
    """
    Handles all agent-related functionality for SmartSumstats.
    
    This class separates agent orchestration from the Sumstats wrapper,
    making it easier to test and maintain.
    """
    
    def __init__(
        self,
        sumstats_wrapper,  # Changed: now expects SmartSumstats wrapper, not just sumstats
        session_state: SessionState,
        llm=None,
        verbose: bool = True,
        # Dependency injection factories
        planner_factory: Optional[Callable] = None,
        validator_factory: Optional[Callable] = None,
        loader_factory: Optional[Callable] = None,
        pathmanager_factory: Optional[Callable] = None,
        summarizer_factory: Optional[Callable] = None
    ):
        """
        Initialize agent capabilities.
        
        Parameters
        ----------
        sumstats_wrapper : SmartSumstats
            The SmartSumstats wrapper object (needed for tool building)
        session_state : SessionState
            Centralized session state
        llm : optional
            LLM instance
        verbose : bool
            Verbose flag
        planner_factory : callable, optional
            Factory function to create Planner instance
        validator_factory : callable, optional
            Factory function to create Validator instance
        loader_factory : callable, optional
            Factory function to create SmartLoader instance
        pathmanager_factory : callable, optional
            Factory function to create PathManager instance
        summarizer_factory : callable, optional
            Factory function to create Summarizer instance
        
        Note
        ----
        **kwargs from SmartSumstats.__init__() are NOT passed here.
        They are only used for gl.Sumstats() initialization, not for sub-agents.
        """
        self.sumstats_wrapper = sumstats_wrapper
        self.sumstats = sumstats_wrapper.sumstats  # Access underlying sumstats
        self.session_state = session_state
        self.llm = llm
        self.verbose = verbose
        self.log = sumstats_wrapper.log if hasattr(sumstats_wrapper, 'log') else Log()
        
        # Store factories for lazy initialization if needed
        self._planner_factory = planner_factory
        self._validator_factory = validator_factory
        self._loader_factory = loader_factory
        self._pathmanager_factory = pathmanager_factory
        self._summarizer_factory = summarizer_factory
        # Note: kwargs are not stored - they're only for gl.Sumstats(), not for sub-agents
        # Sub-agents receive their parameters explicitly
        
        # Initialize sub-agents using factories (dependency injection)
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all sub-agents using dependency injection."""
        # Import here to avoid circular imports
        from gwaslab_agent.agents.a_planner import Planner
        from gwaslab_agent.agents.a_validator import Validator
        from gwaslab_agent.agents.a_loader import SmartLoader
        from gwaslab_agent.agents.a_path_manager import PathManager
        from gwaslab_agent.agents.a_summarizer import Summarizer
        from gwaslab_agent.tools.g_build_tools import _build_tools_from_methods
        
        # Build tools first (needed for planner)
        # Pass wrapper for tool building
        self.tools = _build_tools_from_methods(self.sumstats_wrapper, verbose=self.verbose)
        self.full_schema = getattr(self.sumstats_wrapper, 'full_schema', {})
        self.tool_docs = getattr(self.sumstats_wrapper, 'tool_docs', {})
        
        # Filter tools for planner
        _planner_tools = []
        _names = set()
        for t in self.tools:
            n = getattr(t, "name", None)
            if not isinstance(n, str):
                continue
            if n in {"run_on_results"}:
                continue
            if n in _names:
                continue
            _planner_tools.append(t)
            _names.add(n)
        
        # Initialize Planner
        planner_class = self._planner_factory or Planner
        self.planner = planner_class(
            log_object=self.log,
            tools=_planner_tools,
            llm=self.llm,
            history=self.session_state.history,
            archive=self.session_state.archive,
            verbose=False,
            sumstats=self.sumstats,
            full_schema=self.full_schema,
            tool_docs=self.tool_docs
            # Note: No **kwargs - Planner doesn't accept gl.Sumstats kwargs
        )
        # Share token tracker with planner (BaseAgent initializes token_count as dict, 
        # but we can assign TokenTracker object which has compatible interface)
        self.planner.token_count = self.session_state.token_tracker
        
        # Initialize Validator
        validator_class = self._validator_factory or Validator
        self.validator = validator_class(
            llm=self.llm,
            pathmanager=None,  # Will be set after PathManager is created
            full_schema=self.full_schema,
            log=self.log,
            history=self.session_state.history,
            archive=self.session_state.archive,
            verbose=False
        )
        # Share token tracker
        self.validator.token_count = self.session_state.token_tracker
        
        # Initialize PathManager
        pathmanager_class = self._pathmanager_factory or PathManager
        self.pathmanager = pathmanager_class(
            log_object=self.log,
            llm=self.llm,
            history=self.session_state.history,
            archive=self.session_state.archive,
            verbose=False
        )
        # Share token tracker
        self.pathmanager.token_count = self.session_state.token_tracker
        
        # Update validator with pathmanager
        self.validator.pathmanager = self.pathmanager
        
        # Initialize Summarizer
        summarizer_class = self._summarizer_factory or Summarizer
        self.summarizer = summarizer_class(
            log_object=self.log,
            llm=self.llm,
            history=self.session_state.history,
            archive=self.session_state.archive,
            verbose=False
        )
        # Share token tracker
        self.summarizer.token_count = self.session_state.token_tracker
        
        # SmartLoader is created on-demand when needed
        self._loader_class = self._loader_factory or SmartLoader
        self.loader = None
    
    def get_or_create_loader(self):
        """Get existing loader or create a new one."""
        if self.loader is None:
            self.loader = self._loader_class(
                llm=self.llm,
                history=self.session_state.history,
                archive=self.session_state.archive,
                verbose=self.verbose
            )
            self.loader.token_count = self.session_state.token_tracker
        return self.loader
    
    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """
        Get a sub-agent by type.
        
        Parameters
        ----------
        agent_type : str
            Type of agent ('planner', 'validator', 'loader', 'pathmanager', 'summarizer')
            
        Returns
        -------
        BaseAgent or None
            The requested agent, or None if not found
        """
        agent_map = {
            'planner': self.planner,
            'validator': self.validator,
            'loader': self.get_or_create_loader(),
            'pathmanager': self.pathmanager,
            'summarizer': self.summarizer
        }
        return agent_map.get(agent_type.lower())
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """Get all sub-agents as a dictionary."""
        return {
            'planner': self.planner,
            'validator': self.validator,
            'pathmanager': self.pathmanager,
            'summarizer': self.summarizer,
            'loader': self.get_or_create_loader()
        }
    
    def validate_configuration(self):
        """
        Validate that all required components are properly configured.
        
        Raises
        ------
        ConfigurationError
            If configuration is invalid
        """
        if self.llm is None:
            raise ConfigurationError(
                "LLM is not configured",
                config_key="llm"
            )
        
        if self.sumstats is None:
            raise ConfigurationError(
                "Sumstats object is not set",
                config_key="sumstats"
            )
        
        if self.session_state is None:
            raise ConfigurationError(
                "Session state is not set",
                config_key="session_state"
            )
    
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Get a summary of agent capabilities."""
        return {
            "agents": {
                name: {
                    "type": type(agent).__name__,
                    "initialized": agent is not None,
                    "has_llm": hasattr(agent, 'llm') and agent.llm is not None
                }
                for name, agent in self.get_all_agents().items()
            },
            "tools_count": len(self.tools),
            "full_schema_count": len(self.full_schema),
            "session_state": self.session_state.get_state_summary()
        }

