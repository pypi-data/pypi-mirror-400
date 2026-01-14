"""Error response formatting for the wine semantic search MCP server."""

import logging
from enum import Enum
from typing import Any, Dict, Optional

from mcp.types import ErrorData, JSONRPCError


logger = logging.getLogger(__name__)


class ErrorCode(Enum):
    """Standard error codes for the wine semantic search server."""
    
    # Client errors (4xx equivalent)
    INVALID_ARGUMENTS = -32602  # MCP standard invalid params
    MISSING_QUERY = -32001      # Custom: Query parameter missing
    INVALID_QUERY = -32002      # Custom: Query parameter invalid
    INVALID_LIMIT = -32003      # Custom: Limit parameter invalid
    
    # Server errors (5xx equivalent)
    INTERNAL_ERROR = -32603     # MCP standard internal error
    DATABASE_ERROR = -32004     # Custom: Database operation failed
    EMBEDDING_ERROR = -32005    # Custom: Embedding generation failed
    API_ERROR = -32006          # Custom: External API error
    INITIALIZATION_ERROR = -32007  # Custom: Server initialization failed


class WineSearchError(Exception):
    """Base exception for wine search operations with error formatting."""
    
    def __init__(
        self, 
        message: str, 
        error_code: ErrorCode, 
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """Initialize wine search error.
        
        Args:
            message: Human-readable error message
            error_code: Standardized error code
            details: Additional error details (will be sanitized)
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_error = original_error


def sanitize_error_details(details: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize error details to remove sensitive information.
    
    Args:
        details: Raw error details dictionary
        
    Returns:
        Sanitized error details safe for client consumption
    """
    if not details:
        return {}
    
    sanitized = {}
    
    # List of sensitive keys to exclude
    sensitive_keys = {
        'api_key', 'password', 'token', 'secret', 'credential',
        'database_url', 'connection_string', 'auth', 'authorization'
    }
    
    for key, value in details.items():
        # Skip sensitive keys
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            continue
            
        # Sanitize string values that might contain sensitive info
        if isinstance(value, str):
            # Don't include full database URLs or API keys
            if any(sensitive in value.lower() for sensitive in ['postgresql://', 'sk-', 'bearer']):
                continue
            # Truncate very long strings that might contain sensitive data
            if len(value) > 200:
                sanitized[key] = value[:200] + "... [truncated]"
            else:
                sanitized[key] = value
        elif isinstance(value, (int, float, bool)):
            sanitized[key] = value
        elif isinstance(value, (list, dict)):
            # For complex types, only include basic info
            if isinstance(value, list):
                sanitized[key] = f"list with {len(value)} items"
            else:
                sanitized[key] = f"dict with {len(value)} keys"
    
    return sanitized


def format_error_response(
    error: Exception,
    request_id: Optional[str] = None,
    operation: Optional[str] = None
) -> JSONRPCError:
    """Format an exception into a standardized MCP error response.
    
    Args:
        error: The exception to format
        request_id: Optional request ID for tracing
        operation: Optional operation name for context
        
    Returns:
        JSONRPCError formatted for MCP protocol
    """
    # Handle WineSearchError with specific formatting
    if isinstance(error, WineSearchError):
        error_data = ErrorData(
            code=error.error_code.value,
            message=error.message,
            data=sanitize_error_details(error.details) if error.details else None
        )
        
        logger.error(
            f"Wine search error in operation '{operation}'",
            extra={
                "error_code": error.error_code.value,
                "error_message": error.message,
                "operation": operation,
                "request_id": request_id,
                "original_error": str(error.original_error) if error.original_error else None
            }
        )
        
    # Handle standard ValueError (invalid arguments)
    elif isinstance(error, ValueError):
        error_data = ErrorData(
            code=ErrorCode.INVALID_ARGUMENTS.value,
            message=f"Invalid arguments: {str(error)}",
            data={"operation": operation} if operation else None
        )
        
        logger.warning(
            f"Invalid arguments in operation '{operation}': {str(error)}",
            extra={
                "error_code": ErrorCode.INVALID_ARGUMENTS.value,
                "operation": operation,
                "request_id": request_id
            }
        )
        
    # Handle ConnectionError (database issues)
    elif isinstance(error, ConnectionError):
        error_data = ErrorData(
            code=ErrorCode.DATABASE_ERROR.value,
            message="Database connection failed",
            data={"operation": operation} if operation else None
        )
        
        logger.error(
            f"Database connection error in operation '{operation}'",
            extra={
                "error_code": ErrorCode.DATABASE_ERROR.value,
                "operation": operation,
                "request_id": request_id,
                "error_details": str(error)
            }
        )
        
    # Handle RuntimeError (general server errors)
    elif isinstance(error, RuntimeError):
        # Determine specific error code based on error message
        error_message = str(error).lower()
        if "database" in error_message:
            code = ErrorCode.DATABASE_ERROR
            message = "Database operation failed"
        elif "embedding" in error_message or "openai" in error_message:
            code = ErrorCode.EMBEDDING_ERROR
            message = "Embedding generation failed"
        elif "initialization" in error_message:
            code = ErrorCode.INITIALIZATION_ERROR
            message = "Server initialization failed"
        else:
            code = ErrorCode.INTERNAL_ERROR
            message = "Internal server error"
            
        error_data = ErrorData(
            code=code.value,
            message=message,
            data={"operation": operation} if operation else None
        )
        
        logger.error(
            f"Runtime error in operation '{operation}': {message}",
            extra={
                "error_code": code.value,
                "operation": operation,
                "request_id": request_id,
                "error_details": str(error)
            }
        )
        
    # Handle all other exceptions as internal errors
    else:
        error_data = ErrorData(
            code=ErrorCode.INTERNAL_ERROR.value,
            message="An unexpected error occurred",
            data={"operation": operation} if operation else None
        )
        
        logger.error(
            f"Unexpected error in operation '{operation}': {type(error).__name__}",
            extra={
                "error_code": ErrorCode.INTERNAL_ERROR.value,
                "error_type": type(error).__name__,
                "operation": operation,
                "request_id": request_id,
                "error_details": str(error)
            }
        )
    
    # Create JSONRPCError with proper ID
    return JSONRPCError(
        jsonrpc="2.0",
        id=request_id or "unknown",
        error=error_data
    )


def create_validation_error(field: str, message: str, value: Any = None) -> WineSearchError:
    """Create a standardized validation error.
    
    Args:
        field: The field that failed validation
        message: Descriptive error message
        value: The invalid value (will be sanitized)
        
    Returns:
        WineSearchError with validation details
    """
    details = {"field": field}
    if value is not None:
        # Sanitize the value to avoid exposing sensitive data
        if isinstance(value, str) and len(value) > 100:
            details["value"] = value[:100] + "... [truncated]"
        elif not isinstance(value, (dict, list)):
            details["value"] = str(value)
    
    return WineSearchError(
        message=f"Invalid arguments: {message}",
        error_code=ErrorCode.INVALID_ARGUMENTS,
        details=details
    )


def create_database_error(operation: str, original_error: Exception) -> WineSearchError:
    """Create a standardized database error.
    
    Args:
        operation: The database operation that failed
        original_error: The original database exception
        
    Returns:
        WineSearchError with database error details
    """
    return WineSearchError(
        message=f"Database operation '{operation}' failed",
        error_code=ErrorCode.DATABASE_ERROR,
        details={"operation": operation},
        original_error=original_error
    )


def create_embedding_error(operation: str, original_error: Exception) -> WineSearchError:
    """Create a standardized embedding generation error.
    
    Args:
        operation: The embedding operation that failed
        original_error: The original API exception
        
    Returns:
        WineSearchError with embedding error details
    """
    return WineSearchError(
        message=f"Embedding operation '{operation}' failed",
        error_code=ErrorCode.EMBEDDING_ERROR,
        details={"operation": operation},
        original_error=original_error
    )


def create_api_error(service: str, original_error: Exception) -> WineSearchError:
    """Create a standardized external API error.
    
    Args:
        service: The external service that failed
        original_error: The original API exception
        
    Returns:
        WineSearchError with API error details
    """
    return WineSearchError(
        message=f"External API '{service}' request failed",
        error_code=ErrorCode.API_ERROR,
        details={"service": service},
        original_error=original_error
    )