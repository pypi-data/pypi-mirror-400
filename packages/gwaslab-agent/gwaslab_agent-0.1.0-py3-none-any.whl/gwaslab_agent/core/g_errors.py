"""
Structured Error Types for GWASLab Agent System

This module defines specific error types for different failure scenarios,
enabling better error handling and recovery strategies.
"""


class AgentError(Exception):
    """Base exception for all agent-related errors."""
    
    def __init__(self, message: str, context: dict = None):
        """
        Initialize agent error.
        
        Parameters
        ----------
        message : str
            Error message
        context : dict, optional
            Additional context about the error
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
    
    def __str__(self) -> str:
        """String representation with context."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (Context: {context_str})"
        return self.message


class ValidationError(AgentError):
    """Error raised when script validation fails."""
    
    def __init__(self, message: str, errors: list = None, script: str = None, **kwargs):
        """
        Initialize validation error.
        
        Parameters
        ----------
        message : str
            Error message
        errors : list, optional
            List of validation error details
        script : str, optional
            The script that failed validation
        **kwargs
            Additional context
        """
        super().__init__(message, context=kwargs)
        self.errors = errors or []
        self.script = script
    
    def get_error_summary(self) -> str:
        """Get a summary of all validation errors."""
        if not self.errors:
            return self.message
        
        summary = f"{self.message}\nValidation errors:\n"
        for i, error in enumerate(self.errors, 1):
            summary += f"  {i}. {error}\n"
        return summary


class ExecutionError(AgentError):
    """Error raised when script execution fails."""
    
    def __init__(
        self,
        message: str,
        error: Exception = None,
        script: str = None,
        line_number: int = None,
        **kwargs
    ):
        """
        Initialize execution error.
        
        Parameters
        ----------
        message : str
            Error message
        error : Exception, optional
            The original exception that occurred
        script : str, optional
            The script that failed to execute
        line_number : int, optional
            Line number where error occurred
        **kwargs
            Additional context
        """
        super().__init__(message, context=kwargs)
        self.error = error
        self.script = script
        self.line_number = line_number
    
    def get_error_details(self) -> str:
        """Get detailed error information."""
        details = self.message
        if self.line_number:
            details += f"\nError at line {self.line_number}"
        if self.error:
            details += f"\nOriginal error: {type(self.error).__name__}: {str(self.error)}"
        if self.script and self.line_number:
            lines = self.script.split('\n')
            if 0 < self.line_number <= len(lines):
                details += f"\nLine content: {lines[self.line_number - 1]}"
        return details


class PlanningError(AgentError):
    """Error raised when script planning/generation fails."""
    
    def __init__(self, message: str, user_message: str = None, **kwargs):
        """
        Initialize planning error.
        
        Parameters
        ----------
        message : str
            Error message
        user_message : str, optional
            The original user message that triggered planning
        **kwargs
            Additional context
        """
        super().__init__(message, context=kwargs)
        self.user_message = user_message


class LoadingError(AgentError):
    """Error raised when data loading fails."""
    
    def __init__(self, message: str, path: str = None, **kwargs):
        """
        Initialize loading error.
        
        Parameters
        ----------
        message : str
            Error message
        path : str, optional
            The file path that failed to load
        **kwargs
            Additional context
        """
        super().__init__(message, context=kwargs)
        self.path = path


class PathResolutionError(AgentError):
    """Error raised when reference path resolution fails."""
    
    def __init__(self, message: str, placeholder: str = None, **kwargs):
        """
        Initialize path resolution error.
        
        Parameters
        ----------
        message : str
            Error message
        placeholder : str, optional
            The placeholder that couldn't be resolved
        **kwargs
            Additional context
        """
        super().__init__(message, context=kwargs)
        self.placeholder = placeholder


class ConfigurationError(AgentError):
    """Error raised when agent configuration is invalid."""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        """
        Initialize configuration error.
        
        Parameters
        ----------
        message : str
            Error message
        config_key : str, optional
            The configuration key that caused the error
        **kwargs
            Additional context
        """
        super().__init__(message, context=kwargs)
        self.config_key = config_key

