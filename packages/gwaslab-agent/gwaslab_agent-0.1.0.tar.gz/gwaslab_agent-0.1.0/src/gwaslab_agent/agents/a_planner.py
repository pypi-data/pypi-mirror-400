from gwaslab.info.g_Log import Log
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from gwaslab_agent.history.g_history_stages import PLANNER_INPUT, PLANNER_OUTPUT
from gwaslab_agent.core.g_print import print_llm_output, print_status
from gwaslab_agent.core.g_console import console
from gwaslab.qc.qc_reserved_headers import researved_header
from gwaslab_agent.core.g_image import _scrub_log
from gwaslab_agent.core.g_base_agent import BaseAgent


class Planner(BaseAgent):
    """
    GWASLab-Agent Planner - Direct Script Generator
    
    This planner directly generates executable Python scripts for GWASLab operations
    instead of using tool calls. It uses an LLM to generate code that directly calls
    GWASLab methods on the sumstats object.
    
    Workflow
    --------
    The Planner follows a multi-stage workflow to generate and refine scripts:
    
    The workflow follows a clear graph structure (see `_get_workflow_graph()` method):
    
    1. **Script Generation**
       - Determines which GWASLab methods are needed based on the user's request
       - Fetches complete schema information for required methods (parameters, types, defaults)
       - Composes a comprehensive prompt with:
         * User's request
         * QC status and header definitions
         * Sumstats log (scrubbed)
         * Available notebook variables
         * Sumstats preview (if available)
         * Metadata (QC operations performed, references used)
         * Complete parameter schemas for required methods
       - Invokes LLM to generate Python script
    
    2. **Script Validation**
       - Extracts Python code from markdown code blocks
       - Performs multiple validation checks:
         * **Filtering assignments**: Ensures filtering methods (which return new Sumstats)
           are properly assigned to variables
         * **QC assignments**: Detects incorrect assignments from QC methods (which modify in place)
         * **Utility assignments**: Ensures utility methods (which return DataFrames/values)
           are properly assigned
         * **Plot modes**: Validates plot_mqq mode values ('m', 'qq', 'mqq', 'r', 'b')
         * **Filter chains**: Warns about excessive chaining (>3 operations)
         * **Harmonize usage**: Warns if harmonize() is called without explicit user request
         * **Redundant QC calls**: Detects individual QC functions called after basic_check()
       - Returns validation result with 'valid' flag, 'warnings' list, and 'errors' list
    
    3. **Auto-Replanning for Redundancies**
       - Automatically detects redundant function calls (e.g., calling fix_id() after basic_check())
       - If redundancies detected:
         * Generates a replanning prompt explaining the redundancy issue
         * Regenerates the script with instructions to remove redundant calls
         * Validates the new script
         * Repeats up to 2 times if redundancies persist
       - This happens automatically before showing the script to the user
    
    4. **User Confirmation Loop**
       - Displays the generated script and validation results
       - Prompts user to confirm execution or request revisions
       - If user requests revision:
         * Generates a new script incorporating user feedback
         * Re-validates the new script
         * Returns to confirmation loop
       - Continues until user confirms or max iterations reached
    
    Script Validation Details
    -------------------------
    The validation process checks for common mistakes and best practices:
    
    **Filtering Methods** (return new Sumstats objects):
    - Methods: filter_value, filter_region, filter_snp, filter_indel, etc.
    - Validation: Ensures results are assigned (e.g., `filtered = sumstats.filter_value(...)`)
    - Exception: Chained calls are allowed (e.g., `sumstats.filter_value(...).plot_mqq(...)`)
    
    **QC Methods** (modify in place, return self):
    - Methods: basic_check, harmonize, fix_id, fix_chr, fix_pos, etc.
    - Validation: Warns if results are incorrectly assigned
    - Best practice: Don't assign (e.g., `sumstats.basic_check()` not `x = sumstats.basic_check()`)
    
    **Utility Methods** (return DataFrames/values):
    - Methods: get_lead, get_top, get_novel, summary, etc.
    - Validation: Ensures results are assigned (e.g., `leads = sumstats.get_lead()`)
    
    **Redundant Call Detection**:
    - Detects if individual QC functions are called after `basic_check()`
    - Functions checked: fix_id, fix_chr, fix_pos, fix_allele, check_sanity,
      check_data_consistency, normalize_allele, remove_dup, sort_coordinate, sort_column
    - Auto-replanning: Automatically regenerates script to remove redundancies
    
    **Plot Mode Validation**:
    - Validates plot_mqq mode parameter
    - Valid modes: 'm' (Manhattan), 'qq' (QQ plot), 'mqq' (both), 'r' (regional), 'b' (density)
    - Raises error if invalid mode is used
    
    **Harmonize Usage Warning**:
    - Warns if harmonize() is called without explicit user request
    - harmonize() requires reference files and should only be called when user explicitly
      requests harmonization, allele alignment, or reference-based annotation
    
    Examples
    --------
    >>> planner = Planner(log_object=log, llm=llm, sumstats=sumstats)
    >>> script = planner.run("Filter variants with P < 5e-8 and plot Manhattan")
    >>> # Script will be auto-validated and redundant calls removed if detected
    >>> # User will be prompted to confirm or request revisions
    """
    
    def __init__(self, log_object, tools=None, llm=None, history=None, archive=None, 
                 verbose=True, sumstats=None, full_schema=None, tool_docs=None, 
                 include_sig_params=True):
        """Initialize Planner with tools, LLM, and context.
        
        Parameters
        ----------
        log_object : Log
            Logger instance
        tools : list, optional
            List of tools available to the planner
        llm : optional
            LLM instance
        history : list, optional
            Conversation history
        archive : list, optional
            Archive for permanent storage
        verbose : bool, default True
            Verbose flag
        sumstats : optional
            Sumstats object for context
        full_schema : dict, optional
            Full schema for tools
        tool_docs : dict, optional
            Tool documentation
        include_sig_params : bool, default=True
            If True, merge signature parameters with docstring parameters.
            If False, only use parameters from docstring.
        """
        # Initialize BaseAgent
        super().__init__(
            llm=llm,
            log=log_object,
            history=history,
            archive=archive,
            verbose=verbose
        )
        
        self.log.write("Initiating GWASLab Agent Planner (Direct Script Generator)...", verbose=verbose, tag="agent")
        
        self.tools = self._filter_allowed_tools(tools)
        self.sumstats = sumstats
        self.full_schema = full_schema if full_schema is not None else {}
        self.tool_docs = tool_docs if tool_docs is not None else {}
        self.include_sig_params = include_sig_params
        self.tool_index = self._summarize_tools(include_args=False, max_desc_length=50)
    
    # ============================================================================
    # Workflow Graph Structure
    # ============================================================================
    
    def _get_workflow_graph(self):
        """
        Get the workflow graph structure that defines the planner execution flow.
        
        Returns:
            dict: Workflow graph mapping stage names to their execution methods and next stages
        """
        return {
            "start": {
                "method": None,
                "next": ["script_generation"],
                "description": "Entry point: User request received"
            },
            "script_generation": {
                "method": self._generate_script,
                "next": ["initial_validation"],
                "description": "Generate initial Python script from user request"
            },
            "initial_validation": {
                "method": self._validate_script,
                "next": ["redundancy_check"],
                "description": "Validate script for common mistakes and best practices"
            },
            "redundancy_check": {
                "method": self._detect_redundant_calls_for_replanning,
                "next": ["auto_replan", "user_confirmation"],
                "description": "Check for redundant QC function calls",
                "condition": "If redundancies found → auto_replan, else → user_confirmation"
            },
            "auto_replan": {
                "method": self._auto_replan_if_redundant,
                "next": ["re_validation"],
                "description": "Auto-replan to fix redundant calls (max 2 attempts)"
            },
            "re_validation": {
                "method": self._validate_script,
                "next": ["user_confirmation"],
                "description": "Re-validate script after auto-replanning"
            },
            "user_confirmation": {
                "method": self._confirmation_loop,
                "next": ["end"],
                "description": "User confirmation loop (max 10 iterations)"
            },
            "display_script": {
                "method": self._display_script_and_validation,
                "next": ["user_input"],
                "description": "Display script and validation results"
            },
            "user_input": {
                "method": self._check_user_confirmation,
                "next": ["end", "handle_revision", "display_script"],
                "description": "Get user input (confirm/revision/retry)",
                "condition": "Confirmed → end, Revision → handle_revision, Retry → display_script"
            },
            "handle_revision": {
                "method": self._handle_revision_request,
                "next": ["final_validation"],
                "description": "Generate revised script based on user feedback"
            },
            "final_validation": {
                "method": self._validate_script,
                "next": ["display_script"],
                "description": "Validate revised script, then loop back to display"
            },
            "end": {
                "method": None,
                "next": [],
                "description": "End of workflow: Return final script"
            }
        }
    
    # ============================================================================
    # Message Composition
    # ============================================================================
    
    def _compose_log_message(self, message):
        """Compose full message with QC status, header definitions, log, and notebook vars."""
        qc_str = self._get_qc_status()
        header_def_str = self._get_header_definition()
        scrubbed_log = self._get_scrubbed_log()
        notebook_vars_str = self._get_notebook_variables()
        
        return "QC status: {}\n\nHeaderDefinition: {}\n\nSumstats log:\n{}\n\nUser message:{}{}".format(
            qc_str, header_def_str, scrubbed_log, message, notebook_vars_str
        )
    
    def _get_qc_status(self):
        """Get QC status from sumstats if available, parsed to compact list format."""
        try:
            if hasattr(self, "sumstats") and self.sumstats is not None:
                fn = getattr(self.sumstats, "check_sumstats_qc_status", None)
                if callable(fn):
                    qc = fn()
                    if isinstance(qc, dict):
                        # Parse QC status to compact list format
                        qc_performed = self._extract_performed_qc_ops(qc)
                        if qc_performed:
                            return ", ".join(qc_performed)
                        else:
                            return "None"
                    elif isinstance(qc, list):
                        # If it's already a list, return as comma-separated string
                        return ", ".join(str(op) for op in qc) if qc else "None"
                    elif qc is not None:
                        return str(qc)
        except Exception:
            pass
        return "unavailable"
    
    def _extract_performed_qc_ops(self, qc_dict: dict) -> list:
        """
        Extract all performed QC operations from QC status dictionary.
        
        Recursively traverses the nested structure and returns a list of operation names
        where performed=True. Only includes operations that have been performed.
        """
        def extract_performed_ops(status_dict: dict, prefix: str = "") -> list:
            """Recursively extract all operations where performed=True."""
            performed = []
            if not isinstance(status_dict, dict):
                return performed
            
            for key, value in status_dict.items():
                if isinstance(value, dict):
                    # Check if this is an operation entry with 'performed' key
                    if "performed" in value:
                        if value.get("performed", False):
                            op_name = f"{prefix}.{key}" if prefix else key
                            performed.append(op_name)
                    else:
                        # Recursively check nested structures
                        new_prefix = f"{prefix}.{key}" if prefix else key
                        performed.extend(extract_performed_ops(value, new_prefix))
            
            return performed
        
        qc_performed = []
        
        # Top-level operations
        if qc_dict.get("basic_check", {}).get("performed", False):
            qc_performed.append("basic_check")
        if qc_dict.get("harmonize", {}).get("performed", False):
            qc_performed.append("harmonize")
        
        # Extract from qc_and_harmonization_status structure
        qc_status_info = qc_dict.get("qc_and_harmonization_status", {})
        if qc_status_info:
            qc_performed.extend(extract_performed_ops(qc_status_info))
        
        return qc_performed
    
    def _get_header_definition(self):
        """Get header definition from reserved headers."""
        try:
            if isinstance(researved_header, dict):
                import json
                return json.dumps(researved_header, ensure_ascii=False)
            else:
                return str(researved_header)
        except Exception:
            pass
        return "unavailable"
    
    def _get_scrubbed_log(self, max_length=2000):
        """Get scrubbed log text, truncated to max_length. Filters out agent logs to make it concise."""
        try:
            # Filter out agent logs before scrubbing
            filtered_log = self.log.filter_by_tag(tag="agent", include=False, return_text=True)
            scrubbed_log = _scrub_log(filtered_log)
            if len(scrubbed_log) > max_length:
                return "...[truncated earlier log]...\n" + scrubbed_log[-max_length:]
            return scrubbed_log
        except Exception:
            # Fallback: filter and truncate
            filtered_log = self.log.filter_by_tag(tag="agent", include=False, return_text=True)
            if len(filtered_log) > max_length:
                return "...[truncated earlier log]...\n" + filtered_log[-max_length:]
            return filtered_log
    
    def _get_notebook_variables(self, max_vars=10, max_repr_length=150):
        """Get available variables from Jupyter notebook namespace."""
        try:
            from IPython import get_ipython
            ipython = get_ipython()
            if ipython is None:
                return ""
            
            user_ns = getattr(ipython, 'user_ns', {})
            if not user_ns:
                return ""
            
            user_vars = self._extract_notebook_vars(user_ns, max_repr_length)
            if not user_vars:
                return ""
            
            # Limit to top N variables to save tokens
            limited_vars = dict(list(sorted(user_vars.items()))[:max_vars])
            vars_list = "\n".join([f"  - {k} = {v}" for k, v in limited_vars.items()])
            return f"\n\nAvailable notebook variables (top {max_vars}):\n{vars_list}\n\nYou can use these variables directly in the generated script."
        except Exception:
            return ""
    
    def _extract_notebook_vars(self, user_ns, max_repr_length):
        """Extract and format user-defined variables from notebook namespace."""
        user_vars = {}
        skip_keys = ['In', 'Out', 'get_ipython', 'exit', 'quit', 'open', 'print']
        
        for k, v in user_ns.items():
            # Skip private variables (except special builtins)
            if k.startswith('_') and k not in ['__builtins__', '__name__', '__doc__']:
                continue
            if k in skip_keys:
                continue
            
            var_repr = self._format_variable_repr(k, v, max_repr_length)
            if var_repr:
                user_vars[k] = var_repr
        
        return user_vars
    
    def _format_variable_repr(self, key, value, max_length):
        """Format variable representation for display."""
        # Simple types
        if isinstance(value, (int, float, str, bool, list, dict, tuple, type(None))):
            var_type = type(value).__name__
            var_repr = repr(value)
            if len(var_repr) > max_length:
                var_repr = var_repr[:max_length] + "..."
            return f"{var_type}: {var_repr}"
        
        # NumPy/Pandas objects
        if hasattr(value, '__class__'):
            class_name = value.__class__.__name__
            if class_name in ['ndarray', 'Series', 'DataFrame', 'int64', 'float64']:
                var_repr = str(value)
                if len(var_repr) > max_length:
                    var_repr = var_repr[:max_length] + "..."
                return f"{class_name}: {var_repr}"
            
            # Other objects with string representation
            if hasattr(value, '__str__'):
                try:
                    var_repr = str(value)
                    if len(var_repr) <= max_length and not var_repr.startswith('<'):
                        return f"{class_name}: {var_repr}"
                except Exception:
                    pass
        
        return None
    
    # ============================================================================
    # Tool Management
    # ============================================================================
    
    def _filter_allowed_tools(self, tools):
        """Filter tools to only include those listed in g_tools.py."""
        if not isinstance(tools, list):
            return tools
        
        from gwaslab_agent.tools.g_tools import (
            HARMONIZER_SET, DOWNSTREAM_SET, UTILITY_SET, PLOTTER_SET, FILTERER_SET
        )
        
        allowed_tools = (
            HARMONIZER_SET | DOWNSTREAM_SET | UTILITY_SET | PLOTTER_SET | FILTERER_SET
        )
        
        filtered_tools = []
        for t in tools:
            name = getattr(t, "name", None) or str(t)
            if isinstance(name, str):
                if name.startswith("call_") or name not in allowed_tools:
                    continue
                filtered_tools.append(t)
        
        return filtered_tools
    
    def _summarize_tools(self, include_args=False, max_desc_length=50):
        """Generate simplified tool index for planner."""
        if not isinstance(self.tools, list):
            return ""

        from gwaslab_agent.tools.g_tools import (
            HARMONIZER_SET, DOWNSTREAM_SET, UTILITY_SET, PLOTTER_SET, FILTERER_SET
        )

        categorized_tools = self._categorize_tools()
        return self._format_tool_index(categorized_tools, max_desc_length)
    
    def _categorize_tools(self):
        """Group tools by category."""
        from gwaslab_agent.tools.g_tools import (
            HARMONIZER_SET, DOWNSTREAM_SET, UTILITY_SET, PLOTTER_SET, FILTERER_SET
        )
        
        allowed_tools = (
            HARMONIZER_SET | DOWNSTREAM_SET | UTILITY_SET | PLOTTER_SET | FILTERER_SET
        )
        
        categorized = {
            "QC/Harmonization Methods (modify in place)": [],
            "Filtering Methods (return new Sumstats)": [],
            "Plotting Methods (return figures)": [],
            "Utility Methods (return DataFrames/values)": [],
            "Downstream Methods (return results)": []
        }
        
        for t in self.tools:
            name = getattr(t, "name", None) or str(t)
            if not isinstance(name, str) or name.startswith("call_") or name not in allowed_tools:
                continue
            
            # Find category by checking membership in each set
            if name in HARMONIZER_SET:
                categorized["QC/Harmonization Methods (modify in place)"].append(t)
            elif name in FILTERER_SET:
                categorized["Filtering Methods (return new Sumstats)"].append(t)
            elif name in PLOTTER_SET:
                categorized["Plotting Methods (return figures)"].append(t)
            elif name in UTILITY_SET:
                categorized["Utility Methods (return DataFrames/values)"].append(t)
            elif name in DOWNSTREAM_SET:
                categorized["Downstream Methods (return results)"].append(t)
        
        return categorized
    
    def _format_tool_index(self, categorized_tools, max_desc_length):
        """Format categorized tools into index string."""
        from gwaslab_agent.tools.g_tools import (
            HARMONIZER_SET, DOWNSTREAM_SET, UTILITY_SET, PLOTTER_SET, FILTERER_SET
        )
        
        def _oneline(text: str) -> str:
            return " ".join(text.split()) if text else ""

        def _get_return_type(name):
            # First, try to get return info from parsed docstring
            if name in self.full_schema:
                schema = self.full_schema.get(name, {})
                if isinstance(schema, dict):
                    returns_info = schema.get("returns") or schema.get("_returns")
                    if returns_info:
                        return_type = returns_info.get("type", "object")
                        return_desc = returns_info.get("description", "")
                        if return_desc:
                            # Use first line of description if available
                            desc_first_line = return_desc.split('\n')[0].strip()
                            if desc_first_line:
                                return f" → Returns {return_type}: {desc_first_line}"
                            else:
                                return f" → Returns {return_type}"
                        else:
                            return f" → Returns {return_type}"
            
            # Fallback to hardcoded return types based on tool sets
            if name in FILTERER_SET:
                return " → Returns Sumstats (assign result!)"
            elif name in HARMONIZER_SET:
                return " → Modifies in place (don't assign)"
            elif name in PLOTTER_SET:
                return " → Returns figure (can assign or ignore)"
            elif name in UTILITY_SET:
                return " → Returns DataFrame/value (assign result!)"
            elif name in DOWNSTREAM_SET:
                return " → Returns results (assign result!)"
            return ""

        lines = []
        lines.append("Note: Detailed parameter information is available in full_schema. Use method names and return types below.\n")

        for category, tools in categorized_tools.items():
            if not tools:
                continue
            
            lines.append("")
            lines.append(f"### {category}")
            lines.append("")

            for t in tools:
                name = getattr(t, "name", None) or str(t)
                desc = _oneline(getattr(t, "description", "") or "")
                
                if len(desc) > max_desc_length:
                    desc = desc[:max_desc_length] + "..."
                
                return_type = _get_return_type(name)
                lines.append(f"- {name}: {desc}{return_type}")

        return "\n".join(lines)
    
    def check_full_schema(self, tool_names) -> dict:
        """
        Get the full schema (description and all arguments) for one or more gwaslab functions.
        
        Parameters
        ----------
        tool_names : str or list of str
            The name(s) of the tool/function(s) to get the full schema for.
            Can be a single tool name (str) or a list of tool names.
        
        Returns
        -------
        dict
            If a single tool name is provided: A dictionary containing:
            - description: Full description of the tool
            - args: Complete argument schema with all parameters
            
            If multiple tool names are provided: A dictionary mapping tool names to their schemas.
        """
        # Normalize input to list
        if isinstance(tool_names, str):
            tool_names_list = [tool_names]
            return_single = True
        else:
            tool_names_list = tool_names
            return_single = False
        
        # Log the request
        if return_single:
            self.log.write(f"Checking full schema for tool: {tool_names}", verbose=True, tag="agent")
        else:
            self.log.write(f"Checking full schema for {len(tool_names_list)} tools: {', '.join(tool_names_list)}", verbose=True, tag="agent")
        
        result = {}
        for tool_name in tool_names_list:
            result[tool_name] = self._get_single_tool_schema(tool_name)
        
        # Log results summary
        found_count = sum(1 for v in result.values() if v.get("description", "").startswith("Tool '") == False)
        if found_count < len(tool_names_list):
            not_found = [name for name, schema in result.items() if schema.get("description", "").startswith("Tool '")]
            self.log.write(f"Schema check complete: {found_count}/{len(tool_names_list)} tools found. Not found: {', '.join(not_found) if not_found else 'none'}", verbose=True, tag="agent")
        else:
            self.log.write(f"Schema check complete: All {len(tool_names_list)} tool(s) found", verbose=True, tag="agent")
        
        # Return single dict if only one tool was requested
        return result[tool_names_list[0]] if return_single else result
    
    def _filter_schema_args(self, properties, required):
        """Filter out args starting with '_' and column name args."""
        # Common column name arguments to filter out
        colname_args = {
            'chrom', 'chr', 'pos', 'ea', 'nea', 'snpid', 'rsid', 
            'chromosome', 'position', 'effect_allele', 'non_effect_allele',
            'a1', 'a2', 'ref', 'alt', 'allele1', 'allele2'
        }
        
        filtered_props = {}
        filtered_required = []
        
        for param_name, param_info in properties.items():
            # Filter out args starting with "_"
            if param_name.startswith("_"):
                continue
            
            # Filter out column name args (case-insensitive)
            if param_name.lower() in colname_args:
                continue
            
            filtered_props[param_name] = param_info
            if param_name in required:
                filtered_required.append(param_name)
        
        return filtered_props, filtered_required
    
    def _get_internal_functions_for_all_in_one(self, tool_name):
        """
        Get list of internal function names for all-in-one functions.
        
        All-in-one functions like `basic_check()` and `harmonize()` internally call
        multiple individual QC/harmonization functions. This method returns the list
        of public method names that are called internally, so their schemas can be
        included in the all-in-one function's schema.
        
        Parameters
        ----------
        tool_name : str
            Name of the all-in-one function ('basic_check' or 'harmonize')
        
        Returns
        -------
        list of str
            List of public method names that are called internally by the all-in-one function.
            Returns empty list if tool_name is not a recognized all-in-one function.
        """
        # Define the set of functions included in basic_check()
        # These are the core QC operations performed by basic_check()
        BASIC_CHECK_FUNCTIONS = [
            'fix_id',
            'fix_chr',
            'fix_pos',
            'fix_allele',
            'check_sanity',
            'check_data_consistency',
            'normalize_allele',
            'remove_dup',
            'sort_coordinate',
            'sort_column'
        ]
        
        # Define additional functions included in harmonize()
        # harmonize() includes all basic_check functions plus these harmonization-specific ones
        HARMONIZE_ADDITIONAL_FUNCTIONS = [
            'flip_allele_stats',
            'infer_strand',
            'assign_rsid'
        ]
        
        # Map tool names to their internal function lists
        if tool_name == 'basic_check':
            return BASIC_CHECK_FUNCTIONS
        elif tool_name == 'harmonize':
            # harmonize() includes all basic_check functions plus harmonization-specific ones
            return BASIC_CHECK_FUNCTIONS + HARMONIZE_ADDITIONAL_FUNCTIONS
        
        # Unknown all-in-one function
        return []
    
    def _get_single_tool_schema(self, tool_name):
        """
        Get schema for a single tool using a priority-based approach.
        
        Priority order:
        1. Use cached schema if available (fastest)
        2. Build schema from sumstats method using _build_args_schema (primary source)
        3. Fallback to tools list (rarely needed)
        
        Parameters
        ----------
        tool_name : str
            Name of the tool/method to get schema for
        
        Returns
        -------
        dict
            Dictionary with 'description' and 'args' keys, optionally 'returns' key.
            If tool not found, returns dict with error message.
        """
        # Priority 1: Use cached schema if available
        cached_result = self._get_schema_from_cache(tool_name)
        if cached_result is not None:
            return cached_result
        
        # Priority 2: Build schema from sumstats method (primary source)
        if self.sumstats is not None:
            sumstats_result = self._build_schema_from_sumstats_method(tool_name)
            if sumstats_result is not None:
                return sumstats_result
        
        # Priority 3: Fallback to tools list (should rarely be needed)
        tools_result = self._get_schema_from_tools_list(tool_name)
        if tools_result is not None:
            return tools_result
        
        # Tool not found in any source
        self.log.write(f"  - Tool '{tool_name}' not found in sumstats methods or tools", verbose=True, tag="agent")
        return {
            "description": f"Tool '{tool_name}' not found",
            "args": {}
        }
    
    def _get_schema_from_cache(self, tool_name):
        """
        Get schema from cache if available.
        
        Returns None if not cached, otherwise returns the cached schema.
        Handles both old format (parameter dict) and new format (schema dict with properties).
        """
        if tool_name not in self.full_schema:
            return None
        
        cached = self.full_schema.get(tool_name, {})
        
        # Normalize cached schema to standard format
        args = self._normalize_cached_schema_format(cached)
        
        # Apply filters to remove internal args and column name args
        if "properties" in args:
            filtered_props, filtered_required = self._filter_schema_args(
                args.get("properties", {}), 
                args.get("required", [])
            )
            args = {
                "type": "object",
                "properties": filtered_props,
                "required": filtered_required
            }
        
        # Build result dictionary
        result = {
            "description": self.tool_docs.get(tool_name, "No description available"),
            "args": args
        }
        
        # Include return information if available
        if isinstance(cached, dict):
            if "returns" in cached:
                result["returns"] = cached["returns"]
            elif "_returns" in cached:
                result["returns"] = cached["_returns"]
        
        return result
    
    def _normalize_cached_schema_format(self, cached):
        """
        Normalize cached schema to standard format.
        
        Handles both old format (parameter dict directly) and new format (schema dict with properties).
        """
        if not isinstance(cached, dict):
            return {}
        
        if "properties" in cached:
            # New format: schema dict with properties
            return cached
        else:
            # Old format: parameter dict directly, wrap it in schema format
            return {
                "type": "object",
                "properties": cached,
                "required": []
            }
    
    def _build_schema_from_sumstats_method(self, tool_name):
        """
        Build schema from sumstats method using _build_args_schema.
        
        This is the primary source since tools are Sumstats object methods.
        Also handles all-in-one functions by including internal function schemas.
        
        Returns None if method not found or error occurs.
        """
        import inspect
        from gwaslab_agent.tools.g_build_tools import _build_args_schema
        
        try:
            method = getattr(self.sumstats, tool_name, None)
            if not method or not inspect.ismethod(method):
                return None
            
            # Get docstring parameters (primary source)
            detailed_docs, all_schema, schema_doc = _build_args_schema(method, if_sig=False)
            props_doc = schema_doc.get("properties", {})
            
            # Merge docstring and signature parameters if enabled
            if self.include_sig_params:
                final_schema = self._merge_docstring_and_signature_params(method, props_doc, schema_doc)
            else:
                # Only use docstring parameters
                final_schema = schema_doc
            
            # Apply filters: remove args starting with "_" and column name args
            final_schema = self._apply_schema_filters(final_schema)
            
            # For all-in-one functions, include internal function schemas
            internal_schemas = self._get_internal_function_schemas(tool_name)
            if internal_schemas:
                final_schema["internal_functions"] = internal_schemas
            
            # Extract return information from schema_doc if available
            return_info = schema_doc.get("returns")
            if return_info:
                final_schema["returns"] = return_info
            
            # Cache the schema for future use
            self.full_schema[tool_name] = final_schema
            self.tool_docs[tool_name] = detailed_docs
            
            # Build result dictionary
            result = {
                "description": detailed_docs or "No description available",
                "args": final_schema
            }
            if return_info:
                result["returns"] = return_info
            
            return result
            
        except Exception as e:
            self.log.write(f"  - Error building schema for '{tool_name}' from sumstats: {str(e)}", verbose=True, tag="agent")
            import traceback
            self.log.write(f"  - Traceback: {traceback.format_exc()}", verbose=True, tag="agent")
            return None
    
    def _merge_docstring_and_signature_params(self, method, props_doc, schema_doc):
        """
        Merge docstring parameters with signature parameters.
        
        This ensures we get both docstring args AND wrapper signature params
        (e.g., build, gls) that aren't in the docstring.
        """
        from gwaslab_agent.tools.g_build_tools import _build_args_schema
        
        # Get signature parameters to catch wrapper parameters not in docstring
        _, _, schema_sig = _build_args_schema(method, if_sig=True)
        props_sig = schema_sig.get("properties", {})
        
        # Start with docstring params, then add signature params not in docstring
        merged_props = dict(props_doc)
        merged_required = list(schema_doc.get("required", []))
        
        # Add signature params that aren't in docstring (these are wrapper params)
        sig_params_to_add = set(props_sig.keys()) - set(props_doc.keys())
        for param_name in sig_params_to_add:
            merged_props[param_name] = props_sig[param_name]
            # If it's required in signature and not in docstring, add to required
            if param_name in schema_sig.get("required", []):
                if param_name not in merged_required:
                    merged_required.append(param_name)
        
        # Create merged schema
        return {
            "type": "object",
            "properties": merged_props,
            "required": merged_required
        }
    
    def _apply_schema_filters(self, schema):
        """
        Apply filters to schema: remove args starting with "_" and column name args.
        
        Returns filtered schema in standard format.
        """
        if "properties" not in schema:
            return schema
        
        filtered_props, filtered_required = self._filter_schema_args(
            schema.get("properties", {}),
            schema.get("required", [])
        )
        
        return {
            "type": "object",
            "properties": filtered_props,
            "required": filtered_required
        }
    
    def _get_internal_function_schemas(self, tool_name):
        """
        Get schemas for internal functions of all-in-one functions.
        
        For all-in-one functions like basic_check() and harmonize(), this method
        retrieves the schemas of the internal functions they call.
        
        Returns dict mapping internal function names to their schemas, or empty dict.
        """
        import inspect
        from gwaslab_agent.tools.g_build_tools import _build_args_schema
        
        internal_functions = self._get_internal_functions_for_all_in_one(tool_name)
        if not internal_functions:
            return {}
        
        internal_schemas = {}
        for internal_func_name in internal_functions:
            try:
                internal_method = getattr(self.sumstats, internal_func_name, None)
                if not internal_method or not inspect.ismethod(internal_method):
                    continue
                
                # Get schema for internal function
                _, _, internal_schema = _build_args_schema(internal_method, if_sig=False)
                internal_props = internal_schema.get("properties", {})
                internal_required = internal_schema.get("required", [])
                
                # Apply filters to internal function schemas too
                filtered_internal_props, filtered_internal_required = self._filter_schema_args(
                    internal_props, internal_required
                )
                
                if filtered_internal_props:
                    internal_schemas[internal_func_name] = {
                        "type": "object",
                        "properties": filtered_internal_props,
                        "required": filtered_internal_required
                    }
            except Exception as e:
                self.log.write(
                    f"  - Error getting schema for internal function '{internal_func_name}': {str(e)}",
                    verbose=True,
                    tag="agent"
                )
        
        return internal_schemas
    
    def _get_schema_from_tools_list(self, tool_name):
        """
        Get schema from tools list as fallback (should rarely be needed).
        
        Returns None if tool not found in tools list.
        """
        for t in self.tools:
            if getattr(t, "name", None) != tool_name:
                continue
            
            schema = getattr(t, "args_schema", None)
            try:
                if isinstance(schema, dict):
                    sdict = schema
                elif hasattr(schema, "schema"):
                    sdict = schema.schema()
                else:
                    sdict = {}
                
                return {
                    "description": getattr(t, "description", "No description available"),
                    "args": sdict
                }
            except Exception as e:
                self.log.write(
                    f"  - Error extracting schema for '{tool_name}' from tools: {str(e)}",
                    verbose=True,
                    tag="agent"
                )
        
        return None
    
    # ============================================================================
    # System Prompt
    # ============================================================================
    
    def _get_system_prompt(self):
        """Get complete system prompt for direct script generation."""
        prompt = _build_system_prompt_base()
        
        # Add tool index if available
        if self.tool_index:
            prompt += "\n\n## Available Methods\n" + self.tool_index
            prompt += _build_system_prompt_tool_index_section()
        
        return prompt
    
    # ============================================================================
    # Script Generation
    # ============================================================================
    
    def _parse_meta(self, meta: dict) -> str:
        """Parse and format meta dictionary to reduce token usage with proper QC status parsing."""
        if not meta or not isinstance(meta, dict):
            return ""
        
        sections = []
        
        # ========================================================================
        # Basic Information
        # ========================================================================
        basic_info = []
        if "gwaslab_version" in meta:
            basic_info.append(f"GWASLab version: {meta['gwaslab_version']}")
        if "genome_build" in meta and meta.get("genome_build") != "Unknown":
            basic_info.append(f"Genome build: {meta['genome_build']}")
        if "study_name" in meta and meta.get("study_name") != "Unknown":
            basic_info.append(f"Study: {meta['study_name']}")
        
        if basic_info:
            sections.append("## Basic Information\n" + "\n".join(basic_info))
        
        # ========================================================================
        # QC Status (from qc_and_harmonization_status structure)
        # Parse to list format to save tokens, only keep performed operations
        # ========================================================================
        qc_performed = self._extract_performed_qc_ops(meta)
        
        # Format as compact list (only include if non-empty)
        if qc_performed:
            sections.append("## QC Status\nQC operations performed: " + ", ".join(qc_performed))
        
        # ========================================================================
        # References
        # ========================================================================
        refs = meta.get("references", {})
        refs_used = []
        for ref_key, ref_value in refs.items():
            if ref_value and ref_value != "Unknown":
                refs_used.append(f"  - {ref_key}: {ref_value}")
        
        if refs_used:
            sections.append("## References\n" + "\n".join(refs_used))
        
        return "\n\n".join(sections) if sections else ""
    
    def _generate_script(self, message: str, head=None, meta=None, verbose=True):
        """Generate a script using the LLM with automatic schema checking."""
        # Step 1: Determine which tools/methods will be needed
        self.log.write("Step 1: Determining which methods will be needed...", verbose=verbose, tag="agent")
        required_methods = self._determine_required_methods(message, verbose)
        
        # Step 2: Get full schema for required methods
        self.log.write(f"Step 2: Fetching full schema for {len(required_methods)} method(s)...", verbose=verbose, tag="agent")
        schema_info = ""
        if required_methods:
            schema_info = self._get_schema_info_for_methods(required_methods, verbose)
        
        # Step 3: Compose well-organized message with schema information
        full_message = self._compose_log_message(message)
        
        # Add organized sections
        sections = []
        
        # Sumstats head
        if head is not None:
            sections.append("## Sumstats Preview\n" + head)
        
        # Parsed meta information
        if meta is not None:
            parsed_meta = self._parse_meta(meta)
            if parsed_meta:
                sections.append(parsed_meta)
        
        # Schema information for required methods
        if schema_info:
            sections.append("## Full Schema Information for Required Methods\n"
                          "The following methods have been identified as needed for this task. "
                          "Use the complete parameter information below to generate an accurate script:\n"
                          + schema_info)
        
        # Add all sections to message
        if sections:
            full_message += "\n\n" + "\n\n".join(sections)
        
        # Final instruction
        full_message += "\n\n## Task\n"
        full_message += "Generate a Python script to accomplish the user's request. "
        full_message += "After generating the script, ask the user if they would like to proceed with execution or if they would like to revise the plan."

        # Add to history
        self._add_to_history(full_message, PLANNER_INPUT)
        
        self.log.write("Step 3: Calling GWASLab Agent Planner to generate script...", verbose=verbose, tag="agent")
        
        # Prepare and invoke LLM
        langchain_messages = self._prepare_llm_messages()
        script_content = self._invoke_llm(langchain_messages, verbose)
        
        # Store response
        self._add_to_history(script_content, PLANNER_OUTPUT, role="assistant")
        
        return script_content
    
    def _determine_required_methods(self, message: str, verbose: bool) -> list:
        """
        Determine which methods will be needed based on the user's message.
        Uses LLM to intelligently identify required methods.
        """
        from gwaslab_agent.tools.g_tools import (
            HARMONIZER_SET, DOWNSTREAM_SET, UTILITY_SET, PLOTTER_SET, FILTERER_SET
        )
        
        all_methods = sorted(list(HARMONIZER_SET | DOWNSTREAM_SET | UTILITY_SET | PLOTTER_SET | FILTERER_SET))
        
        # First, try simple extraction from message
        mentioned = self._extract_mentioned_methods(message)
        
        # If we found methods, use them
        if mentioned:
            self.log.write(f"  - Found {len(mentioned)} method(s) mentioned in message: {', '.join(mentioned)}", verbose=verbose, tag="agent")
            return mentioned
        
        # Otherwise, use LLM to determine required methods
        if self.llm is None:
            return []
        
        self.log.write("  - No methods explicitly mentioned, using LLM to determine required methods...", verbose=verbose, tag="agent")
        
        # Create a prompt to identify required methods
        method_list = "\n".join([f"- {m}" for m in all_methods])
        prompt = _build_required_methods_prompt(method_list, message)

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse the response
            if "none" in response_text.lower():
                return []
            
            # Extract method names
            identified = []
            response_lower = response_text.lower()
            for method in all_methods:
                if method.lower() in response_lower:
                    identified.append(method)
            
            if identified:
                self.log.write(f"  - LLM identified {len(identified)} method(s): {', '.join(identified)}", verbose=verbose, tag="agent")
            else:
                self.log.write("  - LLM did not identify specific methods", verbose=verbose, tag="agent")
            
            return identified
        except Exception as e:
            self.log.write(f"  - Error determining methods: {str(e)}", verbose=verbose, tag="agent")
            return []
    
    def _extract_mentioned_methods(self, text: str) -> list:
        """Extract method names mentioned in the text that are in the tool sets."""
        import re
        from gwaslab_agent.tools.g_tools import (
            HARMONIZER_SET, DOWNSTREAM_SET, UTILITY_SET, PLOTTER_SET, FILTERER_SET
        )
        
        all_methods = HARMONIZER_SET | DOWNSTREAM_SET | UTILITY_SET | PLOTTER_SET | FILTERER_SET
        mentioned = set()
        
        text_lower = text.lower()
        
        # Check for method names in various patterns
        for method in all_methods:
            method_lower = method.lower()
            # Pattern 1: method_name( or method_name()
            if re.search(rf'\b{re.escape(method_lower)}\s*\(', text_lower):
                mentioned.add(method)
            # Pattern 2: .method_name( (method call)
            elif re.search(rf'\.{re.escape(method_lower)}\s*\(', text_lower):
                mentioned.add(method)
            # Pattern 3: "method_name" or 'method_name' (quoted)
            elif re.search(rf'["\']{re.escape(method_lower)}["\']', text_lower):
                mentioned.add(method)
            # Pattern 4: method_name as a word (with word boundaries)
            elif re.search(rf'\b{re.escape(method_lower)}\b', text_lower):
                # Only add if it's not part of another word
                mentioned.add(method)
        
        return sorted(list(mentioned))
    
    def _get_schema_info_for_methods(self, method_names: list, verbose: bool) -> str:
        """Get formatted schema information for a list of methods with complete argument details."""
        if not method_names:
            return ""
        
        # Get full schemas
        schemas = self.check_full_schema(method_names)
        
        # Format the schema information
        lines = []
        for method_name in method_names:
            if method_name not in schemas:
                self.log.write(f"  - Method '{method_name}' not in schemas dict", verbose=verbose, tag="agent")
                continue
            
            schema = schemas[method_name]
            if isinstance(schema, dict) and schema.get("description", "").startswith("Tool '"):
                # Tool not found, skip
                self.log.write(f"  - Tool '{method_name}' not found", verbose=verbose, tag="agent")
                continue
            
            lines.append(f"\n### {method_name}")
            lines.append(f"**Description**: {schema.get('description', 'No description available')}")
            
            # Add return type information if available
            returns_info = schema.get("returns")
            if returns_info:
                return_type = returns_info.get("type", "object")
                return_desc = returns_info.get("description", "")
                if return_desc:
                    # Use full description (preserve multi-line formatting)
                    # Replace newlines with spaces for single-line display, but keep all content
                    desc_full = " ".join(line.strip() for line in return_desc.split('\n') if line.strip())
                    if desc_full:
                        lines.append(f"**Returns**: `{return_type}` - {desc_full}")
                    else:
                        lines.append(f"**Returns**: `{return_type}`")
                else:
                    lines.append(f"**Returns**: `{return_type}`")
            
            args = schema.get("args", {})
            
            if isinstance(args, dict):
                # Check if args is already a properties dict (old format) or has properties key (new format)
                if "properties" in args:
                    # New format: args = {"type": "object", "properties": {...}, "required": [...]}
                    properties = args.get("properties", {})
                    required = args.get("required", [])
                else:
                    # Old format: args is directly the properties dict
                    # This happens when cached schema was stored in the old format
                    properties = args
                    required = []
                
                if properties:
                    lines.append("\n**Complete Parameter Information:**")
                    for param_name, param_info in properties.items():
                        if not isinstance(param_info, dict):
                            continue
                        
                        # Build comprehensive parameter description
                        param_parts = [f"`{param_name}`"]
                        
                        # Type information
                        param_type = param_info.get("type", "")
                        if param_type:
                            if isinstance(param_type, list):
                                param_parts.append(f"({', '.join(param_type)})")
                            else:
                                param_parts.append(f"({param_type})")
                        
                        # Required flag
                        if param_name in required:
                            param_parts.append("**[required]**")
                        else:
                            param_parts.append("[optional]")
                        
                        # Default value
                        param_default = param_info.get("default")
                        if param_default is not None:
                            param_parts.append(f"default={repr(param_default)}")
                        
                        # Enum/choices
                        param_enum = param_info.get("enum")
                        if param_enum:
                            enum_str = ", ".join(repr(e) for e in param_enum)
                            param_parts.append(f"choices=[{enum_str}]")
                        
                        # Additional constraints
                        if "minimum" in param_info:
                            param_parts.append(f"min={param_info['minimum']}")
                        if "maximum" in param_info:
                            param_parts.append(f"max={param_info['maximum']}")
                        if "minLength" in param_info:
                            param_parts.append(f"min_length={param_info['minLength']}")
                        if "maxLength" in param_info:
                            param_parts.append(f"max_length={param_info['maxLength']}")
                        if "format" in param_info:
                            param_parts.append(f"format={param_info['format']}")
                        if "pattern" in param_info:
                            param_parts.append(f"pattern={repr(param_info['pattern'])}")
                        
                        # Description
                        param_desc = param_info.get("description", "")
                        if param_desc:
                            param_parts.append(f"- {param_desc}")
                        
                        # Format as bullet point
                        param_line = "  - " + " ".join(param_parts)
                        lines.append(param_line)
                else:
                    lines.append("\n**Parameters:** None (method accepts only **kwargs)")
                
                # Add internal function schemas if available (for all-in-one functions)
                if "internal_functions" in args:
                    internal_functions = args.get("internal_functions", {})
                    if internal_functions:
                        lines.append("\n**Internal Functions (included in this all-in-one function):**")
                        for internal_func_name, internal_func_schema in internal_functions.items():
                            lines.append(f"\n  - **{internal_func_name}**:")
                            internal_props = internal_func_schema.get("properties", {})
                            internal_required = internal_func_schema.get("required", [])
                            if internal_props:
                                for param_name, param_info in list(internal_props.items())[:5]:  # Show first 5 params
                                    if isinstance(param_info, dict):
                                        param_parts = [f"`{param_name}`"]
                                        param_type = param_info.get("type", "")
                                        if param_type:
                                            param_parts.append(f"({param_type})")
                                        if param_name in internal_required:
                                            param_parts.append("[required]")
                                        else:
                                            param_parts.append("[optional]")
                                        param_default = param_info.get("default")
                                        if param_default is not None:
                                            param_parts.append(f"default={repr(param_default)}")
                                        lines.append(f"    - {' '.join(param_parts)}")
                                if len(internal_props) > 5:
                                    lines.append(f"    - ... and {len(internal_props) - 5} more parameters")
                            else:
                                lines.append(f"    - No parameters")
            else:
                lines.append("\n**Parameters:** Schema information not available")
        
        if not lines:
            return ""
        
        return "\n".join(lines)
    
    def _add_to_history(self, content, stage, role="user"):
        """Add message to history and archive.
        
        This method overrides BaseAgent._add_to_history() to support
        the Planner-specific signature (content, stage, role).
        """
        message = {
            "role": role,
            "stage": stage,
            "gwaslab_agent": "Planner",
            "content": content
        }
        # Call BaseAgent's _add_to_history with the constructed message
        super()._add_to_history(message)
    
    def _prepare_llm_messages(self, max_history=8):
        """Prepare messages for LLM in LangChain format."""
        langchain_messages = [SystemMessage(content=self._get_system_prompt())]
        
        # Limit history to save tokens
        recent_history = self.history[-max_history:] if len(self.history) > max_history else self.history
        
        for msg in recent_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
        
        return langchain_messages
    
    def _invoke_llm(self, messages, verbose):
        """Invoke LLM and track token usage."""
        if self.llm is None:
            return "# Error: LLM not initialized"
        
        response = self.llm.invoke(messages)
        script_content = response.content if hasattr(response, 'content') else str(response)
        
        # Track token usage
        try:
            from gwaslab_agent.core.g_llm import extract_token_usage, accumulate_token_usage
            usage = extract_token_usage(response)
            if usage:
                self.log.write(
                    f"[USAGE] This call: prompt={usage['input']}, completion={usage['output']}, "
                    f"total={usage.get('total', usage['input']+usage['output'])}",
                    verbose=verbose,
                    tag="agent"
                )
                if hasattr(self, "token_count") and isinstance(self.token_count, dict):
                    accumulate_token_usage(self.token_count, usage)
        except Exception:
            pass
        
        return script_content
    
    # ============================================================================
    # Script Validation
    # ============================================================================
    
    def _validate_script(self, script: str) -> dict:
        """
        Validate generated script for common mistakes and best practices.
        
        This method performs comprehensive validation of the generated Python script,
        checking for proper method usage, assignment patterns, and common errors.
        The validation is performed in multiple stages:
        
        1. **Code Extraction**: Extracts Python code from markdown code blocks
        2. **Comment Removal**: Removes comments for pattern matching while preserving structure
        3. **Validation Checks**: Performs multiple validation checks (see below)
        
        Validation Checks Performed:
        ----------------------------
        
        **Filtering Assignments** (`_check_filtering_assignments`):
        - Checks if filtering methods (filter_value, filter_region, filter_snp, etc.)
          are properly assigned to variables
        - These methods return new Sumstats objects, so results must be assigned
        - Exception: Chained calls are allowed (e.g., `sumstats.filter_value(...).plot_mqq(...)`)
        - Returns warnings for unassigned filtering method calls
        
        **QC Assignments** (`_check_qc_assignments`):
        - Detects incorrect assignments from QC methods (basic_check, harmonize, fix_id, etc.)
        - QC methods modify in place and return self, so assigning is unnecessary
        - Returns warnings for incorrect assignments (e.g., `x = sumstats.basic_check()`)
        
        **Utility Assignments** (`_check_utility_assignments`):
        - Checks if utility methods (get_lead, get_top, get_novel, summary, etc.)
          are properly assigned to variables
        - These methods return DataFrames or values, so results must be assigned
        - Exception: Chained calls are allowed (e.g., `sumstats.get_lead().iloc[0]`)
        - Returns warnings for unassigned utility method calls
        
        **Plot Modes** (`_check_plot_modes`):
        - Validates plot_mqq mode parameter values
        - Valid modes: 'm' (Manhattan), 'qq' (QQ plot), 'mqq' (both), 'r' (regional), 'b' (density)
        - Returns errors for invalid mode values
        
        **Filter Chains** (`_check_filter_chains`):
        - Warns about excessive filter chaining (>3 operations)
        - Suggests assigning intermediate results for better readability
        - Returns warnings for long chains
        
        **Harmonize Usage** (`_check_harmonize_usage`):
        - Warns if harmonize() is called without explicit user request
        - harmonize() requires reference files and should only be called when explicitly requested
        - Returns warnings for potentially unnecessary harmonize() calls
        
        **Redundant QC Calls** (`_check_redundant_qc_calls`):
        - Detects if individual QC functions are called after basic_check()
        - Functions checked: fix_id, fix_chr, fix_pos, fix_allele, check_sanity,
          check_data_consistency, normalize_allele, remove_dup, sort_coordinate, sort_column
        - These functions are already included in basic_check(), so calling them separately
          after basic_check() is redundant
        - Returns warnings for redundant calls
        - Note: These warnings trigger auto-replanning in the main workflow
        
        Parameters
        ----------
        script : str
            The generated Python script (may include markdown formatting)
        
        Returns
        -------
        dict
            Validation result dictionary with:
            - 'valid' (bool): True if no errors found, False otherwise
            - 'warnings' (list): List of warning messages about potential issues
            - 'errors' (list): List of error messages about critical issues
            
        Note
        ----
        Warnings do not prevent script execution but indicate potential issues.
        Errors indicate critical problems that should be fixed before execution.
        Redundant QC call warnings trigger automatic replanning in the main workflow.
        """
        code = self._extract_python_code(script)
        code_no_comments = self._remove_comments(code)
        
        warnings = []
        errors = []
        
        warnings.extend(self._check_filtering_assignments(code, code_no_comments))
        warnings.extend(self._check_qc_assignments(code_no_comments))
        warnings.extend(self._check_utility_assignments(code, code_no_comments))
        errors.extend(self._check_plot_modes(code_no_comments))
        warnings.extend(self._check_filter_chains(code_no_comments))
        warnings.extend(self._check_harmonize_usage(code_no_comments))
        warnings.extend(self._check_redundant_qc_calls(code_no_comments))
        
        return {
            'valid': len(errors) == 0,
            'warnings': warnings,
            'errors': errors
        }
    
    def _extract_python_code(self, text: str) -> str:
        """Extract Python code from markdown code blocks."""
        import re
        python_block_pattern = r"```(?:python)?\s*(.*?)```"
        match = re.search(python_block_pattern, text, re.DOTALL)
        return match.group(1).strip() if match else text.strip()
    
    def _remove_comments(self, code):
        """Remove comments from code while preserving line structure."""
        lines = code.split('\n')
        return '\n'.join([line.split('#')[0] if '#' in line else line for line in lines])
    
    def _check_filtering_assignments(self, code_with_comments, code_no_comments):
        """Check if filtering methods are properly assigned."""
        import re
        from gwaslab_agent.tools.g_tools import FILTERER_SET
        
        warnings = []
        filter_pattern = r'\.(filter_value|filter_region|filter_snp|filter_indel|filter_palindromic|exclude_hla|search)\s*\('
        
        for match in re.finditer(filter_pattern, code_no_comments):
            line_start = code_no_comments.rfind('\n', 0, match.start()) + 1
            line_end = code_no_comments.find('\n', match.end())
            if line_end == -1:
                line_end = len(code_no_comments)
            line = code_no_comments[line_start:line_end].strip()
            
            # Skip if chained call
            remaining_line = code_no_comments[match.end():line_end]
            has_chained_call = re.search(r'\)\s*\.(filter_|plot_|get_)', remaining_line)
            
            # Check if assigned
            if not re.match(r'^\s*\w+\s*=', line) and not has_chained_call:
                method_name = match.group(1)
                if 'inplace=True' not in line:
                    orig_line = self._get_original_line(code_with_comments, match.start())
                    warnings.append(
                        f"Line with {method_name}(): '{orig_line[:60]}...' - "
                        f"{method_name}() returns a new Sumstats object. "
                        f"Consider assigning: `filtered = sumstats.{method_name}(...)`"
                    )
        
        return warnings
    
    def _check_qc_assignments(self, code_no_comments):
        """Check if QC methods are incorrectly assigned."""
        import re
        
        warnings = []
        qc_pattern = r'(\w+)\s*=\s*sumstats\.(basic_check|harmonize|fix_id|fix_chr|fix_pos|fix_allele|remove_dup|normalize_allele|sort_coordinate|sort_column)\s*\('
        
        for match in re.finditer(qc_pattern, code_no_comments):
            var_name = match.group(1)
            method_name = match.group(2)
            warnings.append(
                f"Variable '{var_name}' assigned from {method_name}(). "
                f"QC methods modify in place and return None. Remove the assignment: `sumstats.{method_name}()`"
            )
        
        return warnings
    
    def _check_utility_assignments(self, code_with_comments, code_no_comments):
        """Check if utility methods are properly assigned."""
        import re
        
        warnings = []
        utility_pattern = r'\.(get_lead|get_top|get_novel|get_associations|summary|check_sumstats_qc_status)\s*\('
        
        for match in re.finditer(utility_pattern, code_no_comments):
            line_start = code_no_comments.rfind('\n', 0, match.start()) + 1
            line_end = code_no_comments.find('\n', match.end())
            if line_end == -1:
                line_end = len(code_no_comments)
            line = code_no_comments[line_start:line_end].strip()
            
            # Skip if chained call
            remaining_line = code_no_comments[match.end():line_end]
            has_chained_call = re.search(r'\)\s*\.(iloc|loc|query|head|tail|tolist)', remaining_line)
            
            # Check if assigned
            if not re.match(r'^\s*\w+\s*=', line) and not has_chained_call:
                method_name = match.group(1)
                orig_line = self._get_original_line(code_with_comments, match.start())
                warnings.append(
                    f"Line with {method_name}(): '{orig_line[:60]}...' - "
                    f"{method_name}() returns a DataFrame/value. "
                    f"Consider assigning: `result = sumstats.{method_name}(...)`"
                )
        
        return warnings
    
    def _check_plot_modes(self, code_no_comments):
        """Check for invalid plot modes."""
        import re
        
        errors = []
        plot_mode_pattern = r'plot_mqq\s*\([^)]*mode\s*=\s*["\']([^"\']+)["\']'
        valid_modes = {'m', 'qq', 'mqq', 'r', 'b'}
        
        for match in re.finditer(plot_mode_pattern, code_no_comments):
            mode = match.group(1)
            if mode not in valid_modes:
                errors.append(
                    f"Invalid plot_mqq mode: '{mode}'. Valid modes are: {', '.join(sorted(valid_modes))}"
                )
        
        return errors
    
    def _check_filter_chains(self, code_no_comments):
        """Check for excessive filter chaining."""
        import re
        
        warnings = []
        filter_chain_pattern = r'\.(filter_value|filter_region|filter_snp)\s*\([^)]*\)\s*\.(filter_|plot_|get_)'
        chain_matches = list(re.finditer(filter_chain_pattern, code_no_comments))
        
        if len(chain_matches) > 3:
            warnings.append(
                "Multiple chained filtering operations detected (>3). Consider assigning intermediate results "
                "for better readability: `filtered = sumstats.filter_value(...)`"
            )
        
        return warnings
    
    def _check_harmonize_usage(self, code_no_comments):
        """Check if harmonize() is called and warn that it should only be called if explicitly requested."""
        import re
        
        warnings = []
        # Pattern to match harmonize() calls
        harmonize_pattern = r'\.harmonize\s*\('
        
        matches = list(re.finditer(harmonize_pattern, code_no_comments))
        if matches:
            for match in matches:
                line_start = code_no_comments.rfind('\n', 0, match.start()) + 1
                line_end = code_no_comments.find('\n', match.end())
                if line_end == -1:
                    line_end = len(code_no_comments)
                line = code_no_comments[line_start:line_end].strip()
                
                warnings.append(
                    f"⚠️  WARNING: `harmonize()` is called in the script. "
                    f"`harmonize()` should ONLY be called if the user explicitly requests harmonization, "
                    f"allele alignment/flipping, reference-based annotation, strand inference, or rsID assignment. "
                    f"If the user only requested basic QC, use `basic_check()` instead. "
                    f"Line: `{line[:80]}{'...' if len(line) > 80 else ''}`"
                )
        
        return warnings
    
    def _check_redundant_qc_calls(self, code_no_comments):
        """
        Check if individual QC functions are called after basic_check() has been called.
        
        Returns:
            list: List of warning messages about redundant calls
        """
        import re
        
        warnings = []
        
        # Functions that are included in basic_check()
        basic_check_includes = {
            'fix_id', 'fix_chr', 'fix_pos', 'fix_allele',
            'check_sanity', 'check_data_consistency',
            'normalize_allele', 'remove_dup',
            'sort_coordinate', 'sort_column'
        }
        
        # Find all basic_check() calls
        basic_check_pattern = r'\.basic_check\s*\('
        basic_check_matches = list(re.finditer(basic_check_pattern, code_no_comments))
        
        if not basic_check_matches:
            return warnings  # No basic_check() called, so no redundancy to check
        
        # Find positions of basic_check() calls
        basic_check_positions = [m.start() for m in basic_check_matches]
        
        # Check for individual QC function calls after basic_check()
        for func_name in basic_check_includes:
            func_pattern = rf'\.{re.escape(func_name)}\s*\('
            func_matches = list(re.finditer(func_pattern, code_no_comments))
            
            for func_match in func_matches:
                func_pos = func_match.start()
                
                # Check if this function call appears after any basic_check() call
                for bc_pos in basic_check_positions:
                    if func_pos > bc_pos:
                        # Found a redundant call
                        line_start = code_no_comments.rfind('\n', 0, func_match.start()) + 1
                        line_end = code_no_comments.find('\n', func_match.end())
                        if line_end == -1:
                            line_end = len(code_no_comments)
                        line = code_no_comments[line_start:line_end].strip()
                        
                        warnings.append(
                            f"⚠️  REDUNDANT: `{func_name}()` is called after `basic_check()` has been called. "
                            f"`{func_name}()` is already included in `basic_check()`, so calling it again is redundant. "
                            f"Remove this call or remove `basic_check()` if you only need `{func_name}()`. "
                            f"Line: `{line[:80]}{'...' if len(line) > 80 else ''}`"
                        )
                        break  # Only warn once per function call
        
        return warnings
    
    def _detect_redundant_calls_for_replanning(self, code_no_comments):
        """
        Detect redundant QC calls that should trigger auto-replanning.
        
        Returns:
            dict: Information about redundant calls with:
                - 'has_redundant': bool - Whether redundant calls were detected
                - 'redundant_functions': set - Set of redundant function names
                - 'message': str - Message describing the redundancies
        """
        import re
        
        result = {
            'has_redundant': False,
            'redundant_functions': set(),
            'message': ''
        }
        
        # Functions that are included in basic_check()
        basic_check_includes = {
            'fix_id', 'fix_chr', 'fix_pos', 'fix_allele',
            'check_sanity', 'check_data_consistency',
            'normalize_allele', 'remove_dup',
            'sort_coordinate', 'sort_column'
        }
        
        # Find all basic_check() calls
        basic_check_pattern = r'\.basic_check\s*\('
        basic_check_matches = list(re.finditer(basic_check_pattern, code_no_comments))
        
        if not basic_check_matches:
            return result  # No basic_check() called, so no redundancy to check
        
        # Find positions of basic_check() calls
        basic_check_positions = [m.start() for m in basic_check_matches]
        
        # Check for individual QC function calls after basic_check()
        for func_name in basic_check_includes:
            func_pattern = rf'\.{re.escape(func_name)}\s*\('
            func_matches = list(re.finditer(func_pattern, code_no_comments))
            
            for func_match in func_matches:
                func_pos = func_match.start()
                
                # Check if this function call appears after any basic_check() call
                is_redundant = False
                for bc_pos in basic_check_positions:
                    if func_pos > bc_pos:
                        result['has_redundant'] = True
                        result['redundant_functions'].add(func_name)
                        is_redundant = True
                        break  # Found one redundant call for this function, no need to check more bc_pos
                
                if is_redundant:
                    break  # Found redundant call for this function, no need to check more func_matches
        
        # Build message if redundancies found
        if result['has_redundant']:
            func_list = sorted(list(result['redundant_functions']))
            if len(func_list) == 1:
                result['message'] = (
                    f"The script calls `{func_list[0]}()` after `basic_check()`, which is redundant. "
                    f"`{func_list[0]}()` is already included in `basic_check()`. "
                    f"Please remove the redundant `{func_list[0]}()` call."
                )
            else:
                func_names = ', '.join([f"`{f}()`" for f in func_list[:-1]]) + f", and `{func_list[-1]}()`"
                result['message'] = (
                    f"The script calls {func_names} after `basic_check()`, which is redundant. "
                    f"These functions are already included in `basic_check()`. "
                    f"Please remove these redundant calls."
                )
        
        return result
    
    def _generate_replanning_prompt_for_redundancy(self, original_message, redundant_info):
        """
        Generate a replanning prompt to fix redundant function calls.
        
        Parameters
        ----------
        original_message : str
            The original user message
        redundant_info : dict
            Information about redundant calls from _detect_redundant_calls_for_replanning
        
        Returns
        -------
        str
            Prompt for replanning that addresses the redundancies
        """
        redundant_functions = sorted(list(redundant_info['redundant_functions']))
        func_list_str = ', '.join([f"`{f}()`" for f in redundant_functions])
        
        return _build_replanning_prompt_for_redundancy(original_message, func_list_str)
    
    def _get_original_line(self, code_with_comments, position):
        """Get original line (with comments) at given position."""
        lines = code_with_comments.split('\n')
        line_num = code_with_comments[:position].count('\n')
        return lines[line_num].strip() if line_num < len(lines) else ""
    
    # ============================================================================
    # User Interaction
    # ============================================================================
    
    def _check_user_confirmation(self, user_input: str):
        """
        Check if user input indicates confirmation or revision request.
        
        Returns:
            (is_confirmed, is_revision): Tuple indicating if user confirmed or wants revision
        """
        user_lower = user_input.strip().lower()
        
        confirm_keywords = ['yes', 'y', 'proceed', 'execute', 'confirm', 'ok', 'okay', 'go', 'run', 'plan_confirmed']
        revision_keywords = ['no', 'n', 'revise', 'change', 'modify', 'update', 'different', 'edit', 'fix', 'adjust']
        
        is_confirmed = any(keyword in user_lower for keyword in confirm_keywords)
        is_revision = any(keyword in user_lower for keyword in revision_keywords)
        
        return is_confirmed, is_revision
    
    def _display_script_and_validation(self, script_content, validation_result, if_print):
        """Display script and validation results."""
        print_llm_output(console, script_content, title="PLANNER", if_print=if_print)
        
        if validation_result['warnings'] or validation_result['errors']:
            console.print()
            if validation_result['errors']:
                print_status(console, "Script Validation - Errors Found:", "error")
                for error in validation_result['errors']:
                    console.print(f"  ❌ {error}")
            if validation_result['warnings']:
                print_status(console, "Script Validation - Warnings:", "warning")
                for warning in validation_result['warnings'][:5]:
                    console.print(f"  ⚠️  {warning}")
                if len(validation_result['warnings']) > 5:
                    console.print(f"  ... and {len(validation_result['warnings']) - 5} more warnings")
            console.print()
    
    def _handle_revision_request(self, user_response, head, meta, verbose):
        """Handle user's revision request."""
        revision_prompt = _build_revision_prompt(user_response)
        
        self._add_to_history(revision_prompt, PLANNER_INPUT)
        script_content = self._generate_script(revision_prompt, head=head, meta=meta, verbose=verbose)
        return script_content
    
    # ============================================================================
    # Main Run Method
    # ============================================================================
    
    def run(self, message: str, 
            verbose=True, 
            return_message=True, 
            verbose_return=False, 
            message_to_return=None,
            head=None,
            meta=None,
            if_print=True,
            yes=False):
        """
        Run the planner to generate a Python script with confirmation loop.
        
        This is the main entry point for the Planner. It orchestrates the complete
        workflow from script generation through validation, auto-replanning, and user confirmation.
        
        Workflow Steps:
        --------------
        
        1. **Initial Script Generation**
           - Determines required methods from user message
           - Fetches complete schemas for required methods
           - Composes comprehensive prompt with context (QC status, log, variables, etc.)
           - Invokes LLM to generate Python script
        
        2. **Initial Validation**
           - Validates the generated script for common mistakes
           - Checks assignment patterns, method usage, plot modes, etc.
           - See `_validate_script()` for detailed validation checks
        
        3. **Auto-Replanning for Redundancies**
           - Detects redundant QC function calls (e.g., fix_id() after basic_check())
           - If redundancies detected:
             * Generates replanning prompt explaining the issue
             * Regenerates script with instructions to remove redundancies
             * Validates the new script
             * Repeats up to 2 times if redundancies persist
           - This happens automatically before user sees the script
        
        4. **Re-Validation**
           - Re-validates script after auto-replanning
           - Ensures auto-replanning fixed the issues
        
        5. **User Confirmation Loop**
           - Displays script and validation results (warnings/errors)
           - Prompts user to confirm execution or request revisions
           - If user requests revision:
             * Generates new script incorporating feedback
             * Re-validates the new script
             * Returns to confirmation loop
           - Continues until user confirms or max iterations (10) reached
        
        6. **Token Usage Tracking**
           - Tracks and logs total token usage for the run
        
        Parameters
        ----------
        message : str
            User's request/instruction for what the script should do
        verbose : bool, default True
            Whether to print verbose logging
        return_message : bool, default True
            Whether to return the generated script content
        verbose_return : bool, default False
            Unused parameter (for BaseAgent interface compatibility)
        message_to_return : optional
            Unused parameter (for BaseAgent interface compatibility)
        head : optional
            Preview of sumstats DataFrame (first few rows) to include in prompt
        meta : optional
            Metadata dictionary with QC status, references, etc. to include in prompt
        if_print : bool, default True
            Whether to print the script and validation results
        yes : bool, default False
            If True, skip user confirmation and proceed automatically
        
        Returns
        -------
        str or None
            The generated Python script content if return_message=True, None otherwise
        
        Note
        ----
        This method implements the BaseAgent.run() interface.
        The script generation process is fully automated with auto-replanning,
        but user confirmation is required before execution (unless yes=True).
        """
        # Track token usage
        from gwaslab_agent.core.g_llm import snapshot_counters, log_run_totals
        _start = snapshot_counters(self.token_count) if hasattr(self, 'token_count') else (0, 0, 0)
        
        # ========================================================================
        # Workflow Execution (following graph structure - see _get_workflow_graph())
        # ========================================================================
        # Stage 1: script_generation → Generate initial Python script
        script_content = self._generate_script(message, head=head, meta=meta, verbose=verbose)
        
        # Stage 2: initial_validation → Validate script for common mistakes
        validation_result = self._validate_script(script_content)
        
        # Stage 3: redundancy_check → Check for redundant QC function calls
        code = self._extract_python_code(script_content)
        code_no_comments = self._remove_comments(code)
        redundant_info = self._detect_redundant_calls_for_replanning(code_no_comments)
        
        if redundant_info['has_redundant']:
            # Stage 4: auto_replan → Auto-replan to fix redundant calls (max 2 attempts)
            script_content = self._auto_replan_if_redundant(script_content, message, head, meta, verbose)
            if script_content:
                # Stage 5: re_validation → Re-validate script after auto-replanning
                validation_result = self._validate_script(script_content)
        
        # Stage 6: user_confirmation → User confirmation loop (includes display_script, user_input, handle_revision, final_validation)
        script_content = self._confirmation_loop(
            script_content, validation_result, head, meta, verbose, if_print, yes=yes
        )
        
        # Log total token usage
        if hasattr(self, 'token_count'):
            _end = snapshot_counters(self.token_count)
            log_run_totals(self.log, "planner_run", _start, _end, verbose=verbose)
        
        return script_content if return_message else None
    
    def _auto_replan_if_redundant(self, script_content, original_message, head, meta, verbose, max_auto_replan_attempts=2):
        """
        Automatically replan the script if redundant function calls are detected.
        
        Parameters
        ----------
        script_content : str
            The current script content
        original_message : str
            The original user message
        head : optional
            Sumstats head preview
        meta : optional
            Metadata
        verbose : bool
            Verbose flag
        max_auto_replan_attempts : int
            Maximum number of auto-replanning attempts (default: 2)
        
        Returns
        -------
        str
            The script content (either original or replanned)
        """
        code = self._extract_python_code(script_content)
        code_no_comments = self._remove_comments(code)
        
        # Check for redundant QC calls
        redundant_info = self._detect_redundant_calls_for_replanning(code_no_comments)
        
        if not redundant_info['has_redundant']:
            return script_content  # No redundancies, return original script
        
        # Log that we're auto-replanning
        self.log.write(
            f"Auto-replanning: Redundant function calls detected: {', '.join(redundant_info['redundant_functions'])}",
            verbose=verbose,
            tag="agent"
        )
        
        # Attempt to fix redundancies through replanning
        for attempt in range(1, max_auto_replan_attempts + 1):
            self.log.write(f"Auto-replanning attempt {attempt}/{max_auto_replan_attempts}...", verbose=verbose, tag="agent")
            
            # Generate replanning prompt
            replan_prompt = self._generate_replanning_prompt_for_redundancy(original_message, redundant_info)
            
            # Generate revised script
            revised_script = self._generate_script(replan_prompt, head=head, meta=meta, verbose=verbose)
            
            # Check if redundancies are fixed
            revised_code = self._extract_python_code(revised_script)
            revised_code_no_comments = self._remove_comments(revised_code)
            revised_redundant_info = self._detect_redundant_calls_for_replanning(revised_code_no_comments)
            
            if not revised_redundant_info['has_redundant']:
                self.log.write(
                    f"Auto-replanning successful: Redundant calls removed after {attempt} attempt(s)",
                    verbose=verbose,
                    tag="agent"
                )
                return revised_script
            else:
                # Still has redundancies, update info for next attempt
                redundant_info = revised_redundant_info
                script_content = revised_script
        
        # Max attempts reached, log warning but return the best attempt
        self.log.write(
            f"Auto-replanning: Maximum attempts reached. Some redundancies may remain: "
            f"{', '.join(redundant_info['redundant_functions'])}",
            verbose=verbose,
            tag="agent"
        )
        return script_content
    
    def _confirmation_loop(self, script_content, validation_result, head, meta, verbose, if_print, max_iterations=10, yes=False):
        """Handle user confirmation loop for script generation."""
        # If yes=True, skip confirmation and return immediately
        if yes:
            self._display_script_and_validation(script_content, validation_result, if_print)
            print_status(console, "Skipping confirmation (yes=True). Proceeding to validation and execution...", "success")
            console.print()
            return script_content
        
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Display script and validation
            self._display_script_and_validation(script_content, validation_result, if_print)
            
            # Prompt user
            print_status(console, "Would you like to proceed with execution, or would you like to revise the plan?", "info")
            console.print("[dim]You can say 'yes'/'proceed' to confirm, or describe what you'd like to change.[/dim]")
            
            try:
                user_response = input("\nYour response: ").strip()
                
                if not user_response:
                    print_status(console, "Please provide a response. Type 'yes' to confirm or describe changes you'd like.", "warning")
                    continue
                
                is_confirmed, is_revision = self._check_user_confirmation(user_response)
                
                if is_confirmed:
                    print_status(console, "Plan confirmed. Proceeding to validation and execution...", "success")
                    console.print()
                    return script_content
                
                elif is_revision or (not is_confirmed and not is_revision):
                    # Generate revised script
                    script_content = self._handle_revision_request(user_response, head, meta, verbose)
                    validation_result = self._validate_script(script_content)
                    # Loop will continue to display revised script
                    
            except (EOFError, KeyboardInterrupt):
                console.print()
                print_status(console, "Plan confirmation cancelled (interrupted).", "error")
                console.print()
                return None
        
        # Max iterations reached
        print_status(console, "Maximum confirmation iterations reached. Proceeding with current plan.", "warning")
        console.print()
        return script_content


# ================================
# Prompt Templates
# ================================

def _build_required_methods_prompt(method_list: str, message: str) -> str:
    """Build prompt for determining required methods from user message.
    
    Args:
        method_list: Formatted list of available methods
        message: User request message
        
    Returns:
        Formatted prompt string
    """
    return f"""Based on the user's request below, identify which GWASLab methods will be needed to accomplish the task.

Available methods:
{method_list}

User request:
{message}

Respond with ONLY a comma-separated list of method names (e.g., "filter_value, plot_mqq, get_lead").
If no specific methods are needed, respond with "none"."""


def _build_replanning_prompt_for_redundancy(original_message: str, func_list_str: str) -> str:
    """Build prompt for replanning to fix redundant function calls.
    
    Args:
        original_message: Original user request message
        func_list_str: Formatted string of redundant function names
        
    Returns:
        Formatted prompt string
    """
    return (
        f"Original user request: {original_message}\n\n"
        f"IMPORTANT: The previously generated script had redundant function calls that need to be fixed.\n\n"
        f"Problem: The script called {func_list_str} after `basic_check()` was called. "
        f"These functions are already included in `basic_check()`, so calling them separately is redundant.\n\n"
        f"Please regenerate the script to:\n"
        f"1. Keep `basic_check()` if it's needed\n"
        f"2. Remove the redundant calls to {func_list_str}\n"
        f"3. Only call individual QC functions if `basic_check()` is NOT being used\n\n"
        f"Generate a corrected Python script that avoids these redundancies."
    )


def _build_revision_prompt(user_response: str) -> str:
    """Build prompt for handling user revision requests.
    
    Args:
        user_response: User's feedback/request for revision
        
    Returns:
        Formatted prompt string
    """
    return (
        f"The user would like to revise the plan. Their feedback: {user_response}\n\n"
        "Please generate a revised Python script incorporating their feedback."
    )


def _build_system_prompt_base() -> str:
    """Build base system prompt for direct script generation.
    
    Returns:
        Base system prompt string
    """
    return """You generate executable Python scripts for GWASLab. The `sumstats` object is already loaded - do NOT include data loading or imports.

## Key Rules
- Use `sumstats` directly (already loaded)
- Registered objects accessible: `subset_0`, `subset_1`, `df_0`, `df_1`, etc.
- New objects auto-registered for subsequent scripts
- Use GWASLab methods directly (no tool calls)

## Critical Warnings

**DO NOT add extra steps unless user explicitly requests them.** Only include operations the user 
specifically asks for. Do not automatically add QC, filtering, or other processing steps.

**DO NOT call `harmonize()` unless user explicitly requests it.** Only call when user asks for:
harmonization, allele alignment, reference-based annotation, strand inference, or rsID assignment.

**DO NOT call individual QC functions after `basic_check()`.** `basic_check()` includes:
`fix_id`, `fix_chr`, `fix_pos`, `fix_allele`, `check_sanity`, `check_data_consistency`, 
`normalize_allele`, `remove_dup`, `sort_coordinate`, `sort_column`. Only call individual 
functions if you need them WITHOUT running the full `basic_check()` pipeline.

## Method Return Types

Return information is parsed from docstrings when available. Fallback rules:

### Filtering Methods → Return NEW Sumstats objects
All `filter_*` methods, `exclude_hla`, `search`, `random_variants` return new objects when `inplace=False` (default).
**ALWAYS assign**: `filtered = sumstats.filter_value(expr="P<5e-8")`

### QC Methods → Modify in place (return self)
All QC methods modify in place and return `self`:
- **All-in-one**: `basic_check()`, `harmonize()`
- **Individual**: `fix_id`, `fix_chr`, `fix_pos`, `fix_allele`, `remove_dup`, `normalize_allele`, 
  `sort_coordinate`, `sort_column`, `check_sanity`, `check_data_consistency`, `assign_rsid`, 
  `assign_rsid2`, `infer_af`, `check_af`, `flip_allele_stats`, `flip_snpid`, `infer_strand`, 
  `infer_strand2`, `liftover`, `strip_snpid`, `set_build`

**DO NOT assign results**: `sumstats.basic_check()` (NOT `filtered = sumstats.basic_check()`)

### Plotting Methods → Return figure objects
- `plot_mqq(build=None, mode='mqq', **kwargs)` → Returns matplotlib figure
Can assign or ignore: `fig = sumstats.plot_mqq(mode='m')` or `sumstats.plot_mqq(mode='m')`

### Utility Methods → Return DataFrames/values
- `get_lead(gls=False)`, `get_top(gls=False)` → DataFrame (or Sumstats if gls=True)
- `get_novel`, `get_associations`, `get_proxy`, `get_density`, `fill_data`, `get_ess`, 
  `get_gc`, `get_per_snp_r2`, `get_region_start_and_end`, `view_sumstats`, `to_format` → DataFrame/values
- `summary`, `check_sumstats_qc_status`, `infer_ancestry`, `infer_build`, `lookup_status` → dict/string
**ALWAYS assign**: `leads_df = sumstats.get_lead()`

### Downstream Methods
- `estimate_h2_by_ldsc`, `estimate_partitioned_h2_by_ldsc`, `estimate_h2_cts_by_ldsc` → Returns dict/results
- `clump` → Modifies in place (stores in self.clumps), returns None

## Common Parameters

- `inplace=False` (filtering): Default returns new object. Always assign when False.
- `build=None` (plotting/utility): Default uses `sumstats.build`. Only specify if different.
- `mode` (plot_mqq): `'m'` (Manhattan), `'qq'` (QQ), `'mqq'` (both), `'r'` (regional), `'b'` (density). Default: `'mqq'`
- `verbose=True`: Controls logging output

## Workflow Examples

```python
# Basic QC and plot
sumstats.basic_check()
sumstats.plot_mqq(mode='mqq')

# Filter and plot
significant = sumstats.filter_value(expr="P<5e-8")
significant.plot_mqq(mode='m')

# Get leads and plot region
leads = sumstats.get_lead()
first_lead = leads.iloc[0]
sumstats.plot_mqq(
    mode='r',
    region=[first_lead.CHR, first_lead.POS - 500000, first_lead.POS + 500000],
    highlight=[first_lead.SNPID]
)

# Multi-step filtering
filtered = sumstats.filter_value(expr="P<1e-5")
filtered_snps = filtered.filter_snp()
filtered_snps.plot_mqq(mode='m')
```

## Common Mistakes

1. **WRONG**: `filtered = sumstats.basic_check()` - Returns self, not new object
   **CORRECT**: `sumstats.basic_check()` - Modifies in place

2. **WRONG**: `sumstats.filter_value(expr="P<5e-8")` then `sumstats.plot_mqq()` - Plots original
   **CORRECT**: `filtered = sumstats.filter_value(expr="P<5e-8")` then `filtered.plot_mqq()`

3. **WRONG**: `sumstats.get_lead()` without assignment - Result lost
   **CORRECT**: `leads = sumstats.get_lead()` then use `leads`

## DataFrame Operations
Use pandas directly: `.query()`, `.iloc[]`, `.tolist()`, `.head()`, etc.
Access columns: `leads_df.CHR`, `leads_df.POS`, `leads_df.SNPID`

## Reference Files
Use placeholders: `{REF:description}` (e.g., `{REF:LD panel for EAS hg38}`). Validator resolves automatically.

## Output
Generate complete, executable Python script. Include comments for major steps. Ensure all filtering and utility method results are assigned to variables."""


def _build_system_prompt_tool_index_section() -> str:
    """Build the tool index section for system prompt.
    
    Returns:
        Tool index section string
    """
    return """
## Verifying Method Arguments (CRITICAL - READ CAREFULLY)

**BEFORE generating any script, you MUST verify the exact argument names, types, default values, and requirements for each method you plan to use.**

The simplified method index above shows only basic descriptions. For accurate script generation, you need complete parameter information.

**Workflow for argument verification:**
1. Identify all methods you need to use in the script
2. For each method, check if you have complete argument information
3. If argument details are unclear or missing, you MUST request the full schema before proceeding
4. Only generate the script after you have verified all required arguments

**To request full schema information:**
- Ask explicitly: 'I need the full schema for [method_name]' or 'Please provide complete argument details for [method_name]'
- You can request multiple methods at once: 'I need full schemas for filter_value, plot_mqq, and harmonize'
- The full schema will include: argument names, types, default values, required parameters, enum options, and descriptions

**Common mistakes to avoid:**
- Using incorrect argument names (e.g., 'chromosome' instead of 'chr')
- Missing required arguments
- Using wrong argument types (e.g., string instead of int)
- Not checking enum values for categorical arguments

**Remember:** It is better to request schema information and generate an accurate script than to guess and produce incorrect code.
Pay attention to return types indicated in method categories above."""
