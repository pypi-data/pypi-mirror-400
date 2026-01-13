# ================================
# Standard Library
# ================================
import gzip
import os
import sys
import re
from itertools import islice
from typing import TypedDict, Optional, Any, Dict, List

# Add gwaslab source path
sys.path.insert(0, "/home/yunye/work/gwaslab/src")

# ================================
# Third-Party Libraries
# ================================
import numpy as np
import pandas as pd
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, START, END

# ================================
# GWASLab
# ================================
import gwaslab as gl
from gwaslab.bd.bd_download import check_format, list_formats
from gwaslab.io.io_preformat_input import _preformat

# ================================
# GWASLab-Agent Modules
# ================================
from gwaslab_agent.tools.g_build_tools import _build_args_schema
from gwaslab_agent.core.g_console import console
from gwaslab_agent.core.g_sys_prompt import system_prompt_loader
from gwaslab_agent.history.g_history_stages import LOADER_INPUT, LOADER_OUTPUT
from gwaslab_agent.tools.g_wrap_tools import wrap_loader_method
from gwaslab_agent.core.g_image import _is_figure
from gwaslab_agent.core.g_base_agent import BaseAgent
from gwaslab_agent.agents.a_loader_summarizer import LoaderSummarizer
from gwaslab_agent.core.g_message_utils import extract_report_metadata
from gwaslab_agent.tools.g_toolcall_parser import _build_toolcall_string

# ================================
# Module-Level Constants and Utilities
# ================================

# Schema caching to avoid rebuilding on every loader instantiation
_TOOL_SCHEMA_CACHE = {}

def _get_cached_schema(method, if_sig=False):
    """Get schema for a method, using cache if available."""
    cache_key = (id(method), if_sig)
    if cache_key not in _TOOL_SCHEMA_CACHE:
        _TOOL_SCHEMA_CACHE[cache_key] = _build_args_schema(method, if_sig=if_sig)
    return _TOOL_SCHEMA_CACHE[cache_key]


@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        import traceback
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})\n{traceback.format_exc()}",
            tool_call_id=request.tool_call["id"]
        )


def check_file_format_and_headers(file_path: str):
    """Check file format based on extension and read first 5 lines.
    
    Args:
        file_path: Path to file to check
        
    Returns:
        Tuple of (format_extension, list_of_first_lines)
    """
    num_lines = 5
    # split file path into directory and filename
    _, ext = os.path.splitext(file_path)
    
    try:
        opener = gzip.open if ext == ".gz" else open
        mode = "rt" if ext == ".gz" else "r"
        with opener(file_path, mode) as f:
            # load first num_lines lines
            lines = list(islice(f, num_lines))
        return ext, lines
    except StopIteration:
        # File has fewer than num_lines, return what we got
        return ext, lines
    except (IOError, OSError, gzip.BadGzipFile) as e:
        # Preserve original exception type
        raise type(e)(f"Error reading file {file_path}: {e}") from e
    except Exception as e:
        # For other exceptions, wrap in IOError
        raise IOError(f"Error reading file {file_path}: {e}") from e


def _extract_file_path_with_regex(text: str, include_sumstats: bool = False) -> Optional[str]:
    """Extract file path from text using regex patterns.
    
    Args:
        text: Text to search for file path
        include_sumstats: Whether to include "sumstats" as a valid extension
        
    Returns:
        Extracted file path or None if not found
    """
    # Clean the message by removing leading "load" command
    message_clean = re.sub(r'^\s*load\s+', '', text, flags=re.IGNORECASE).strip()
    
    # Build extension pattern
    extensions = r'txt|tsv|csv|gz|vcf|bcf|bam|bed'
    if include_sumstats:
        extensions += r'|sumstats'
    
    # Look for file paths - prioritize paths with directory components
    path_patterns = [
        rf'["\']([^"\']+\.(?:{extensions}))["\']',  # Quoted paths
        rf'(\.\.?/[^\s]+\.(?:{extensions}))',  # Relative paths with ./ or ../
        rf'([^\s]*[/\\][^\s]+\.(?:{extensions}))',  # Paths with directory separators
        rf'([/][^\s]+\.(?:{extensions}))',  # Absolute paths starting with /
        rf'\b([^\s]+\.(?:{extensions}))',  # Filename only (fallback)
    ]
    
    for pattern in path_patterns:
        match = re.search(pattern, message_clean)
        if match:
            file_path = match.group(1)
            # Handle @ placeholder
            if file_path and "@" in file_path:
                file_path = file_path.replace("@", "1")
            return file_path
    
    # If still no path found, try the cleaned message as-is
    if message_clean and re.search(rf'\.(?:{extensions})', message_clean):
        file_path = message_clean
        if "@" in file_path:
            file_path = file_path.replace("@", "1")
        return file_path
    
    return None


# ================================
# LangGraph State Definition
# ================================
class LoaderState(TypedDict):
    """State schema for the LangGraph loader workflow."""
    message: str  # Original user message
    file_path: Optional[str]  # Extracted file path
    file_extension: Optional[str]  # File extension (.gz, .txt, etc.)
    file_headers: Optional[List[str]]  # First few lines of the file
    header_mapping: Optional[Dict[str, str]]  # Mapping from raw headers to GWASLab headers
    load_args: Optional[Dict[str, Any]]  # Arguments for gl.Sumstats()
    loaded_sumstats: Optional[Any]  # Resulting Sumstats object
    error: Optional[str]  # Error message if any
    step_index: int  # Current step in workflow


# ================================
# SmartLoader Class
# ================================
class SmartLoader(BaseAgent):
    """
    GWASLab-Agent Sumstats Loader
    
    Uses LangGraph workflow to ensure structured loading:
    1. Check file headers first
    2. Map headers to GWASLab standard format
    3. Load file with mappings
    4. Generate loading report
    """
    
    # ================================
    # Initialization
    # ================================
    def __init__(self, llm=None, history=None, archive=None, verbose=True, **kwargs):
        # Create empty sumstats for log access
        empty_data = pd.DataFrame()
        temp_sumstats = gl.Sumstats(empty_data, verbose=False)
        log = temp_sumstats.log
        log.log_text = ""
        
        # Initialize BaseAgent
        super().__init__(
            llm=llm,
            log=log,
            history=history,
            archive=archive,
            verbose=verbose
        )
        
        self.sumstats = temp_sumstats
        self.full_schema = {}
        self.tool_docs = {}
        
        self._init_verbose = verbose
        self._agent = None  # Lazy initialization for fallback
        self._graph = None  # Lazy initialization for LangGraph
        self._loader_summarizer = None  # Lazy initialization for loader summarizer
        self.log.write(" -Initiating GWASLab Agent Loader...", verbose=verbose, tag="agent")
        self.tools = self._build_tools_from_methods(verbose=verbose)

    # ================================
    # Tool Building and Registration
    # ================================
    def __preformat(self, **kwargs):
        """Wrapper for GWASLab's _preformat function."""
        return _preformat(log=self.log, **kwargs)
    __preformat.__doc__ = _preformat.__doc__

    def _register_tool(self, name, method, schema_method, tools, verbose=True):
        """Helper method to register a single tool with schema caching.
        
        Args:
            name: Tool name
            method: Method/function to wrap
            schema_method: Method to use for schema building (may differ from method)
            tools: List to append tool to
            verbose: Verbose flag
        """
        detailed_docs, all_schema, schema = _get_cached_schema(schema_method, if_sig=False)
        self.full_schema[name] = all_schema
        wrapped = self._wrap_method(name, method)
        
        tools.append(
            StructuredTool.from_function(
                func=wrapped,
                name=name,
                description=detailed_docs or "No description provided.",
                args_schema=schema,
            )
        )
        self.tool_docs[name] = detailed_docs

    def _build_tools_from_methods(self, verbose=True):
        """Build tools from methods with schema caching."""
        tools = []
        
        # Tool configuration: (name, method, schema_method)
        tool_configs = [
            ("Sumstats", gl.Sumstats, self.__preformat),
            ("list_formats", list_formats, list_formats),
            ("check_format", check_format, check_format),
            ("check_file_format_and_read", check_file_format_and_headers, check_file_format_and_headers),
        ]
        
        for name, method, schema_method in tool_configs:
            self._register_tool(name, method, schema_method, tools, verbose)
        
        _v = getattr(self, "_init_verbose", verbose)
        self.log.write(f" -Registered {len(tools)} tools for SmartLoader.", verbose=_v, tag="agent")
        return tools
    
    def _wrap_method(self, name, method):
        """Wrap a method for LLM-safe, structured output serialization."""
        return wrap_loader_method(self, name, method)

    # ================================
    # Agent Initialization
    # ================================
    def _init_agent(self):
        """Initialize the agent (lazy initialization)."""
        if self._agent is None:
            self._agent = create_agent(
                model=self.llm,
                tools=self.tools,
                middleware=[
                    handle_tool_errors,
                    ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0),
                    ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0)
                ],
                system_prompt=system_prompt_loader
            )
        return self._agent
    
    @property
    def agent(self):
        """Lazy-loaded agent property (fallback for non-graph mode)."""
        return self._init_agent()

    # ================================
    # Loader Summarizer Initialization
    # ================================
    def _get_loader_summarizer(self):
        """Get or create the loader summarizer (lazy initialization)."""
        if self._loader_summarizer is None:
            self._loader_summarizer = LoaderSummarizer(
                log_object=self.log,
                llm=self.llm,
                history=self.history,
                archive=self.archive,
                verbose=self._init_verbose
            )
            # Share token counter
            if hasattr(self, 'token_count'):
                self._loader_summarizer.token_count = self.token_count
        return self._loader_summarizer

    # ================================
    # LangGraph Node Definitions
    # ================================
    # These functions define the workflow steps in execution order
    
    def _extract_file_path(self, message: str) -> Optional[str]:
        """Extract file path from user message using LLM or regex fallback.
        
        Args:
            message: User message containing file path
            
        Returns:
            Extracted file path or None if extraction fails
        """
        if not self.llm:
            return None
        
        try:
            # Use LLM to extract file path from the message
            extraction_prompt = _build_file_path_extraction_prompt(message)
            
            response = self.llm.invoke([HumanMessage(content=extraction_prompt)])
            extracted_path = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            
            # Clean up the extracted path using regex helper (include sumstats extension)
            extracted_path = extracted_path.strip('"\'`')
            file_path = _extract_file_path_with_regex(extracted_path, include_sumstats=True)
            
            if file_path and len(file_path) >= 3:
                self.log.write(f" -Extracted file path by LLM: {file_path}", verbose=self._init_verbose, tag="agent")
                return file_path
            
        except Exception as e:
            # Fallback to regex extraction if LLM fails
            self.log.write(f" -LLM path extraction failed, using regex fallback: {str(e)}", verbose=self._init_verbose, tag="agent")
        
        # Regex fallback
        return _extract_file_path_with_regex(message)

    def _check_headers_node(self, state: LoaderState) -> LoaderState:
        """Step 1: Check file headers first."""
        message = state.get("message", "")
        self.log.write(" -Checking input file headers...", verbose=self._init_verbose, tag="agent")
        
        # Extract file path from message
        file_path = state.get("file_path")
        if not file_path:
            file_path = self._extract_file_path(message)
            if not file_path:
                state["error"] = f"Could not extract file path from message: {message}"
                return state
        
        state["file_path"] = file_path
        
        try:
            # Check file format and read headers
            ext, lines = check_file_format_and_headers(file_path)
            state["file_extension"] = ext
            state["file_headers"] = lines
            state["step_index"] = 1
            self.log.write(f" -File headers checked: {len(lines)} lines read", verbose=self._init_verbose, tag="agent")
        except Exception as e:
            state["error"] = f"Error checking file headers: {str(e)}"
            self.log.write(f" -✗ Error: {state['error']}", verbose=self._init_verbose, tag="agent")
        
        return state

    def _map_headers_node(self, state: LoaderState) -> LoaderState:
        """Step 2: Map raw headers to GWASLab headers using LLM agent."""
        if state.get("error"):
            return state
        
        file_headers = state.get("file_headers")
        file_path = state.get("file_path")
        if not file_headers or not file_path:
            state["error"] = "No file headers or path available for mapping"
            return state
        
        self.log.write(" -Mapping input file headers to GWASLab standard format...", verbose=self._init_verbose, tag="agent")
        
        if not self.llm:
            state["error"] = "LLM not available for header mapping"
            return state
        
        try:
            # Create a focused prompt for header mapping
            headers_text = "\n".join(file_headers[:3])  # First 3 lines
            original_message = state.get("message", "")
            mapping_message = _build_header_mapping_prompt(original_message, headers_text, file_path)
            
            # Use agent to handle the mapping and loading
            agent = self._init_agent()
            temp_history = [
                {"role": "user", "content": mapping_message, "stage": LOADER_INPUT}
            ]
            
            # Stream the agent response (silently, no reporting here)
            for chunk in agent.stream(
                {"messages": temp_history},
                stream_mode="updates"
            ):
                for step, data in chunk.items():
                    messages = data.get("messages", [])
                    if messages:
                        msg = messages[-1]
                        # Archive and log tool calls
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tool_call in msg.tool_calls:
                                # Log the tool call
                                name = tool_call.get("name", "unknown_tool")
                                args = tool_call.get("args", {})
                                tc, _prefix = _build_toolcall_string("Loader", name, args)
                                self.log.write(f"[TOOL Loader] {tc}", verbose=self._init_verbose, tag="agent")
                                
                                # Archive the tool call
                                self._add_to_history({
                                    "role": "assistant",
                                    "tool_calls": [tool_call],
                                    "stage": "tool_execution",
                                    "gwaslab_agent": "Loader"
                                })
            
            # Extract mapping from agent response or use empty dict
            state["header_mapping"] = {}  # Will be determined during loading
            state["step_index"] = 2
            
        except Exception as e:
            state["error"] = f"Error in header mapping: {str(e)}"
            self.log.write(f" -✗ Error: {state['error']}", verbose=self._init_verbose, tag="agent")
        
        return state

    def _load_file_node(self, state: LoaderState) -> LoaderState:
        """Step 3: Load the file using gl.Sumstats."""
        if state.get("error"):
            return state
        
        file_path = state.get("file_path")
        if not file_path:
            state["error"] = "No file path available for loading"
            return state
        
        # Check if sumstats was already loaded by agent in step 2
        if self.sumstats.data is not None and not self.sumstats.data.empty:
            state["loaded_sumstats"] = self.sumstats
            state["step_index"] = 3
            return state
        
        # Fallback: load using preformat function
        try:
            loaded_sumstats = self.__preformat(path=file_path, verbose=self._init_verbose)
            
            # Update loader's sumstats
            self.sumstats.data = loaded_sumstats.data
            self.sumstats.meta = loaded_sumstats.meta
            self.sumstats.build = loaded_sumstats.build
            self.log.combine(loaded_sumstats.log, pre=False)
            state["loaded_sumstats"] = loaded_sumstats
            state["step_index"] = 3
            self.log.write(" -File loaded successfully", verbose=self._init_verbose, tag="agent")
            
            # Use BaseAgent's _add_to_history method
            self._add_to_history({
                "result": loaded_sumstats,
                "stage": LOADER_OUTPUT,
                "gwaslab_agent": "Loader"
            })
            
        except Exception as e:
            state["error"] = f"Error loading file: {str(e)}"
            self.log.write(f" -✗ Error: {state['error']}", verbose=self._init_verbose, tag="agent")
        
        return state

    def _generate_report_node(self, state: LoaderState) -> LoaderState:
        """Step 4: Generate a formatted report about the loading process."""
        if state.get("error"):
            return state
        
        # Only generate report if loading was successful
        if state.get("loaded_sumstats") is None:
            return state
        
        self.log.write(" -Generating loading report about header mapping...", verbose=self._init_verbose, tag="agent")
        
        try:
            # Get loader summarizer
            loader_summarizer = self._get_loader_summarizer()
            
            # Extract metadata from original message (language, style, format preferences)
            original_message = state.get("message", "")
            metadata = extract_report_metadata(original_message)
            
            # Compose message for summarizer
            report_message = _build_loading_report_prompt(
                state.get('file_path', 'Unknown'),
                state.get('file_extension', 'Unknown')
            )
            
            # Run the summarizer (this will generate and display the report)
            # Note: history is not needed - tool calls and log are extracted from archive/log
            loader_summarizer.run(
                message=report_message,
                history=None,  # Will use empty history - context is in composed message
                verbose=self._init_verbose,
                return_message=False,
                verbose_return=False,
                metadata=metadata
            )
            
            state["step_index"] = 4
            self.log.write(" -Loading report generated", verbose=self._init_verbose, tag="agent")
            
        except Exception as e:
            # Don't fail the entire workflow if report generation fails
            self.log.write(f" -⚠ Warning: Report generation failed: {str(e)}", verbose=self._init_verbose, tag="agent")
            # Continue without error - reporting is optional
        
        return state

    # ================================
    # LangGraph Workflow Building
    # ================================
    def _build_loader_graph(self):
        """Build LangGraph workflow for structured loading process."""
        if self._graph is not None:
            return self._graph
        
        # Build the graph
        graph = StateGraph(LoaderState)
        
        # Add nodes (in workflow order)
        graph.add_node("check_headers", self._check_headers_node)
        graph.add_node("map_headers", self._map_headers_node)
        graph.add_node("load_file", self._load_file_node)
        graph.add_node("generate_report", self._generate_report_node)
        
        # Define edges: START → check_headers
        graph.add_edge(START, "check_headers")
        
        # Conditional edge after check_headers: skip to END if error, otherwise continue
        def route_after_check_headers(state: LoaderState) -> str:
            """Route after checking headers - skip to END if error."""
            if state.get("error"):
                return "end"
            return "map_headers"
        
        graph.add_conditional_edges(
            "check_headers",
            route_after_check_headers,
            {
                "map_headers": "map_headers",
                "end": END
            }
        )
        
        # Conditional edge after map_headers: skip to END if error, otherwise continue
        def route_after_map_headers(state: LoaderState) -> str:
            """Route after mapping headers - skip to END if error."""
            if state.get("error"):
                return "end"
            return "load_file"
        
        graph.add_conditional_edges(
            "map_headers",
            route_after_map_headers,
            {
                "load_file": "load_file",
                "end": END
            }
        )
        
        # Conditional edge after load_file: skip to END if error, otherwise generate report
        def route_after_load_file(state: LoaderState) -> str:
            """Route after loading file - skip to END if error, otherwise generate report."""
            if state.get("error"):
                return "end"
            return "generate_report"
        
        graph.add_conditional_edges(
            "load_file",
            route_after_load_file,
            {
                "generate_report": "generate_report",
                "end": END
            }
        )
        
        # After generate_report, always go to END
        graph.add_edge("generate_report", END)
        
        self._graph = graph.compile()
        return self._graph

    # ================================
    # Public API
    # ================================
    def run(self, message: str, verbose=True, verbose_return=False, return_message=False):
        """
        Run the loader using LangGraph workflow that always checks headers first, then maps headers, then loads.
        
        Args:
            message: User message/instruction for loading
            verbose: Whether to print verbose output
            verbose_return: Whether to return verbose output
            return_message: Whether to return the message
        """
        # Use BaseAgent's _add_to_history method
        self._add_to_history({
            "role": "user",
            "content": message,
            "stage": LOADER_INPUT,
            "gwaslab_agent": "Loader"
        })
        
        try:
            # Build graph if not already built
            graph = self._build_loader_graph()
            
            # Initialize state
            initial_state: LoaderState = {
                "message": message,
                "file_path": None,
                "file_extension": None,
                "file_headers": None,
                "header_mapping": None,
                "load_args": None,
                "loaded_sumstats": None,
                "error": None,
                "step_index": 0
            }
            
            # Run the graph
            self.log.write(" -LOADER: Starting structured loading workflow...", verbose=verbose, tag="agent")
            
            final_state = graph.invoke(initial_state)
            
            # Check for errors
            if final_state.get("error"):
                error_msg = f"Loader error: {final_state['error']}"
                self.log.write(f" -{error_msg}", verbose=verbose, tag="agent")
                if verbose:
                    console.print(f"[red]Error:[/red] {error_msg}")
                raise RuntimeError(error_msg)
            
            # Return loaded sumstats (reporting will be handled by loader summarizer)
            return final_state.get("loaded_sumstats")
            
        except Exception as e:
            error_msg = f"Loader error: {str(e)}"
            self.log.write(f" -{error_msg}", verbose=verbose)
            if verbose:
                import traceback
                console.print(f"[red]Error:[/red] {error_msg}\n{traceback.format_exc()}")
            raise


# ================================
# Prompt Templates
# ================================

def _build_file_path_extraction_prompt(message: str) -> str:
    """Build prompt for extracting file path from user message.
    
    Args:
        message: User message containing file path
        
    Returns:
        Formatted prompt string
    """
    return f"""Extract the file path from the following user message. Return ONLY the file path, nothing else.

User message: {message}

Rules:
- Extract the complete file path including directory components (e.g., "../examples/file.txt" not just "file.txt")
- Preserve relative paths (../, ./) and absolute paths (/path/to/file)
- If the message contains "load" or similar commands, extract the path that follows
- Return only the path, no quotes, no explanation
- If there's a @ placeholder for chromosome files, keep it as-is

File path:"""


def _build_header_mapping_prompt(original_message: str, headers_text: str, file_path: str) -> str:
    """Build prompt for mapping file headers to GWASLab standard format.
    
    Args:
        original_message: Original user request message
        headers_text: First few lines of file headers
        file_path: Path to the file
        
    Returns:
        Formatted prompt string
    """
    return f"""Based on the file headers I've read, determine the correct column mapping from raw headers to GWASLab standard headers and load the file.

Original user request: {original_message}

File headers:
{headers_text}

Please:
1. Analyze the headers to identify which columns map to GWASLab standard columns (SNPID, CHR, POS, EA, NEA, EAF, BETA, SE, P, N, etc.)
2. Extract format information from the user request:
   - If user explicitly mentions format (e.g., "with vcf format", "vcf file", "in vcf format") → use fmt="vcf"
   - If file extension is .vcf or .vcf.gz and user mentions VCF → use fmt="vcf"
   - For other formats, use fmt parameter if explicitly requested
3. Extract any loading arguments from the user request (e.g., "first 1000 lines" → use readargs={{"nrows": 1000}})
4. Load the file using gl.Sumstats() with the appropriate column mappings, format, and loading arguments.

File path: {file_path}

Format handling:
- "with vcf format" or "vcf file" → use fmt="vcf"
- "with VCF format" → use fmt="vcf"
- If format is explicitly mentioned, always use the fmt parameter

Loading arguments:
- "first 1000 lines" → readargs={{"nrows": 1000}}
- "first 500 rows" → readargs={{"nrows": 500}}
- Any other pandas.read_table() arguments can be passed via readargs
"""


def _build_loading_report_prompt(file_path: str, file_extension: str) -> str:
    """Build prompt for generating loading report.
    
    Args:
        file_path: Path to the loaded file
        file_extension: File extension
        
    Returns:
        Formatted prompt string
    """
    return f"""Generate a report about the file loading process.

File path: {file_path}
File extension: {file_extension}
Loading status: Successfully loaded

Please generate a formatted report describing:
1. File information (path, format)
2. Column headers found in the file
3. Column mappings applied (if any)
4. Loading results and status
"""
