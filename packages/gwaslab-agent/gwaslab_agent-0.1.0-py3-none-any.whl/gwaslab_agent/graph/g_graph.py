from typing import TypedDict, Optional, Any, Dict
from langgraph.graph import StateGraph, START, END
import re


class GraphState(TypedDict):
    """State schema for the LangGraph workflow."""
    message: str
    original_message: str
    route: str
    mode: str
    script_instructions: Optional[str]
    summary_instructions: Optional[Dict[str, Any]]
    needs_summary: bool
    script: Optional[str]
    resolved_script: Optional[str]  # Script with placeholders resolved
    validated_script: Optional[str]
    exec_message: Optional[str]
    step_index: int
    yes: bool


def build_sumstats_graph(agent_obj):
    """
    Build a LangGraph workflow for SmartSumstats using QueryRouter.
    
    The graph flow:
    1. router_node: Interpret user message and extract instructions
    2. planner_node: Generate script using Planner with script instructions
    3. path_manager_node: Resolve {REF:...} placeholders using PathManager
    4. validator_node: Validate the script (placeholders already resolved)
    5. executor_node: Execute the validated script
    6. summarizer_node: Generate summary if needed (with summary instructions)
    """
    from langgraph.graph import StateGraph, START, END
    from gwaslab_agent.agents.a_router import QueryRouter
    
    def router_node(state: GraphState) -> GraphState:
        """Interpret user message and extract instructions for Planner and Summarizer."""
        message = state.get("message", "")
        original_message = state.get("original_message", message)
        
        # Use QueryRouter to interpret the message
        router = QueryRouter(agent_obj)
        interpretation = router.interpret(message, verbose=True)
        
        # Update state with interpretation results
        state["route"] = interpretation["route"]
        state["script_instructions"] = interpretation["script_instructions"]
        state["summary_instructions"] = interpretation["summary_instructions"]
        # Always need summary after execution (unless it's just planning)
        route = interpretation["route"]
        state["needs_summary"] = route not in ("plan", "planner", "path_manager", "loader", "summarizer")
        state["original_message"] = original_message
        
        # Set mode
        mode_mapping = {
            'plan': 'plan',
            'plan_run': 'plan_run',
            'plan_run_sum': 'plan_run_sum',
            'path_manager': 'plan_run',
            'planner': 'plan',
            'loader': 'plan_run',
            'summarizer': 'plan_run',
        }
        state["mode"] = mode_mapping.get(interpretation["route"], 'plan_run')
        agent_obj._current_mode = state["mode"]
        
        return state
    
    def planner_node(state: GraphState) -> GraphState:
        """Generate Python script using Planner with script instructions."""
        script_instructions = state.get("script_instructions", state.get("message", ""))
        yes = state.get("yes", False)
        
        # Generate script with instructions
        script = agent_obj.planner.run(
            script_instructions,
            head=agent_obj.sumstats.data.head().to_markdown() if hasattr(agent_obj.sumstats, 'data') and agent_obj.sumstats.data is not None else "",
            meta=agent_obj.sumstats.meta.get("gwaslab", {}) if hasattr(agent_obj.sumstats, 'meta') else {},
            return_message=True,
            yes=yes
        )
        
        if script is None:
            # User cancelled - set script to empty to skip execution
            agent_obj.log.write("User cancelled script generation in planner_node", verbose=True)
            state["script"] = None
            state["resolved_script"] = None
            state["validated_script"] = None
            return state
        
        # Extract Python code from markdown if needed
        from gwaslab_agent.execution.s_script_execution import extract_python_code
        extracted_script = extract_python_code(script)
        
        agent_obj.log.write(f"Planner generated script (length: {len(extracted_script)} chars)", verbose=True)
        state["script"] = extracted_script
        state["step_index"] = 0
        
        return state
    
    def path_manager_node(state: GraphState) -> GraphState:
        """Resolve {REF:...} placeholders in script using PathManager."""
        script = state.get("script")
        if script is None:
            agent_obj.log.write("No script to process in path_manager_node", verbose=True)
            state["resolved_script"] = None
            return state
        
        # Check if script contains {REF:...} placeholders
        placeholder_pattern = r'\{REF:([^}]+)\}'
        placeholders = re.findall(placeholder_pattern, script)
        
        if not placeholders:
            # No placeholders, script is already resolved
            state["resolved_script"] = script
            return state
        
        # PathManager not available
        if not hasattr(agent_obj, 'pathmanager') or agent_obj.pathmanager is None:
            agent_obj.log.write("Reference placeholders found but PathManager not available. Keeping placeholders.", verbose=True)
            state["resolved_script"] = script
            return state
        
        # Resolve each unique placeholder
        resolved_script = script
        resolved_paths = {}  # Cache resolved paths
        resolved_count = 0
        failed_placeholders = []
        
        # Process unique placeholders only
        unique_placeholders = list(set(placeholders))
        agent_obj.log.write(f"Found {len(unique_placeholders)} unique placeholder(s) to resolve", verbose=True)
        
        for placeholder_desc in unique_placeholders:
            try:
                agent_obj.log.write(f"Resolving placeholder: {placeholder_desc}", verbose=True)
                
                # Query PathManager
                query = f"Resolve reference file path for: {placeholder_desc.strip()}"
                result = agent_obj.pathmanager.run(query, verbose=False, return_message=True, if_print=False)
                
                # Extract path from result using the same logic as validator
                resolved_path = _extract_path_from_pathmanager_result(result)
                
                if resolved_path:
                    resolved_paths[placeholder_desc] = resolved_path
                    resolved_count += 1
                    agent_obj.log.write(f"Resolved {placeholder_desc} → {resolved_path}", verbose=True)
                else:
                    failed_placeholders.append(placeholder_desc)
                    agent_obj.log.write(f"Could not resolve placeholder: {placeholder_desc}", verbose=True)
                    
            except Exception as e:
                failed_placeholders.append(placeholder_desc)
                agent_obj.log.write(f"Error resolving placeholder '{placeholder_desc}': {str(e)}", verbose=True)
        
        # Replace all placeholders in script
        for placeholder_desc, resolved_path in resolved_paths.items():
            placeholder = f"{{REF:{placeholder_desc}}}"
            # Ensure path is clean (no quotes) - should already be cleaned by _extract_path_from_pathmanager_result
            clean_path = resolved_path.strip()
            # Remove any remaining quotes (defensive check)
            while clean_path and (clean_path[0] in ["'", '"', '`'] or clean_path[-1] in ["'", '"', '`']):
                if clean_path[0] in ["'", '"', '`']:
                    clean_path = clean_path[1:]
                if clean_path and clean_path[-1] in ["'", '"', '`']:
                    clean_path = clean_path[:-1]
                clean_path = clean_path.strip()
            # Remove any embedded quotes
            if "'" in clean_path or '"' in clean_path or '`' in clean_path:
                clean_path = clean_path.replace("'", "").replace('"', "").replace('`', "")
            
            # Check if placeholder is already inside quotes in the script
            # Pattern: "..."{REF:...}"..." or '...'{REF:...}'...'
            # Look for placeholder inside double quotes: "...{REF:...}..."
            double_quote_pattern = f'"[^"]*{re.escape(placeholder)}[^"]*"'
            # Look for placeholder inside single quotes: '...{REF:...}...'
            single_quote_pattern = f"'[^']*{re.escape(placeholder)}[^']*'"
            
            if re.search(double_quote_pattern, resolved_script):
                # Placeholder is inside double quotes, replace just the placeholder part (no quotes)
                escaped_path = clean_path.replace('\\', '\\\\').replace('"', '\\"')
                resolved_script = resolved_script.replace(placeholder, escaped_path)
            elif re.search(single_quote_pattern, resolved_script):
                # Placeholder is inside single quotes, replace just the placeholder part (no quotes)
                escaped_path = clean_path.replace('\\', '\\\\').replace("'", "\\'")
                resolved_script = resolved_script.replace(placeholder, escaped_path)
            else:
                # Placeholder is not inside quotes, add quotes (single quotes for consistency with validator)
                escaped_path = clean_path.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
                resolved_script = resolved_script.replace(placeholder, f"'{escaped_path}'")
        
        if failed_placeholders:
            agent_obj.log.write(f"Warning: {len(failed_placeholders)} placeholder(s) could not be resolved: {failed_placeholders}", verbose=True)
        
        if resolved_count > 0:
            agent_obj.log.write(f"Resolved {resolved_count}/{len(unique_placeholders)} placeholder(s) using PathManager", verbose=True)
        
        state["resolved_script"] = resolved_script
        return state
    
    def _extract_path_from_pathmanager_result(result: Any) -> Optional[str]:
        """
        Extract resolved path from PathManager result.
        
        Parameters
        ----------
        result : Any
            PathManager result (dict with "message" key or string)
        
        Returns
        -------
        Optional[str]
            Resolved path or None if not found
        """
        # Extract message from result
        if isinstance(result, dict) and "message" in result:
            message = result["message"]
        elif isinstance(result, str):
            message = result
        else:
            return None
        
        # Try multiple patterns to extract the path (same as validator)
        # Pattern 1: "Path:" or "Resolved Path:" followed by path in backticks
        path_match = re.search(r'(?:Path|Resolved Path):\s*`([^`\n]+)`', message, re.IGNORECASE)
        if path_match:
            resolved_path = path_match.group(1).strip()
        else:
            # Pattern 2: "Path:" or "Resolved Path:" followed by path without backticks
            path_match = re.search(r'(?:Path|Resolved Path):\s*([/][^\n\'"]+)', message, re.IGNORECASE)
            if path_match:
                resolved_path = path_match.group(1).strip()
            else:
                # Pattern 3: Paths in markdown code blocks
                path_match = re.search(r'`([/][^`\n]+)`', message)
                if path_match:
                    resolved_path = path_match.group(1).strip()
                else:
                    # Pattern 4: Absolute paths with common extensions
                    path_match = re.search(r'([/][^\s\n`\'"]+(?:\.(?:vcf|gz|fa|chain|gtf|tsv|txt|bcf|bam|bed)[^`\s\'"]*)?)', message)
                    if path_match:
                        resolved_path = path_match.group(1).strip()
                    else:
                        # Pattern 5: Look in markdown table format
                        lines = message.split('\n')
                        resolved_path = None
                        for line in lines:
                            if '✅ Found' in line or 'Found' in line:
                                path_match = re.search(r'([/][^\s`\'"]+)', line)
                                if path_match:
                                    resolved_path = path_match.group(1).strip()
                                    break
        
        if not resolved_path:
            return None
        
        # Clean up the path: aggressively remove any quotes that might have been extracted
        # This matches the cleaning logic in a_validator.py
        if resolved_path:
            # Remove quotes from both ends and from anywhere in the string
            clean_path = resolved_path.strip()
            # Remove quotes from the beginning and end (multiple passes to handle nested quotes)
            while clean_path and (clean_path[0] in ["'", '"', '`'] or clean_path[-1] in ["'", '"', '`']):
                if clean_path[0] in ["'", '"', '`']:
                    clean_path = clean_path[1:]
                if clean_path and clean_path[-1] in ["'", '"', '`']:
                    clean_path = clean_path[:-1]
                clean_path = clean_path.strip()
            # Final check: ensure no quotes remain anywhere in the path
            # This handles cases where quotes might be embedded in the middle
            if "'" in clean_path or '"' in clean_path or '`' in clean_path:
                # Remove all quote characters (shouldn't be in file paths anyway)
                clean_path = clean_path.replace("'", "").replace('"', "").replace('`', "")
            resolved_path = clean_path
        
        return resolved_path.strip() if resolved_path else None
    
    def validator_node(state: GraphState) -> GraphState:
        """Validate script (placeholders should already be resolved by path_manager_node)."""
        resolved_script = state.get("resolved_script")
        if resolved_script is None:
            agent_obj.log.write("No resolved script to validate in validator_node", verbose=True)
            state["validated_script"] = None
            return state
        
        agent_obj.log.write(f"Validating script (length: {len(resolved_script)} chars)", verbose=True)
        
        original_message = state.get("original_message", state.get("message", ""))
        
        # Validate the script (placeholders already resolved)
        try:
            validation_result, validated_script = agent_obj.validator.validate(original_message, resolved_script)
            
            if validation_result == "VALID":
                agent_obj.log.write("Script validation passed", verbose=True)
            else:
                agent_obj.log.write(f"Script validation failed: {validation_result[:200]}", verbose=True)
                # Try to fix the script automatically
                from gwaslab_agent.agents.a_script_fixer import ScriptFixer
                if not hasattr(agent_obj, 'script_fixer'):
                    agent_obj.script_fixer = ScriptFixer(llm=agent_obj.llm, log=agent_obj.log, verbose=True)
                
                fixed_script, fix_message = agent_obj.script_fixer.fix_script(original_message, validated_script, validation_result)
                
                if fixed_script != validated_script:
                    agent_obj.log.write("Attempting to fix script with script fixer...", verbose=True)
                    validation_result, validated_script = agent_obj.validator.validate(original_message, fixed_script)
                    if validation_result == "VALID":
                        agent_obj.log.write("Script fixer successfully corrected the script", verbose=True)
                        validated_script = fixed_script
                    else:
                        agent_obj.log.write(f"Fixed script still has validation errors: {validation_result[:200]}", verbose=True)
                        state["validated_script"] = None
                        return state
                else:
                    agent_obj.log.write("Script fixer did not modify the script", verbose=True)
                    state["validated_script"] = None
                    return state
        except Exception as e:
            agent_obj.log.write(f"Error during script validation: {str(e)}", verbose=True)
            state["validated_script"] = None
            return state
        
        state["validated_script"] = validated_script
        agent_obj.log.write(f"Validation completed. Script ready for execution (length: {len(validated_script)} chars)", verbose=True)
        return state
    
    def executor_node(state: GraphState) -> GraphState:
        """Execute the validated script."""
        validated_script = state.get("validated_script")
        if validated_script is None:
            agent_obj.log.write("No validated script to execute in executor_node", verbose=True)
            state["exec_message"] = "Script validation failed or was cancelled."
            return state
        
        original_message = state.get("original_message", state.get("message", ""))
        
        agent_obj.log.write(f"Executing validated script (length: {len(validated_script)} chars)", verbose=True)
        
        # Execute the script
        try:
            agent_obj._execute_planner_script(validated_script, original_message)
            state["exec_message"] = "Script executed successfully."
            agent_obj.log.write("Script execution completed successfully", verbose=True)
        except Exception as e:
            agent_obj.log.write(f"Error during script execution: {str(e)}", verbose=True)
            state["exec_message"] = f"Script execution failed: {str(e)}"
        
        return state
    
    def summarizer_node(state: GraphState) -> GraphState:
        """Generate summary using Summarizer with summary instructions."""
        summary_instructions = state.get("summary_instructions")
        exec_message = state.get("exec_message", "")
        script = state.get("script", "")
        original_message = state.get("original_message", "")
        
        # Extract execution results information from RESULTS registry
        results_info = []
        if hasattr(agent_obj, 'RESULTS') and hasattr(agent_obj.RESULTS, 'objects'):
            for obj_id, obj in agent_obj.RESULTS.objects.items():
                obj_type = type(obj).__name__
                if obj_type == 'Sumstats':
                    # For Sumstats objects, try to get basic info
                    try:
                        if hasattr(obj, 'data') and obj.data is not None:
                            n_variants = len(obj.data)
                            results_info.append(f"- {obj_id}: Sumstats object with {n_variants:,} variants")
                    except:
                        results_info.append(f"- {obj_id}: Sumstats object")
                elif obj_type == 'DataFrame':
                    try:
                        n_rows = len(obj)
                        n_cols = len(obj.columns)
                        results_info.append(f"- {obj_id}: DataFrame with {n_rows:,} rows and {n_cols} columns")
                    except:
                        results_info.append(f"- {obj_id}: DataFrame")
                else:
                    results_info.append(f"- {obj_id}: {obj_type} object")
        
        # Compose summary message with execution results
        summary_message = f"User request: {original_message}\n\nGenerated script:\n{script}\n\nExecution status: {exec_message}"
        if results_info:
            summary_message += f"\n\nExecution results:\n" + "\n".join(results_info)
        else:
            summary_message += "\n\nExecution completed."
        
        # Use summary instructions if available
        if summary_instructions:
            metadata = {
                'language': summary_instructions.get('language'),
                'style': summary_instructions.get('style'),
                'format': summary_instructions.get('format')
            }
            agent_obj.summarizer.run(summary_message, metadata=metadata)
        else:
            # Fallback to extracting metadata from original message
            from gwaslab_agent.core.g_message_utils import extract_report_metadata
            metadata = extract_report_metadata(original_message)
            agent_obj.summarizer.run(summary_message, metadata=metadata)
        
        return state
    
    # Build the graph
    graph = StateGraph(GraphState)
    
    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("planner", planner_node)
    graph.add_node("path_manager", path_manager_node)
    graph.add_node("validator", validator_node)
    graph.add_node("executor", executor_node)
    graph.add_node("summarizer", summarizer_node)
    
    # Define edges
    graph.add_edge(START, "router")
    
    def route_after_router(state: GraphState) -> str:
        """Route after router based on route type."""
        route = state.get("route", "plan_run")
        
        # Special routes that don't go through planner
        if route == "path_manager":
            return "end"  # PathManager handles its own execution
        elif route == "loader":
            return "end"  # Loader handles its own execution
        elif route == "summarizer":
            return "end"  # Summarizer handles its own execution
        elif route == "planner":
            return "planner"  # Only planning, no execution
        else:
            # plan, plan_run, plan_run_sum all go through planner
            return "planner"
    
    graph.add_conditional_edges(
        "router",
        route_after_router,
        {
            "planner": "planner",
            "end": END
        }
    )
    
    # After planner, go to path_manager to resolve placeholders
    graph.add_edge("planner", "path_manager")
    
    # After path_manager, go to validator
    graph.add_edge("path_manager", "validator")
    
    def route_after_validator(state: GraphState) -> str:
        """Route after validator - check if script is valid and if execution is needed."""
        validated_script = state.get("validated_script")
        route = state.get("route", "plan_run")
        
        if validated_script is None:
            return "end"  # Skip execution if validation failed
        
        # If route is "plan" or "planner", only generate script, don't execute
        if route in ("plan", "planner"):
            return "end"
        
        return "executor"
    
    graph.add_conditional_edges(
        "validator",
        route_after_validator,
        {
            "executor": "executor",
            "end": END
        }
    )
    
    # After executor, always route to summarizer (unless it's just planning)
    def route_after_executor(state: GraphState) -> str:
        """Route after executor - always summarize after execution."""
        route = state.get("route", "plan_run")
        
        # Only skip summarizer if it's just planning (no execution)
        if route == "plan" or route == "planner":
            return "end"
        
        # Always summarize after execution (plan_run, plan_run_sum, etc.)
        return "summarizer"
    
    graph.add_conditional_edges(
        "executor",
        route_after_executor,
        {
            "summarizer": "summarizer",
            "end": END
        }
    )
    
    # Summarizer always ends
    graph.add_edge("summarizer", END)
    
    return graph.compile()
