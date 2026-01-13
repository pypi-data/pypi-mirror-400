"""
Script Fixer module for GWASLab Agent.

This module provides automatic fixing of validation errors in Planner-generated scripts
using LLM-based code correction.
"""

from typing import Optional, Tuple
from langchain_core.messages import SystemMessage, HumanMessage
from gwaslab_agent.core.g_print import print_status, print_llm_output
from gwaslab_agent.core.g_console import console


class ScriptFixer:
    """
    Script Fixer that uses LLM to automatically correct validation errors in scripts.
    
    When a script fails validation, the fixer analyzes the errors and generates
    a corrected version of the script that should pass validation.
    """
    
    def __init__(self, llm=None, log=None, verbose=True):
        """
        Initialize the Script Fixer.
        
        Parameters
        ----------
        llm : optional
            Language model for fixing scripts. If None, will be obtained from g_llm.
        log : optional
            Log object for writing messages
        verbose : bool, default True
            Whether to print verbose messages
        """
        if log is None:
            from gwaslab.info.g_Log import Log
            log = Log()
        self.log = log
        
        if llm is None:
            from gwaslab_agent.core.g_llm import get_llm
            llm = get_llm(self.log, verbose=verbose)
        self.llm = llm
        
        self.verbose = verbose
        
    def fix_script(self, user_request: str, original_script: str, validation_errors: str) -> Tuple[str, str]:
        """
        Fix a script that failed validation.
        
        This method uses an LLM to analyze validation errors and generate a corrected
        version of the script. It provides the LLM with:
        - The original user request
        - The original script code
        - The validation error messages
        
        Parameters
        ----------
        user_request : str
            The original user request that led to script generation
        original_script : str
            The script code that failed validation
        validation_errors : str
            The validation error messages from the validator
            
        Returns
        -------
        Tuple[str, str]
            (fixed_script, fix_message)
            - fixed_script: The corrected script code (may be the same if fixing failed)
            - fix_message: A message describing what was fixed or why fixing failed
        """
        self.log.write("Attempting to fix script with validation errors...", verbose=self.verbose, tag="agent")
        
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_fix_prompt(user_request, original_script, validation_errors)
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            fix_message = response.content if hasattr(response, 'content') else str(response)
            
            # Extract the fixed code from the response
            fixed_script = self._extract_fixed_code(fix_message, original_script)
            
            if fixed_script and fixed_script != original_script:
                self.log.write("Script fixer generated corrected code", verbose=self.verbose, tag="agent")
                print_status(console, "Script fixer generated corrected code", "success", title="SCRIPT FIXER")
                print_llm_output(console, fix_message, title="SCRIPT FIXER", if_print=self.verbose)
                return fixed_script, fix_message
            else:
                self.log.write("Script fixer could not generate corrected code", verbose=self.verbose, tag="agent")
                print_status(console, "Script fixer could not generate corrected code", "warning", title="SCRIPT FIXER")
                return original_script, "Could not fix script automatically. Please revise manually."
                
        except Exception as e:
            self.log.write(f"Error in script fixer: {str(e)}", verbose=True, tag="agent")
            print_status(console, f"Error in script fixer: {str(e)}", "error", title="SCRIPT FIXER")
            return original_script, f"Error during script fixing: {str(e)}"
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the script fixer.
        
        Returns
        -------
        str
            System prompt instructing the LLM on how to fix scripts
        """
        return """You are a Python script fixer for GWASLab operations. Your task is to fix validation errors in Python scripts generated for GWASLab analysis.

## Your Role
Analyze validation errors and correct the script to make it pass validation while preserving the original intent.

## Rules
1. **Preserve Intent**: Keep the original functionality and user intent intact
2. **Fix All Errors**: Address all validation errors mentioned in the error messages
3. **Follow GWASLab Conventions**:
   - Do NOT include `import gwaslab` - sumstats is already loaded
   - Do NOT include `gl.Sumstats(...)` or `Sumstats(...)` - data is already loaded
   - Start directly with operations on the `sumstats` object
   - Use proper GWASLab method names and arguments
4. **Syntax Errors**: Fix syntax errors (missing colons, parentheses, etc.)
5. **Method Calls**: Correct method names and argument names based on error messages
6. **Code Structure**: Ensure the code is valid Python and follows GWASLab patterns

## Output Format
Provide the corrected Python script in a markdown code block:
```python
# Corrected script here
```

If you cannot fix the script, explain why and suggest what needs to be changed manually.

## Important Notes
- The `sumstats` object is already loaded and available
- Do not add imports or data loading code
- Focus on fixing the specific errors mentioned in the validation output
- Maintain the original script structure and logic as much as possible"""
    
    def _build_fix_prompt(self, user_request: str, original_script: str, validation_errors: str) -> str:
        """
        Build the prompt for fixing the script.
        
        Parameters
        ----------
        user_request : str
            The original user request
        original_script : str
            The script that failed validation
        validation_errors : str
            The validation error messages
            
        Returns
        -------
        str
            The prompt for the LLM
        """
        prompt = f"""The following Python script failed validation. Please fix all validation errors.

## Original User Request
{user_request}

## Validation Errors
{validation_errors}

## Original Script (with errors)
```python
{original_script}
```

## Your Task
Fix all validation errors in the script while preserving the original intent and functionality. Provide the corrected script in a markdown code block."""
        
        return prompt
    
    def _extract_fixed_code(self, fix_message: str, fallback_script: str) -> str:
        """
        Extract the fixed code from the LLM response.
        
        Parameters
        ----------
        fix_message : str
            The LLM response message
        fallback_script : str
            The original script to return if extraction fails
            
        Returns
        -------
        str
            The extracted fixed code, or fallback_script if extraction fails
        """
        import re
        
        # Try to find Python code block
        python_block_pattern = r"```(?:python)?\s*(.*?)```"
        match = re.search(python_block_pattern, fix_message, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # If no code block, check if the entire message looks like Python code
        # (contains common Python keywords/patterns)
        fix_message_stripped = fix_message.strip()
        if fix_message_stripped:
            # Check for Python-like patterns
            has_python_patterns = any(
                keyword in fix_message_stripped for keyword in ['sumstats.', 'def ', '=', '(', ')', '#']
            )
            
            if has_python_patterns:
                # Check if it starts with a comment or looks like Python code
                first_line = fix_message_stripped.split('\n')[0].strip()
                if (first_line.startswith('#') or 
                    first_line.startswith('sumstats') or
                    '=' in first_line or
                    '(' in first_line):
                    return fix_message_stripped
        
        # If we can't extract code, return the fallback
        return fallback_script

