"""Logging configuration for the wine semantic search MCP server."""

import logging
import logging.config
import sys
from typing import Any, Dict, Optional


def setup_logging(
    level: str = "INFO",
    format_type: str = "structured",
    log_file: Optional[str] = None
) -> None:
    """Set up structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type ('structured' or 'simple')
        log_file: Optional file path for logging output
    """
    # Define log formats
    if format_type == "structured":
        log_format = (
            "%(asctime)s | %(levelname)-8s | %(name)s | "
            "%(funcName)s:%(lineno)d | %(message)s"
        )
    else:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure logging
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard",
                "stream": sys.stderr
            }
        },
        "loggers": {
            "wine_semantic_search": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            },
            # Reduce noise from external libraries
            "openai": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "asyncpg": {
                "level": "WARNING", 
                "handlers": ["console"],
                "propagate": False
            },
            "httpx": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": level,
            "handlers": ["console"]
        }
    }
    
    # Add file handler if log_file is specified
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "level": level,
            "formatter": "standard",
            "filename": log_file,
            "mode": "a"
        }
        # Add file handler to all loggers
        for logger_config in config["loggers"].values():
            logger_config["handlers"].append("file")
        config["root"]["handlers"].append("file")
    
    logging.config.dictConfig(config)


def sanitize_for_logging(data: Any, sensitive_keys: Optional[set] = None) -> Any:
    """Sanitize data for logging by removing or masking sensitive information.
    
    Args:
        data: Data to sanitize (dict, list, str, or other)
        sensitive_keys: Set of keys to mask (defaults to common sensitive keys)
        
    Returns:
        Sanitized data safe for logging
    """
    if sensitive_keys is None:
        sensitive_keys = {
            'password', 'api_key', 'token', 'secret', 'key', 'auth',
            'authorization', 'credential', 'openai_api_key', 'database_url'
        }
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive_key in key_lower for sensitive_key in sensitive_keys):
                # Mask sensitive values
                if isinstance(value, str) and len(value) > 8:
                    sanitized[key] = f"{value[:4]}...{value[-4:]}"
                else:
                    sanitized[key] = "***MASKED***"
            else:
                sanitized[key] = sanitize_for_logging(value, sensitive_keys)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_for_logging(item, sensitive_keys) for item in data]
    elif isinstance(data, str):
        # Check if the string looks like a URL with credentials
        if '://' in data and '@' in data:
            # Mask credentials in URLs like postgresql://user:pass@host/db
            parts = data.split('@')
            if len(parts) >= 2:
                protocol_and_creds = parts[0]
                if '://' in protocol_and_creds:
                    protocol, creds = protocol_and_creds.split('://', 1)
                    if ':' in creds:
                        user, _ = creds.split(':', 1)
                        return f"{protocol}://{user}:***@{'@'.join(parts[1:])}"
        return data
    else:
        return data


def log_request_start(logger: logging.Logger, operation: str, **kwargs) -> None:
    """Log the start of a request or operation.
    
    Args:
        logger: Logger instance to use
        operation: Name of the operation being started
        **kwargs: Additional context to log (will be sanitized)
    """
    sanitized_context = sanitize_for_logging(kwargs)
    logger.info(f"Starting {operation}", extra={"context": sanitized_context})


def log_request_success(
    logger: logging.Logger, 
    operation: str, 
    duration_ms: Optional[float] = None,
    **kwargs
) -> None:
    """Log successful completion of a request or operation.
    
    Args:
        logger: Logger instance to use
        operation: Name of the operation that completed
        duration_ms: Optional duration in milliseconds
        **kwargs: Additional context to log (will be sanitized)
    """
    sanitized_context = sanitize_for_logging(kwargs)
    message = f"Completed {operation}"
    if duration_ms is not None:
        message += f" in {duration_ms:.2f}ms"
    
    logger.info(message, extra={"context": sanitized_context})


def log_request_error(
    logger: logging.Logger,
    operation: str,
    error: Exception,
    duration_ms: Optional[float] = None,
    **kwargs
) -> None:
    """Log an error during a request or operation.
    
    Args:
        logger: Logger instance to use
        operation: Name of the operation that failed
        error: The exception that occurred
        duration_ms: Optional duration in milliseconds before failure
        **kwargs: Additional context to log (will be sanitized)
    """
    sanitized_context = sanitize_for_logging(kwargs)
    message = f"Failed {operation}: {type(error).__name__}: {str(error)}"
    if duration_ms is not None:
        message += f" (after {duration_ms:.2f}ms)"
    
    logger.error(message, extra={"context": sanitized_context}, exc_info=True)