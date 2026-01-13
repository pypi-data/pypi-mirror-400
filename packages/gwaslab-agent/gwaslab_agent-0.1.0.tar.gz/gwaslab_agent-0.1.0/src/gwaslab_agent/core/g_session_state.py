"""
Session State Management for GWASLab Agent System

This module provides centralized state management for agent sessions,
including history, results, token tracking, and execution context.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from copy import deepcopy
from gwaslab_agent.history.g_history_manager import HistoryManager
from gwaslab_agent.tools.g_build_tools import RESULTS


@dataclass
class TokenTracker:
    """Tracks token usage across all components."""
    input: int = 0
    output: int = 0
    total: int = 0
    
    def accumulate(self, input_tokens: int, output_tokens: int):
        """Accumulate token counts."""
        self.input += input_tokens
        self.output += output_tokens
        self.total = self.input + self.output
    
    def reset(self):
        """Reset all counts to zero."""
        self.input = 0
        self.output = 0
        self.total = 0
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return {
            "input": self.input,
            "output": self.output,
            "total": self.total
        }


@dataclass
class ExecutionContext:
    """Tracks execution context for scripts."""
    current_script: Optional[str] = None
    current_mode: Optional[str] = None
    last_error: Optional[str] = None
    execution_count: int = 0
    
    def start_execution(self, script: str, mode: str):
        """Mark start of script execution."""
        self.current_script = script
        self.current_mode = mode
        self.execution_count += 1
        self.last_error = None
    
    def end_execution(self, error: Optional[str] = None):
        """Mark end of script execution."""
        if error:
            self.last_error = error
        # Keep current_script and current_mode for debugging
    
    def reset(self):
        """Reset execution context."""
        self.current_script = None
        self.current_mode = None
        self.last_error = None
        self.execution_count = 0


class SessionState:
    """
    Centralized state management for agent sessions.
    
    This class manages:
    - Conversation history (via HistoryManager)
    - Results registry
    - Token tracking
    - Execution context
    - Configuration
    
    Provides a single source of truth for all session state.
    """
    
    def __init__(
        self,
        history_max_tokens: int = 50000,
        history_min_messages: int = 3,
        history_max_messages: int = 12,
        archive_max_entries: int = 1000,
        llm=None,
        enable_summarization: bool = True
    ):
        """
        Initialize session state.
        
        Parameters
        ----------
        history_max_tokens : int
            Maximum tokens in history
        history_min_messages : int
            Minimum messages to keep
        history_max_messages : int
            Maximum messages to keep
        archive_max_entries : int
            Archive compression threshold
        llm : optional
            LLM instance for summarization
        enable_summarization : bool
            Whether to enable LLM-based summarization
        """
        # Initialize HistoryManager
        self.history_manager = HistoryManager(
            max_tokens=history_max_tokens,
            min_messages=history_min_messages,
            max_messages=history_max_messages,
            archive_max_entries=archive_max_entries,
            llm=llm,
            enable_summarization=enable_summarization
        )
        
        # Expose history and archive
        self.history = self.history_manager.history
        self.archive = self.history_manager.archive
        
        # Results registry
        self.results = RESULTS
        
        # Token tracking
        self.token_tracker = TokenTracker()
        
        # Execution context
        self.execution_context = ExecutionContext()
        
        # Configuration
        self.config: Dict[str, Any] = {}
    
    def snapshot(self) -> Dict[str, Any]:
        """
        Create a snapshot of current state for rollback/restore.
        
        Returns
        -------
        dict
            Snapshot of current state
        """
        return {
            "history": deepcopy(self.history),
            "archive": deepcopy(self.archive),
            "token_tracker": asdict(self.token_tracker),
            "execution_context": asdict(self.execution_context),
            "config": deepcopy(self.config),
            "results_count": len(self.results.objects) if hasattr(self.results, 'objects') else 0
        }
    
    def restore(self, snapshot: Dict[str, Any]):
        """
        Restore state from a snapshot.
        
        Parameters
        ----------
        snapshot : dict
            Snapshot created by snapshot() method
        """
        if "history" in snapshot:
            self.history.clear()
            self.history.extend(snapshot["history"])
        
        if "archive" in snapshot:
            self.archive.clear()
            self.archive.extend(snapshot["archive"])
        
        if "token_tracker" in snapshot:
            self.token_tracker.input = snapshot["token_tracker"]["input"]
            self.token_tracker.output = snapshot["token_tracker"]["output"]
            self.token_tracker.total = snapshot["token_tracker"]["total"]
        
        if "execution_context" in snapshot:
            ctx = snapshot["execution_context"]
            self.execution_context.current_script = ctx.get("current_script")
            self.execution_context.current_mode = ctx.get("current_mode")
            self.execution_context.last_error = ctx.get("last_error")
            self.execution_context.execution_count = ctx.get("execution_count", 0)
        
        if "config" in snapshot:
            self.config = deepcopy(snapshot["config"])
    
    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current state.
        
        Returns
        -------
        dict
            State summary
        """
        return {
            "history_stats": self.history_manager.get_history_stats(),
            "token_usage": self.token_tracker.to_dict(),
            "execution_context": asdict(self.execution_context),
            "results_count": len(self.results.objects) if hasattr(self.results, 'objects') else 0,
            "config_keys": list(self.config.keys())
        }
    
    def clear(self, clear_history: bool = True, clear_archive: bool = False, clear_results: bool = True):
        """
        Clear state components.
        
        Parameters
        ----------
        clear_history : bool
            Whether to clear history
        clear_archive : bool
            Whether to clear archive
        clear_results : bool
            Whether to clear results registry
        """
        if clear_history and self.history:
            self.history.clear()
        
        if clear_archive and self.archive:
            self.archive.clear()
        
        if clear_results and hasattr(self.results, 'objects'):
            self.results.objects.clear()
        
        self.token_tracker.reset()
        self.execution_context.reset()
        self.config.clear()
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SessionState("
            f"history={len(self.history)}, "
            f"archive={len(self.archive)}, "
            f"tokens={self.token_tracker.total}, "
            f"executions={self.execution_context.execution_count}"
            f")"
        )

