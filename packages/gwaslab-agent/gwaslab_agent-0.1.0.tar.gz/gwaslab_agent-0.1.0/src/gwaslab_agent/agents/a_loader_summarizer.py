# ================================
# Standard Library
# ================================
from typing import Optional, Dict, Any

# ================================
# Third-Party Libraries
# ================================
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware

# ================================
# GWASLab-Agent Modules
# ================================
from gwaslab_agent.core.g_sys_prompt import system_prompt_loader_summarizer
from gwaslab_agent.history.g_history_stages import LOADER_SUMMARIZER_INPUT, LOADER_SUMMARIZER_OUTPUT
from gwaslab_agent.core.g_print import print_message
from gwaslab_agent.core.g_console import console
from gwaslab_agent.history.g_toolcall_extractor import extract_all_toolcalls
from gwaslab_agent.core.g_base_agent import BaseAgent


class LoaderSummarizer(BaseAgent):
    """
    GWASLab-Agent Loader Summarizer
    
    Generates formatted reports about the file loading process, including:
    - Raw headers found in the file
    - Column mappings applied
    - Loading status and results
    """
    
    def __init__(self, log_object, llm=None, history=None, archive=None, verbose=True):
        # Initialize BaseAgent
        super().__init__(
            llm=llm,
            log=log_object,
            history=history,
            archive=archive,
            verbose=verbose
        )
        
        self.log.write(" -Initiating GWASLab Agent Loader Summarizer...", verbose=verbose, tag="agent")
        
        self.agent = self._init_agent()

    def _init_agent(self):
        """Initialize the summarizer agent."""
        return create_agent(
            model=self.llm,
            system_prompt=system_prompt_loader_summarizer,
            middleware=[
                ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
            ]
        )
        
    def _compose_log_message(self, message, metadata=None):
        """Compose the message for the summarizer based on loader history and tool calls."""
        # Filter out agent logs to make it concise
        filtered_log = self.log.filter_by_tag(tag="agent", include=False, return_text=True)
        base_message = """Toolcalls:{}\n\nSumstats log:\n{}\n\nGWASLab loader message:{}""".format(
            self._extract_toolcalls(), 
            filtered_log, 
            message
        )
        
        # Add language and style instructions from metadata
        if metadata:
            from gwaslab_agent.core.g_message_utils import format_language_instruction
            language_instruction = format_language_instruction(metadata.get('language'))
            if language_instruction:
                base_message += language_instruction
            
            # Add style instructions
            style_parts = []
            if metadata.get('style'):
                style_parts.append(f"Style: {metadata['style']}")
            if metadata.get('format'):
                style_parts.append(f"Format: {metadata['format']}")
            if style_parts:
                base_message += f"\n\n## Additional Requirements\n{', '.join(style_parts)}."
        
        return base_message

    def _extract_toolcalls(self):
        """Extract tool calls from archive, excluding file format checking."""
        excluded = {"check_file_format_and_read"}
        return extract_all_toolcalls(self.archive, exclude=excluded)

    @property
    def toolcalls(self):
        """Property to access extracted tool calls."""
        return self._extract_toolcalls()

    def run(self, message: str, history=None, verbose=True, return_message=False, 
            verbose_return=False, message_to_return=None, metadata=None):
        """
        Run the loader summarizer agent with the given message.
        
        Parameters
        ----------
        message : str
            The message/context for summarization (typically includes loading results)
        history : list, optional
            Conversation history (uses self.history if None)
        verbose : bool, default True
            Whether to print verbose output
        return_message : bool, default False
            Whether to return the generated message
        verbose_return : bool, default False
            Whether to return verbose messages
        message_to_return : str, optional
            Pre-existing message to return
        metadata : dict, optional
            Metadata extracted from user message (e.g., language preferences)
            Expected keys: 'language', 'style', 'format'
        """
        
        self.log.write(" -Calling GWASLab Agent Loader Summarizer to generate loading report...", verbose=verbose, tag="agent")
        
        # Compose message with tool calls and log information
        composed_message = self._compose_log_message(message, metadata=metadata)
        
        # Use BaseAgent's _add_to_history method to archive the input
        self._add_to_history({
            "role": "user",
            "stage": LOADER_SUMMARIZER_INPUT,
            "gwaslab_agent": "LoaderSummarizer",
            "content": composed_message
        })

        # Start with empty history - all context is in the composed message
        # The composed message already includes tool calls and log information
        agent_history = [{"role": "user", "content": composed_message}]

        for chunk in self.agent.stream(
            {"messages": agent_history},
            stream_mode="updates"
        ):
            for step, data in chunk.items():
                messages = data.get("messages", [])
                if not messages:
                    continue
                
                msg = messages[-1]

                message_to_return = print_message(
                    self, console, msg, step, return_message, verbose, 
                    verbose_return, False, title="LOADER_SUMMARIZER", role="LoaderSummarizer"
                )
                if getattr(msg, "content", None):
                    # Use BaseAgent's _add_to_history method
                    self._add_to_history({
                        "role": "assistant",
                        "gwaslab_agent": "LoaderSummarizer",
                        "content": msg.content,
                        "stage": LOADER_SUMMARIZER_OUTPUT
                    })
        
        if return_message == True:
            return message_to_return

