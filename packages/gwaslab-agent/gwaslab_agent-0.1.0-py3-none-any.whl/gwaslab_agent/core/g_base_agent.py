"""
Base Agent Interface for GWASLab Agent System

This module defines the base interface that all sub-agents (Planner, Loader, Validator, etc.)
should implement for consistency and easier testing.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from gwaslab.info.g_Log import Log


class BaseAgent(ABC):
    """
    Base class for all GWASLab Agent sub-agents.
    
    This provides a unified interface for:
    - Planner
    - SmartLoader
    - Validator
    - PathManager
    - Summarizer
    
    All sub-agents should inherit from this class and implement the required methods.
    """
    
    def __init__(
        self,
        llm=None,
        log: Optional[Log] = None,
        history: Optional[List] = None,
        archive: Optional[List] = None,
        verbose: bool = True,
        **kwargs
    ):
        """
        Initialize the base agent.
        
        Parameters
        ----------
        llm : optional
            Large Language Model instance
        log : Log, optional
            Logger instance
        history : list, optional
            Conversation history list
        archive : list, optional
            Archive list for permanent storage
        verbose : bool, default True
            Whether to print verbose output
        **kwargs
            Additional agent-specific parameters
        """
        self.llm = llm
        self.log = log or Log()
        self.history = history if history is not None else []
        self.archive = archive if archive is not None else []
        self.verbose = verbose
        # Initialize token_count as dict (can be replaced with TokenTracker object)
        self.token_count = {
            "input": 0,
            "output": 0,
            "total": 0
        }
    
    @abstractmethod
    def run(self, message: str, **kwargs) -> Any:
        """
        Main entry point for the agent.
        
        Parameters
        ----------
        message : str
            Input message/query for the agent
        **kwargs
            Agent-specific parameters
            
        Returns
        -------
        Any
            Agent-specific result
        """
        pass
    
    def get_history_stats(self) -> Dict[str, Any]:
        """
        Get statistics about agent's history usage.
        
        Returns
        -------
        dict
            Dictionary with history statistics
        """
        return {
            "history_length": len(self.history),
            "archive_length": len(self.archive),
            "agent_type": self.__class__.__name__
        }
    
    def get_token_usage(self) -> Dict[str, int]:
        """
        Get token usage statistics.
        
        Returns
        -------
        dict
            Dictionary with token counts
        """
        # Handle both dict and TokenTracker object
        if hasattr(self.token_count, 'to_dict'):
            # TokenTracker object
            return self.token_count.to_dict()
        elif isinstance(self.token_count, dict):
            # Dict format
            return self.token_count.copy()
        else:
            # Fallback: try to access as attributes
            return {
                "input": getattr(self.token_count, 'input', 0),
                "output": getattr(self.token_count, 'output', 0),
                "total": getattr(self.token_count, 'total', 0)
            }
    
    def reset_token_count(self):
        """Reset token count to zero."""
        self.token_count = {
            "input": 0,
            "output": 0,
            "total": 0
        }
    
    def _add_to_history(self, message: Dict[str, Any]):
        """
        Add message to history and archive.
        
        Parameters
        ----------
        message : dict
            Message dictionary with role, content, etc.
        """
        if self.history is not None:
            self.history.append(message)
        if self.archive is not None:
            self.archive.append(message)
    
    def clear_history(self):
        """Clear agent's history (but not archive)."""
        if self.history is not None:
            self.history.clear()
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(llm={'set' if self.llm else 'None'}, verbose={self.verbose})"

