"""Exceptions for xelytics-core.

All package-specific exceptions are defined here.
"""


class XelyticsError(Exception):
    """Base exception for xelytics-core.
    
    All xelytics exceptions inherit from this.
    """
    
    def __init__(self, message: str, error_code: str = "UNKNOWN", details: dict = None):
        """Initialize XelyticsError.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Optional additional details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class DataValidationError(XelyticsError):
    """Invalid input data.
    
    Raised when input data fails validation checks.
    """
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "DATA_VALIDATION_ERROR", details)


class StatisticalError(XelyticsError):
    """Statistical computation failed.
    
    Raised when a statistical test cannot be performed.
    """
    
    def __init__(self, message: str, test_name: str = None, details: dict = None):
        details = details or {}
        if test_name:
            details["test_name"] = test_name
        super().__init__(message, "STATISTICAL_ERROR", details)


class ConfigurationError(XelyticsError):
    """Invalid configuration.
    
    Raised when configuration values are invalid.
    """
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)


class LLMError(XelyticsError):
    """LLM provider error.
    
    Raised when LLM operations fail.
    """
    
    def __init__(self, message: str, provider: str = None, details: dict = None):
        details = details or {}
        if provider:
            details["provider"] = provider
        super().__init__(message, "LLM_ERROR", details)
