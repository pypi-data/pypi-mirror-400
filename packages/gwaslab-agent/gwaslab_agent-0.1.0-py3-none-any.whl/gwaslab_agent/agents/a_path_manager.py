import numpy as np
import pandas as pd
import gwaslab as gl
import inspect
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware
from langchain_core.tools import StructuredTool
from gwaslab_agent.core.g_sys_prompt import system_prompt_path
from gwaslab_agent.history.g_history_stages import PATH_MANAGER_INPUT, PATH_MANAGER_OUTPUT
from gwaslab_agent.tools.g_build_tools import _build_args_schema, handle_tool_errors
from gwaslab_agent.core.g_print import print_message, ensure_string
from gwaslab_agent.history.g_toolcall_extractor import extract_toolcalls
from gwaslab_agent.core.g_console import console
from gwaslab_agent.tools.g_wrap_tools import wrap_main_agent_method
from gwaslab_agent.core.g_llm import get_llm
from gwaslab.info.g_Log import Log
from gwaslab_agent.core.g_base_agent import BaseAgent

class PathManager(BaseAgent):
    """
    GWASLab-Agent Path Manager
    """
    def __init__(self, log_object=None, llm=None, history=None, archive=None, verbose=True):
        if log_object is None:
            log_object = Log()
        
        if llm is None:
            llm = get_llm(log_object, verbose=verbose)
        
        # Initialize BaseAgent
        super().__init__(
            llm=llm,
            log=log_object,
            history=history,
            archive=archive,
            verbose=verbose
        )

        self.log.write("Initiating GWASLab Agent Path Manager...", verbose=verbose, tag="agent")
        self.RESULTS = {}
        self.tool_docs={}
        self.tools = self._build_tools_from_methods(verbose=verbose)
        
        self.agent = self._init_agent()

    def _init_agent(self):
        return  create_agent(       model=self.llm,
                                    tools=self.tools,
                                    system_prompt=system_prompt_path,
                                    middleware=[
                                        handle_tool_errors,
                                        ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                                        ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
                                    ]
                                )
        
    def _compose_log_message(self, message):
        return message
    
    def _get_local_refs_context(self):
        """
        Get the full list of locally available reference files using check_downloaded_ref.
        Returns the complete dictionary with paths, descriptions, and suggested uses.
        
        Returns
        -------
        str
            Formatted string containing detailed information about locally available reference files
        """
        try:
            # Call check_downloaded_ref to get local reference files
            result = gl.check_downloaded_ref()
            
            # Format the result for inclusion in prompt
            if result is None:
                return "## Local Reference Files\nNo local reference files found in registry."
            
            context_parts = ["## Local Reference Files Available"]
            
            # Handle the wrapped result structure from gwaslab tool wrapper
            if isinstance(result, dict):
                # Check if it's the wrapped format: {"status": "success", "method": "...", "type": "dict", "data": {...}}
                if "data" in result and isinstance(result["data"], dict):
                    data = result["data"]
                    # Check if there's nested "data" key
                    if "data" in data and isinstance(data["data"], dict):
                        refs_dict = data["data"]
                    elif isinstance(data, dict) and any(isinstance(v, dict) and "local_path" in v for v in data.values()):
                        # Direct dict with reference entries
                        refs_dict = data
                    else:
                        # Try to find the actual refs dict
                        refs_dict = data
                else:
                    # Direct dict format
                    refs_dict = result
                
                # Format each reference file entry
                if isinstance(refs_dict, dict) and refs_dict:
                    context_parts.append(f"\nFound {len(refs_dict)} locally available reference file(s):\n")
                    
                    for key, info in refs_dict.items():
                        if isinstance(info, dict):
                            local_path = info.get("local_path", "N/A")
                            description = info.get("description", "")
                            suggested_use = info.get("suggested_use", "")
                            
                            context_parts.append(f"- **`{key}`**")
                            context_parts.append(f"  - Path: `{local_path}`")
                            if description:
                                context_parts.append(f"  - Description: {description}")
                            if suggested_use:
                                context_parts.append(f"  - Suggested Use: {suggested_use}")
                            context_parts.append("")  # Empty line between entries
                else:
                    # Fallback: include the dict as formatted string
                    import json
                    context_parts.append(f"\n{json.dumps(refs_dict, indent=2)}")
            elif isinstance(result, str):
                # If it's a string, include it
                context_parts.append(f"\n{result}")
            else:
                # For other types, convert to string
                context_parts.append(f"\n{str(result)}")
            
            context_parts.append("\n**Note:** These are the reference files currently available locally. Use these when possible to avoid unnecessary downloads.")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            self.log.write(f"Error getting local refs context: {str(e)}", verbose=True, tag="agent")
            import traceback
            self.log.write(traceback.format_exc(), verbose=True, tag="agent")
            return "## Local Reference Files\nUnable to retrieve local reference file information."
    
    def _build_tools_from_methods(self, verbose=True):
        tools = []
        ##############################################################################################
        included_tools=["scan_downloaded_files", 
                        "check_available_ref",
                        "remove_local_record",
                        "add_local_data",
                        "check_downloaded_ref", 
                        "download_ref"]
        ## scan_downloaded_files download_ref
        for name, method in inspect.getmembers(gl, predicate=inspect.isfunction):
            if name.startswith("_"):
                continue
            if name not in included_tools:
                continue
            detailed_docs, all_schema, schema = _build_args_schema(method, if_sig=False)
            wrapped = self._wrap_method(name, method)

            tools.append(
                StructuredTool.from_function(
                    func=wrapped,
                    name=name,
                    description=inspect.getdoc(method) or "No description provided.",
                    args_schema=schema,
                )
            )
            self.tool_docs[name] = detailed_docs
        try:
            _v = getattr(self, "_init_verbose", verbose)
        except Exception:
            _v = verbose
        self.log.write(f" -Registered {len(tools)} tools for PathManager.", verbose=_v, tag="agent")
        return tools


    def _wrap_method(self, name, method):
        """Wrap a method for LLM-safe, structured output serialization."""
        return wrap_main_agent_method(self, name, method)
    
    def _extract_toolcalls(self):
        return extract_toolcalls(self.archive, "PathManager")

    @property
    def toolcalls(self):
        return self._extract_toolcalls()

    def run(self, message: str, verbose=True, verbose_return=False, return_message=True, if_print=True, message_to_return=None):
        """
        Run the path manager agent with the given message.
        The message will be enhanced with local reference file information from check_downloaded_ref.
        """

        # Get local reference files context
        local_refs_context = self._get_local_refs_context()
        
        # Compose the enhanced message with local refs context
        enhanced_message = f"""{local_refs_context}

## User Request
{message}"""
        
        composed_message = self._compose_log_message(enhanced_message)
        
        # Use BaseAgent's _add_to_history method
        self._add_to_history({
            "role": "user",
            "stage": PATH_MANAGER_INPUT,
            "gwaslab_agent": "PathManager",
            "content": composed_message
        })

        final_message = None
        result_payload = None
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

                out_msg = print_message(self, console, msg, step, True, verbose, verbose_return, if_print=if_print, title="PATH MANAGER",role="PathManager")
                if step == "tools" and getattr(msg, "content", None) is not None:
                    try:
                        import json
                        content_str = ensure_string(msg.content)
                        result_payload = json.loads(content_str)
                    except Exception:
                        result_payload = ensure_string(msg.content)
                else:
                    final_message = out_msg or final_message
                if getattr(msg, "content", None):
                    # Use BaseAgent's _add_to_history method
                    self._add_to_history({
                        "role": "assistant",
                        "gwaslab_agent": "PathManager",
                        "content": msg.content,
                        "stage": PATH_MANAGER_OUTPUT
                    })
        if return_message:
            return {"message": final_message if final_message is not None else out_msg}
        
    
