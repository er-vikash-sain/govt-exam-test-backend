import structlog
import logging
import sys
from typing import Any, Dict
from app.core.config import settings

def setup_logging():
    """Setup structured logging configuration"""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper())
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a logger instance"""
    return structlog.get_logger(name)

def log_request_info(request_id: str, user_id: str = None, **kwargs) -> Dict[str, Any]:
    """Create a standardized log context for requests"""
    context = {
        "request_id": request_id,
        "timestamp": structlog.processors.TimeStamper(fmt="iso")(None, None, None),
    }
    
    if user_id:
        context["user_id"] = user_id
    
    context.update(kwargs)
    return context

def log_error(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a standardized error log context"""
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": structlog.processors.TimeStamper(fmt="iso")(None, None, None),
    }
    
    if context:
        error_context.update(context)
    
    return error_context
