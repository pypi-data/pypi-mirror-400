"""
Query Router for GWASLab Agent

This module provides a router that intelligently routes user queries to the appropriate
subagent or execution mode based on the query content:
- Path-related queries → PathManager (for finding/locating files and references)
- Planning queries → Planner (for generating execution plans)
- Loading queries → SmartLoader (for loading datasets and sumstats)
- Summarization queries → Summarizer (for generating summaries and reports)
- General queries → LLM-based execution mode selection (plan, plan_run, plan_run_sum)

The router also interprets user messages to extract:
- Script generation instructions for Planner (task/action parts only)
- Summary generation instructions for Summarizer (report/summary requirements)

The router uses keyword matching for specific subagent routing and LLM-based mode selection
for general queries that require execution planning and/or script generation.
"""

from typing import Dict, Any, Optional, Union, TypedDict, Tuple
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field
import re

from gwaslab.info.g_Log import Log
from gwaslab_agent.core.g_llm import accumulate_token_usage
from gwaslab_agent.core.g_sys_prompt import system_prompt_mode_selector
from gwaslab_agent.core.g_message_utils import extract_report_metadata


class RouteSelectionInput(BaseModel):
    """Input schema for route selection."""
    route: str = Field(
        description="The route to select: 'path_manager', 'planner', 'loader', 'summarizer', 'plan', 'plan_run', or 'plan_run_sum'"
    )


class InterpretationResult(TypedDict):
    """Result of message interpretation."""
    route: str
    script_instructions: Optional[str]
    summary_instructions: Optional[Dict[str, Any]]
    needs_summary: bool


class InstructionExtraction(BaseModel):
    """Structured output for instruction extraction."""
    script_instructions: str = Field(description="Task/action instructions for Planner (remove all summary/report related parts)")
    summary_instructions: Optional[str] = Field(default=None, description="Summary/report instructions for Summarizer (e.g., 'report in japanese', 'generate report')")


def create_route_selection_tool() -> BaseTool:
    """Create a tool for selecting query routes."""
    def select_route(route: str) -> Dict[str, str]:
        """Select the route for the user query."""
        valid_routes = [
            'path_manager', 'planner', 'loader', 'summarizer',
            'plan', 'plan_run', 'plan_run_sum'
        ]
        if route not in valid_routes:
            return {"error": f"Invalid route '{route}'. Valid routes are: {valid_routes}"}
        return {"route": route}
    
    return StructuredTool.from_function(
        func=select_route,
        name="select_query_route",
        description="Select the appropriate route/subagent for handling the user query",
        args_schema=RouteSelectionInput
    )


class QueryRouter:
    """
    Intelligent router that directs user queries to the appropriate subagent or execution mode.
    
    Routes queries based on content analysis:
    - Path-related queries → PathManager (for finding/locating files and references)
    - Planning queries → Planner (for generating execution plans)
    - Loading queries → SmartLoader (for loading datasets and sumstats)
    - Summarization queries → Summarizer (for generating summaries and reports)
    - General queries → LLM-based execution mode selection (plan, plan_run, plan_run_sum)
    
    The router also interprets user messages to extract:
    - Script generation instructions for Planner (task/action parts only, excluding summary/report parts)
    - Summary generation instructions for Summarizer (report/summary requirements including language, style, format)
    
    The router uses keyword matching for specific subagent routing and LLM-based mode selection
    for general queries that require execution planning and/or script generation.
    """
    
    # Route keyword mappings
    # PATH_KEYWORDS: Only match when query is explicitly about finding/locating paths
    # Not when reference files are mentioned as part of a larger task
    PATH_KEYWORDS = [
        'find path', 'find file', 'find reference', 'search path', 'search file',
        'locate path', 'locate file', 'locate reference', 'what path', 'what file',
        'where is', 'where are', 'check available', 'check downloaded', 'scan files',
        'list references', 'list files', 'show paths', 'show files', 'show references',
        'what references', 'what files', 'available references', 'downloaded files'
    ]
    
    PLAN_KEYWORDS = [
        'generate plan', 'create plan', 'show plan', 'what steps',
        'plan the', 'planning', 'workflow', 'steps needed', 'how to'
    ]
    
    LOAD_KEYWORDS = [
        'load', 'download', 'fetch', 'get data', 'import', 'read file',
        'open file', 'load sumstats', 'load dataset'
    ]
    
    SUMMARY_KEYWORDS = [
        'summarize', 'summary', 'summarise', 'recap', 'overview',
        'what was done', 'what happened', 'show summary'
    ]
    
    def __init__(self, agent_instance):
        """
        Initialize the query router.
        
        Parameters
        ----------
        agent_instance
            The SmartSumstats instance that contains the subagents and tools
        """
        self.agent = agent_instance
        self.log = getattr(agent_instance, 'log', None) or Log()
    
    def interpret(self, user_query: str, verbose: bool = True) -> InterpretationResult:
        """
        Interpret the user message and extract instructions for Planner and Summarizer.
        
        Parameters
        ----------
        user_query : str
            The user's query or instruction
        verbose : bool, default True
            Whether to print verbose output
        
        Returns
        -------
        InterpretationResult
            Dictionary containing:
            - 'route': The selected route
            - 'script_instructions': Instructions for script generation (for Planner)
            - 'summary_instructions': Instructions for summary generation (for Summarizer)
            - 'needs_summary': Whether a summary is needed
        """
        self.log.write("Interpreting user message...", verbose=verbose, tag="agent")
        
        # First, determine the route
        route_result = self.route(user_query, verbose=verbose, execute=False)
        route = route_result.get('route', 'plan_run')
        
        # Extract metadata for summarizer
        metadata = extract_report_metadata(user_query)
        # Always need summary after execution (plan_run, plan_run_sum, etc.), except for planning-only routes
        needs_summary = route not in ('plan', 'planner', 'path_manager', 'loader', 'summarizer')
        
        # Use LLM to interpret and extract instructions
        llm = getattr(self.agent, 'llm', None)
        if llm is not None:
            try:
                extraction = self._llm_extract_instructions(user_query, needs_summary, verbose=verbose)
                script_instructions = extraction.script_instructions
                summary_instruction_str = extraction.summary_instructions
            except Exception as e:
                self.log.write(f"LLM interpretation failed: {str(e)}, using fallback", verbose=verbose, tag="agent")
                script_instructions, summary_instruction_str = self._get_fallback_instructions(
                    user_query, needs_summary, metadata
                )
        else:
            script_instructions, summary_instruction_str = self._get_fallback_instructions(
                user_query, needs_summary, metadata
            )
        
        self.log.write(f"Instructions to planner: {script_instructions}", verbose=verbose, tag="agent")
        
        # Store summary instructions as dict
        summary_instructions = None
        if needs_summary and summary_instruction_str:
            summary_instructions = {
                'language': metadata.get('language'),
                'style': metadata.get('style'),
                'format': metadata.get('format'),
                'instruction': summary_instruction_str
            }
            self.log.write(f"Instructions to summarizer: {summary_instruction_str}", verbose=verbose, tag="agent")
        
        result: InterpretationResult = {
            'route': route,
            'script_instructions': script_instructions,
            'summary_instructions': summary_instructions,
            'needs_summary': needs_summary
        }
        
        self.log.write(f"Interpretation complete: route={route}, needs_summary={needs_summary}", verbose=verbose, tag="agent")
        return result
    
    def _llm_extract_instructions(self, user_query: str, needs_summary: bool, verbose: bool = True) -> InstructionExtraction:
        """
        Use LLM to extract instructions for Planner and Summarizer.
        
        Parameters
        ----------
        user_query : str
            The user's query
        needs_summary : bool
            Whether a summary is needed
        verbose : bool
            Whether to print verbose output
        
        Returns
        -------
        InstructionExtraction
            Extracted instructions
        """
        llm = getattr(self.agent, 'llm', None)
        if llm is None:
            raise ValueError("LLM not available")
        
        # Create prompt
        prompt = f"""Extract instructions from the user message:

User message: {user_query}

Extract:
1. script_instructions: The task/action part ONLY (remove all summary/report/documentation related parts)
   - Example: "QCをやってから日本語でレポートを作って" → "QCをやって"
   - Example: "Filter P<5e-8 and generate a report" → "Filter P<5e-8"
   
2. summary_instructions: The summary/report instruction ONLY (if summary is needed)
   - Example: "QCをやってから日本語でレポートを作って" → "report in japanese"
   - Example: "Do QC and create a report" → "generate report"
   - If no summary is needed, return "None"

Return in this format:
script_instructions: [task only]
summary_instructions: [summary instruction or None]"""
        
        if not needs_summary:
            prompt += "\n\nNote: No summary is needed, so summary_instructions should be None."
        
        messages = [HumanMessage(content=prompt)]
        
        # Invoke LLM
        try:
            # Try structured output first
            structured_llm = llm.with_structured_output(InstructionExtraction)
            response = structured_llm.invoke(messages)
            self._track_token_usage(response)
            return response
        except (AttributeError, TypeError):
            # Fallback: parse text response
            response = llm.invoke(messages)
            self._track_token_usage(response)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response
            script_instructions = user_query  # Default fallback
            summary_instructions = None
            
            # Try to extract from response
            script_match = re.search(r'script_instructions:\s*(.+?)(?:\n|summary_instructions:)', content, re.DOTALL)
            if script_match:
                script_instructions = script_match.group(1).strip()
            
            summary_match = re.search(r'summary_instructions:\s*(.+?)(?:\n|$)', content, re.DOTALL)
            if summary_match:
                summary_str = summary_match.group(1).strip()
                if summary_str.lower() not in ['none', 'null', '']:
                    summary_instructions = summary_str
            
            return InstructionExtraction(
                script_instructions=script_instructions,
                summary_instructions=summary_instructions
            )
    
    def _get_fallback_instructions(self, user_query: str, needs_summary: bool, metadata: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """
        Get fallback instructions when LLM is not available or fails.
        
        Parameters
        ----------
        user_query : str
            The user's query
        needs_summary : bool
            Whether a summary is needed
        metadata : Dict[str, Any]
            Extracted metadata
        
        Returns
        -------
        Tuple[str, Optional[str]]
            (script_instructions, summary_instruction_str)
        """
        script_instructions = user_query
        summary_instruction_str = None
        
        if needs_summary:
            language = metadata.get('language')
            if language == 'ja':
                summary_instruction_str = "report in japanese"
            elif language == 'en':
                summary_instruction_str = "report in english"
            else:
                summary_instruction_str = "generate report"
        
        return script_instructions, summary_instruction_str
    
    def _get_subagent(self, attr_name: str) -> Optional[Any]:
        """
        Get subagent from agent instance (SmartSumstats).
        
        Parameters
        ----------
        attr_name : str
            Name of the subagent attribute (e.g., 'planner', 'pathmanager')
        
        Returns
        -------
        Optional[Any]
            The subagent instance or None if not found
        """
        # Direct attribute access
        if hasattr(self.agent, attr_name):
            return getattr(self.agent, attr_name)
        
        return None
    
    def _check_keywords(self, query_lower: str, keywords: list) -> bool:
        """
        Check if query contains any of the given keywords.
        
        Parameters
        ----------
        query_lower : str
            Lowercase query string
        keywords : list
            List of keywords to check
        
        Returns
        -------
        bool
            True if any keyword is found
        """
        return any(keyword in query_lower for keyword in keywords)
    
    def route(self, user_query: str, verbose: bool = True, execute: bool = False) -> Dict[str, Any]:
        """
        Route a user query to the appropriate subagent or execution mode.
        
        Parameters
        ----------
        user_query : str
            The user's query or instruction
        verbose : bool, default True
            Whether to print verbose output
        execute : bool, default False
            If True and a handler is available, execute the handler with the query
        
        Returns
        -------
        dict
            Dictionary containing:
            - 'route': The selected route ('path_manager', 'planner', 'loader', 'summarizer', 'plan', 'plan_run', 'plan_run_sum')
            - 'handler': The handler function or method to call (if applicable)
            - 'subagent': The subagent instance (if applicable)
            - 'result': The result if execute=True and handler was called
        """
        # First, check for explicit keywords that indicate specific routes
        query_lower = user_query.lower()
        
        # Route mappings: (keywords, route_name, attr_name, handler_attr)
        route_mappings = [
            (self.PATH_KEYWORDS, 'path_manager', 'pathmanager', 'run'),
            (self.PLAN_KEYWORDS, 'planner', 'planner', 'run'),
            (self.SUMMARY_KEYWORDS, 'summarizer', 'summarizer', 'run'),
        ]
        
        for keywords, route_name, attr_name, handler_attr in route_mappings:
            if self._check_keywords(query_lower, keywords):
                # Special handling for path_manager: only route if query is explicitly about path management
                # Don't route if it's a task that happens to mention a reference file
                if route_name == 'path_manager':
                    # Check if query is about doing something (create, plot, clump, etc.) vs finding paths
                    action_keywords = ['create', 'make', 'generate', 'plot', 'clump', 'harmonize', 
                                      'filter', 'analyze', 'run', 'execute', 'do', 'perform', 'use']
                    if any(keyword in query_lower for keyword in action_keywords):
                        # This is likely a task request, not a path-finding request
                        # Continue to LLM-based mode selection instead
                        self.log.write("Query mentions reference but is a task request, using normal workflow", verbose=verbose, tag="agent")
                        break
                
                subagent = self._get_subagent(attr_name)
                if subagent is not None:
                    handler = getattr(subagent, handler_attr, None)
                    if handler is not None:
                        self.log.write(f"Routing to {route_name.replace('_', ' ').title()}", verbose=verbose, tag="agent")
                        return {
                            'route': route_name,
                            'handler': handler,
                            'subagent': subagent
                        }
        
        # Loading queries (special case: can be 'loader' or 'sl')
        if self._check_keywords(query_lower, self.LOAD_KEYWORDS):
            # Try to get loader from various possible locations
            loader = (
                getattr(self.agent, 'loader', None) or 
                getattr(self.agent, 'sl', None) or
                (getattr(self.agent, 'agent_capabilities', None) and 
                 getattr(self.agent.agent_capabilities, 'loader', None))
            )
            if loader is not None:
                self.log.write("Routing to SmartLoader", verbose=verbose, tag="agent")
                return {
                    'route': 'loader',
                    'handler': loader.run,
                    'subagent': loader
                }
            else:
                # Even if loader not found, still route to loader
                # The chat method will handle it via agent_capabilities
                self.log.write("Routing to SmartLoader (will be handled by chat)", verbose=verbose, tag="agent")
                return {
                    'route': 'loader'
                }
        
        # For general queries, use LLM-based mode selection
        result = self._select_execution_mode(user_query, verbose=verbose)
        
        # If execute is True and we have a handler, execute it
        if execute and 'handler' in result:
            try:
                handler = result['handler']
                execution_result = handler(user_query, verbose=verbose)
                result['result'] = execution_result
            except Exception as e:
                self.log.write(f"Error executing handler: {str(e)}", verbose=verbose, tag="agent")
                result['error'] = str(e)
        
        return result
    
    def _select_execution_mode(self, user_query: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Select execution mode for general queries using LLM.
        
        Parameters
        ----------
        user_query : str
            The user's query
        verbose : bool, default True
            Whether to print verbose output
        
        Returns
        -------
        dict
            Dictionary with 'route' key indicating the execution mode
        """
        self.log.write("Selecting execution mode using LLM...", verbose=verbose, tag="agent")
        
        # Get LLM from agent
        llm = getattr(self.agent, 'llm', None)
        if llm is None:
            self.log.write("No LLM available, defaulting to plan_run", verbose=verbose, tag="agent")
            return {'route': 'plan_run'}
        
        # Get available tools if available
        available_tools = self._get_available_tools()
        
        # Create enhanced system prompt
        enhanced_system_prompt = f"""{system_prompt_mode_selector}

Available Tools:
{', '.join(available_tools[:20])}{'...' if len(available_tools) > 20 else ''}

Consider the available tools when determining the complexity of the request and whether planning is needed.
"""
        
        # Create the route selection tool
        route_selection_tool = create_route_selection_tool()
        
        # Bind the tool to the LLM
        llm_with_tools = llm.bind_tools([route_selection_tool])
        
        # Create messages
        messages = [
            SystemMessage(content=enhanced_system_prompt),
            HumanMessage(content=user_query)
        ]
        
        # Invoke LLM
        response = llm_with_tools.invoke(messages)
        
        # Track token usage
        self._track_token_usage(response)
        
        # Extract route from tool call
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]
            if tool_call["name"] == "select_query_route":
                result = tool_call["args"]
                route = result.get('route', 'plan_run')
                self.log.write(f"Selected route: {route}", verbose=verbose, tag="agent")
                return {'route': route}
        
        # Fallback: parse from content
        if hasattr(response, 'content') and response.content:
            content = response.content.lower()
            if "plan_run_sum" in content:
                route = "plan_run_sum"
            elif "plan_run" in content:
                route = "plan_run"
            elif "plan" in content and "planning" not in content:
                route = "plan"
            else:
                route = "plan_run"
            self.log.write(f"Selected route (from content): {route}", verbose=verbose, tag="agent")
            return {'route': route}
        
        # Default fallback
        self.log.write("Default route: plan_run", verbose=verbose, tag="agent")
        return {'route': 'plan_run'}
    
    def _get_available_tools(self) -> list:
        """
        Get available tools from agent instance.
        
        Returns
        -------
        list
            List of tool names
        """
        if hasattr(self.agent, 'tools'):
            return [tool.name for tool in self.agent.tools] if self.agent.tools else []
        
        return []
    
    def _track_token_usage(self, response):
        """Track token usage from LLM response."""
        token_usage = None
        response_metadata = getattr(response, "response_metadata", {})
        usage_metadata = getattr(response, "usage_metadata", {})
        
        if response_metadata:
            token_usage = response_metadata.get("token_usage")
        if not token_usage and usage_metadata:
            token_usage = usage_metadata
        
        if token_usage:
            prompt_tokens = token_usage.get("prompt_tokens", token_usage.get("input_tokens", 0))
            completion_tokens = token_usage.get("completion_tokens", token_usage.get("output_tokens", 0))
            total_tokens = token_usage.get("total_tokens")
            
            self.log.write(
                f"[USAGE] prompt={prompt_tokens}, completion={completion_tokens}, "
                f"total={total_tokens if isinstance(total_tokens, int) else prompt_tokens + completion_tokens}",
                tag="agent"
            )
            
            if hasattr(self.agent, 'token_count') and isinstance(self.agent.token_count, dict):
                accumulate_token_usage(self.agent.token_count, {
                    "input": prompt_tokens if isinstance(prompt_tokens, int) else 0,
                    "output": completion_tokens if isinstance(completion_tokens, int) else 0,
                    "total": total_tokens if isinstance(total_tokens, int) else None,
                })

