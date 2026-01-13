"""
History Manager for GWASLab Agent

Provides intelligent history management with:
- Token-based pruning
- Message priority scoring
- Archive compression
- Light LLM-based summarization
- Configurable limits
"""

from gwaslab_agent.history.g_history_stages import (
    USER_INPUT, ORCHESTRATOR_REPLY, ORCHESTRATOR_TOOL_CALL
)
from gwaslab_agent.history.g_toolcall_extractor import extract_all_toolcalls


class HistoryManager:
    """
    Manages conversation history with intelligent pruning and context window management.
    
    The HistoryManager provides sophisticated history management capabilities for the GWASLab Agent,
    including automatic pruning based on token limits, message priority scoring, archive
    compression, and optional LLM-based summarization. It ensures that important messages
    (user inputs, errors, orchestrator replies) are preserved while removing less critical
    content to stay within token budgets.
    
    Key Features:
    ------------
    - **Token-based pruning**: Automatically prunes history when token limits are exceeded,
      using intelligent priority-based selection to keep important messages.
    - **Message priority scoring**: Categorizes messages as high, medium, or low priority
      based on role, content, and context (e.g., user messages and errors are high priority).
    - **Archive compression**: Maintains a compressed archive of all messages, automatically
      compressing old entries when the archive grows too large.
    - **LLM-based summarization**: Optionally uses an LLM to summarize old messages instead
      of deleting them, preserving context while reducing token usage.
    - **Agent-specific filtering**: Provides filtered history views for different agent types
      (e.g., excluding Loader messages for orchestrator).
    - **Configurable limits**: Supports configurable token limits, message counts, and
      summarization thresholds.
    
    The manager maintains two separate data structures:
    - **history**: The active, pruned history used for agent context (subject to token limits)
    - **archive**: A complete archive of all messages (compressed when it grows too large)
    
    Examples
    --------
    >>> manager = HistoryManager(max_tokens=50000, min_messages=3, max_messages=12)
    >>> manager.add_message({"role": "user", "content": "Hello"})
    >>> history = manager.get_history_for_agent("Orchestrator")
    >>> stats = manager.get_history_stats()
    """
    
    def __init__(self, 
                 max_tokens: int = 50000, 
                 min_messages: int = 3, 
                 max_messages: int = 12,
                 archive_max_entries: int = 1000,
                 llm=None,
                 enable_summarization: bool = True,
                 summarization_threshold: float = 0.8):
        """
        Initialize HistoryManager.
        
        Parameters
        ----------
        max_tokens : int
            Maximum estimated tokens to keep in history
        min_messages : int
            Minimum number of messages to always keep
        max_messages : int
            Maximum number of messages to keep (hard limit)
        archive_max_entries : int
            Maximum archive entries before compression
        llm : optional
            LLM instance for summarization (if None, summarization is disabled)
        enable_summarization : bool
            Whether to enable LLM-based summarization (default: True)
        summarization_threshold : float
            Threshold (0-1) for when to summarize. 0.8 means summarize when at 80% of max_tokens
        """
        self.max_tokens = max_tokens
        self.min_messages = min_messages
        self.max_messages = max_messages
        self.archive_max_entries = archive_max_entries
        self.llm = llm
        self.enable_summarization = enable_summarization and llm is not None
        self.summarization_threshold = summarization_threshold
        self.history = []
        self.archive = []
    
    def add_message(self, msg: dict):
        """Add message to both history and archive."""
        self.history.append(msg)
        self.archive.append(msg)
        self._prune_if_needed()
        self._compress_archive_if_needed()
    
    def _estimate_tokens(self, messages: list) -> int:
        """Estimate token count for messages (rough: 1 token ≈ 4 characters)."""
        if not messages:
            return 0
        total_chars = sum(len(str(msg.get("content", ""))) for msg in messages)
        # Also count toolcalls if present
        for msg in messages:
            if "toolcalls" in msg and msg["toolcalls"]:
                total_chars += len(str(msg["toolcalls"]))
        return total_chars // 4
    
    def _message_priority(self, msg: dict) -> str:
        """
        Determine message priority for history pruning.
        
        Returns 'high', 'medium', or 'low'
        """
        role = msg.get("role")
        agent = msg.get("gwaslab_agent")
        stage = msg.get("stage")
        content = str(msg.get("content", ""))
        
        # High priority: user messages, errors, system messages
        if role == "user":
            return "high"
        if any(keyword in content.lower() for keyword in ["error", "failed", "exception", "critical"]):
            return "high"
        if stage in (USER_INPUT, ORCHESTRATOR_REPLY):
            return "high"
        
        # Medium priority: tool calls, planner outputs
        if "toolcalls" in msg and msg["toolcalls"]:
            return "medium"
        if agent == "Planner":
            return "medium"
        if agent == "PathManager":
            return "medium"
        
        # Low priority: verbose assistant responses
        if len(content) > 2000:  # Very long responses
            return "low"
        
        return "medium"
    
    def _prune_if_needed(self):
        """Intelligently prune history if needed."""
        if not isinstance(self.history, list):
            return
        
        # Don't prune if we're below minimum threshold
        if len(self.history) <= self.min_messages:
            return
        
        # Estimate tokens
        estimated_tokens = self._estimate_tokens(self.history)
        
        # Check if pruning is needed
        needs_pruning = (
            estimated_tokens > self.max_tokens or 
            len(self.history) > self.max_messages * 2
        )
        
        if not needs_pruning:
            return
        
        # Try summarization first if enabled and LLM available
        if self.enable_summarization and estimated_tokens > self.max_tokens * self.summarization_threshold:
            if self._try_summarize_old_messages():
                # Re-estimate after summarization
                estimated_tokens = self._estimate_tokens(self.history)
                # If still over limit, proceed with pruning
                if estimated_tokens <= self.max_tokens * 0.9:  # Give some buffer
                    return
        
        # Perform intelligent pruning
        self._prune_intelligent()
    
    def _prune_intelligent(self):
        """Intelligently prune history keeping important messages."""
        if not isinstance(self.history, list) or len(self.history) <= self.min_messages:
            return
        
        # Always keep most recent messages
        min_keep = min(self.min_messages, self.max_messages // 4)
        kept = self.history[-min_keep:]
        tokens_kept = self._estimate_tokens(kept)
        
        # Add high-priority messages from earlier in history
        remaining = self.history[:-min_keep]
        
        # Sort remaining by priority (high first, then by recency)
        remaining_with_priority = []
        for msg in reversed(remaining):
            priority = self._message_priority(msg)
            remaining_with_priority.append((priority, msg))
        
        # Sort: high priority first, then by original order (reversed)
        priority_order = {"high": 0, "medium": 1, "low": 2}
        remaining_with_priority.sort(key=lambda x: (priority_order[x[0]], -remaining.index(x[1])))
        
        # Add messages until we hit limits
        for priority, msg in remaining_with_priority:
            if len(kept) >= self.max_messages:
                break
            
            msg_tokens = self._estimate_tokens([msg])
            
            # Check token limit (use 80% of budget to leave room)
            if tokens_kept + msg_tokens > self.max_tokens * 0.8:
                # If it's high priority and we're not too far over, still add it
                if priority == "high" and tokens_kept + msg_tokens <= self.max_tokens * 1.1:
                    kept.insert(0, msg)
                    tokens_kept += msg_tokens
                continue
            
            # Add message
            kept.insert(0, msg)
            tokens_kept += msg_tokens
        
        self.history = kept
    
    def _compress_archive_if_needed(self):
        """Compress old archive entries to save memory."""
        if len(self.archive) <= self.archive_max_entries:
            return
        
        self._compress_archive()
    
    def _compress_archive(self):
        """Compress old archive entries to save memory."""
        if len(self.archive) <= self.archive_max_entries:
            return
        
        # Keep recent entries as-is
        recent = self.archive[-self.archive_max_entries:]
        old = self.archive[:-self.archive_max_entries]
        
        # Extract key information from old entries
        toolcalls = extract_all_toolcalls(old)
        user_messages = [e.get("content") for e in old if e.get("role") == "user"]
        
        # Create summary entry
        summary = {
            "role": "system",
            "content": f"Compressed archive: {len(old)} messages, {len(toolcalls)} tool calls",
            "stage": "archive_summary",
            "toolcalls": toolcalls[:100],  # Keep first 100 tool calls
            "user_messages": user_messages[:20],  # Keep first 20 user messages
            "compressed_count": len(old),
            "gwaslab_agent": "HistoryManager"
        }
        
        self.archive = [summary] + recent
    
    def get_history_for_agent(self, agent_type: str, max_tokens: int = None) -> list:
        """
        Get filtered history for a specific agent type.
        
        Parameters
        ----------
        agent_type : str
            Type of agent requesting history
        max_tokens : int, optional
            Maximum tokens to return (further filtering)
        
        Returns
        -------
        list
            Filtered history messages
        """
        # Standard filtering: exclude Loader messages for orchestrator
        if agent_type != "Loader":
            filtered = [m for m in self.history 
                       if m.get("gwaslab_agent") != "Loader"]
        else:
            filtered = self.history
        
        if max_tokens:
            # Further filter by token count (from most recent)
            tokens = 0
            result = []
            for msg in reversed(filtered):
                msg_tokens = self._estimate_tokens([msg])
                if tokens + msg_tokens > max_tokens:
                    break
                result.insert(0, msg)
                tokens += msg_tokens
            return result
        
        return filtered
    
    def get_history_stats(self) -> dict:
        """Get statistics about current history."""
        total_chars = sum(len(str(msg.get("content", ""))) for msg in self.history)
        estimated_tokens = total_chars // 4
        
        by_agent = {}
        by_stage = {}
        by_priority = {"high": 0, "medium": 0, "low": 0}
        
        for msg in self.history:
            agent = msg.get("gwaslab_agent", "unknown")
            stage = msg.get("stage", "unknown")
            priority = self._message_priority(msg)
            
            by_agent[agent] = by_agent.get(agent, 0) + 1
            by_stage[stage] = by_stage.get(stage, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        return {
            "total_messages": len(self.history),
            "archive_messages": len(self.archive),
            "estimated_tokens": estimated_tokens,
            "max_tokens": self.max_tokens,
            "max_messages": self.max_messages,
            "by_agent": by_agent,
            "by_stage": by_stage,
            "by_priority": by_priority,
            "oldest_message": self.history[0] if self.history else None,
            "newest_message": self.history[-1] if self.history else None,
        }
    
    def clear_history(self, agent_types: list = None):
        """
        Clear history by agent type.
        
        Parameters
        ----------
        agent_types : list, optional
            List of agent types to clear. If None, clears all.
        """
        if agent_types is None:
            self.history = []
        else:
            self.history = [
                h for h in self.history 
                if h.get("gwaslab_agent") not in agent_types
            ]
    
    def clear_archive(self):
        """Clear archive (use with caution)."""
        self.archive = []
    
    def _try_summarize_old_messages(self) -> bool:
        """
        Try to summarize old messages using LLM.
        
        Returns
        -------
        bool
            True if summarization was successful, False otherwise
        """
        if not self.enable_summarization or self.llm is None:
            return False
        
        if len(self.history) <= self.min_messages + 2:
            return False
        
        try:
            # Identify messages to summarize (old messages, excluding recent ones)
            # Keep recent messages and high-priority messages
            recent_count = max(self.min_messages, self.max_messages // 2)
            recent = self.history[-recent_count:]
            old = self.history[:-recent_count]
            
            if len(old) < 3:  # Need at least 3 messages to summarize
                return False
            
            # Filter out high-priority messages from old (keep them as-is)
            old_to_summarize = []
            old_to_keep = []
            for msg in old:
                if self._message_priority(msg) == "high":
                    old_to_keep.append(msg)
                else:
                    old_to_summarize.append(msg)
            
            if len(old_to_summarize) < 2:  # Need at least 2 messages to summarize
                return False
            
            # Create summary using LLM
            summary = self._summarize_messages(old_to_summarize)
            
            if summary:
                # Replace old messages with summary + kept high-priority messages
                self.history = old_to_keep + [summary] + recent
                return True
            
            return False
        except Exception as e:
            # If summarization fails, just return False and let normal pruning handle it
            return False
    
    def _summarize_messages(self, messages: list) -> dict:
        """
        Summarize a list of messages using LLM.
        
        Parameters
        ----------
        messages : list
            List of message dicts to summarize
        
        Returns
        -------
        dict
            Summary message dict, or None if summarization fails
        """
        if not messages or self.llm is None:
            return None
        
        try:
            # Build prompt with messages to summarize (limit to avoid token waste)
            message_texts = []
            total_chars = 0
            max_chars = 2000  # Limit total characters for summarization prompt
            
            for msg in messages:
                if total_chars >= max_chars:
                    break
                
                role = msg.get("role", "unknown")
                agent = msg.get("gwaslab_agent", "")
                content = str(msg.get("content", ""))
                
                # Format message
                if agent:
                    prefix = f"[{agent}] "
                else:
                    prefix = ""
                
                if content:
                    # Truncate content if needed
                    remaining = max_chars - total_chars
                    if len(content) > remaining:
                        content = content[:remaining] + "..."
                    message_texts.append(f"{prefix}{role}: {content}")
                    total_chars += len(content)
                elif "toolcalls" in msg:
                    toolcalls = str(msg.get("toolcalls", ""))[:200]
                    message_texts.append(f"{prefix}{role}: [Tool calls: {toolcalls}]")
                    total_chars += len(toolcalls)
            
            if not message_texts:
                return None
            
            # Create concise summarization prompt
            messages_text = "\n".join(message_texts)
            prompt = f"""Briefly summarize these conversation messages (2-3 sentences). Focus on key requests and actions.

{messages_text}

Summary:"""
            
            # Invoke LLM with timeout protection
            from langchain_core.messages import HumanMessage
            response = self.llm.invoke([HumanMessage(content=prompt)])
            summary_content = response.content if hasattr(response, 'content') else str(response)
            
            # Limit summary length to avoid creating huge summaries
            if len(summary_content) > 500:
                summary_content = summary_content[:500] + "..."
            
            # Create summary message
            summary = {
                "role": "system",
                "content": f"[Summarized {len(messages)} messages] {summary_content}",
                "stage": "history_summary",
                "gwaslab_agent": "HistoryManager",
                "summarized_count": len(messages)
            }
            
            return summary
        except Exception as e:
            # Return None on error - will fall back to normal pruning
            return None

