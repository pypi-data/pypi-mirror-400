from gwaslab.info.g_Log import Log
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware
from gwaslab_agent.core.g_sys_prompt import system_prompt_summarizer
from gwaslab_agent.history.g_history_stages import SUMMARIZER_INPUT, SUMMARIZER_OUTPUT
from gwaslab_agent.tools.g_build_tools import _build_tools_from_methods, handle_tool_errors
from gwaslab_agent.core.g_print import print_message
from gwaslab_agent.core.g_console import console
from gwaslab_agent.history.g_toolcall_extractor import extract_all_toolcalls
from gwaslab_agent.core.g_base_agent import BaseAgent

class Summarizer(BaseAgent):
    """
    GWASLab-Agent Summarizer
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
        
        self.log.write("Initiating GWASLab Agent Summarizer...", verbose=verbose, tag="agent")
        
        self.agent = self._init_agent()

    def _init_agent(self):
        return  create_agent(       model=self.llm,
                                    system_prompt=system_prompt_summarizer,
                                    middleware=[
                                        ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                                        ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
                                    ]
                                )
        
    def _compose_log_message(self, message, metadata=None):
        base_message = """Toolcalls:{}\n\nSumstats log:\n{}\n\nGWASLab worker message:{}""".format(
            self._extract_toolcalls(), 
            self.log.log_text, 
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
        excluded = {"get_reference_file_path", "check_file_format_and_read"}
        return extract_all_toolcalls(self.archive, exclude=excluded)

    @property
    def toolcalls(self):
        return self._extract_toolcalls()

    def run(self, message: str, history=None, verbose=True, return_message=False, verbose_return=False, message_to_return=None, metadata=None):
        """
        Run the summarizer agent with the given message.
        
        Parameters
        ----------
        message : str
            The message/context for summarization
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
        
        

        self.log.write("Calling GWASLab Agent Summarizer to summarize run and create script for replication...", verbose=verbose, tag="agent")
        if history is None:
            self.history = [] 
        else:
            self.history = history

        composed_message = self._compose_log_message(message, metadata=metadata)
        # Use BaseAgent's _add_to_history method
        self._add_to_history({
            "role": "user",
            "stage": SUMMARIZER_INPUT,
            "gwaslab_agent": "Summarizer",
            "content": composed_message
        })

        for chunk in self.agent.stream(
            {"messages": self.history},
            stream_mode="updates"
        ):
            for step, data in chunk.items():
                messages = data.get("messages", [])
                if not messages:
                    continue
                #print(step, data)
                msg = messages[-1]

                message_to_return = print_message(self, console, msg, step, return_message, verbose, verbose_return, title="SUMMARIZER",role="Summarizer")
                if getattr(msg, "content", None):
                    # Use BaseAgent's _add_to_history method
                    self._add_to_history({
                        "role": "assistant",
                        "gwaslab_agent": "Summarizer",
                        "content": msg.content,
                        "stage": SUMMARIZER_OUTPUT
                    })
        
        if return_message == True:
            return message_to_return

    
