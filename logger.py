#!/usr/bin/env python3
"""
Comprehensive Logging System for Legal Assistant AI Platform

Provides structured logging with multiple handlers, log rotation,
and integration with the exception hierarchy for consistent error tracking.
"""

import os
import sys
import json
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime
import threading
import uuid
from contextvars import ContextVar

# Import our exception hierarchy
from exceptions import LegalAssistantError, get_exception_context


class StructuredFormatter(logging.Formatter):
    """
    Structured JSON formatter for consistent log output.
    
    Formats log records as JSON with structured fields for easy parsing
    and analysis by log aggregation systems.
    """
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'thread_id': record.thread,
            'process_id': record.process
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        # Add context information
        if self.include_context:
            context = get_exception_context()
            log_entry['context'] = context
        
        return json.dumps(log_entry, default=str)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Colored console formatter for development and debugging.
    
    Provides human-readable output with color coding for different log levels.
    """
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for console output."""
        # Add color to level name
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Format the message
        formatted = super().format(record)
        
        # Add color to level name in the formatted message
        formatted = formatted.replace(
            record.levelname,
            f"{level_color}{record.levelname}{reset_color}"
        )
        
        return formatted


class LegalAssistantLogger:
    """
    Comprehensive logger for the Legal Assistant AI Platform.
    
    Provides structured logging with multiple handlers, log rotation,
    and integration with the exception hierarchy.
    """
    
    def __init__(self, 
                 name: str = "legal_assistant",
                 log_level: str = "INFO",
                 log_dir: str = "./logs",
                 max_log_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 enable_json: bool = True):
        """
        Initialize the logger with comprehensive configuration.
        
        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory for log files
            max_log_size: Maximum size of log files before rotation
            backup_count: Number of backup log files to keep
            enable_console: Enable console logging
            enable_file: Enable file logging
            enable_json: Enable JSON structured logging
        """
        self.name = name
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir)
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        
        # Create log directory
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Add handlers based on configuration
        if enable_console:
            self._add_console_handler()
        
        if enable_file:
            self._add_file_handlers()
        
        if enable_json:
            self._add_json_handler()
        
        # Add custom exception handler
        self._setup_exception_handling()
        
        # Log initialization
        self.info("Logger initialized", extra={
            'log_level': log_level,
            'log_dir': str(self.log_dir),
            'handlers': [h.__class__.__name__ for h in self.logger.handlers]
        })
    
    def _add_console_handler(self):
        """Add colored console handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Use colored formatter for console
        formatter = ColoredConsoleFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _add_file_handlers(self):
        """Add file handlers with rotation."""
        # General log file
        general_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "legal_assistant.log",
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        general_handler.setLevel(self.log_level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
        )
        general_handler.setFormatter(formatter)
        
        self.logger.addHandler(general_handler)
        
        # Error log file (only errors and above)
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "errors.log",
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        self.logger.addHandler(error_handler)
        
        # Security log file
        security_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "security.log",
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        security_handler.setLevel(self.log_level)
        security_handler.setFormatter(formatter)
        
        # Add filter for security-related logs
        security_handler.addFilter(lambda record: 'security' in record.name.lower() or 
                                                   'auth' in record.name.lower() or
                                                   'encrypt' in record.name.lower())
        
        self.logger.addHandler(security_handler)
    
    def _add_json_handler(self):
        """Add JSON structured logging handler."""
        json_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "structured.log",
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        json_handler.setLevel(self.log_level)
        
        formatter = StructuredFormatter(include_context=True)
        json_handler.setFormatter(formatter)
        
        self.logger.addHandler(json_handler)
    
    def _setup_exception_handling(self):
        """Setup custom exception handling."""
        def handle_exception(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions."""
            if issubclass(exc_type, KeyboardInterrupt):
                # Don't log keyboard interrupts
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            # Log the exception
            self.logger.critical(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback),
                extra={
                    'exception_type': exc_type.__name__,
                    'exception_message': str(exc_value)
                }
            )
        
        # Set the exception handler
        sys.excepthook = handle_exception
    
    def log_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Log an exception with proper formatting and context.
        
        Args:
            exception: Exception to log
            context: Additional context information
        """
        if isinstance(exception, LegalAssistantError):
            # Use structured logging for our custom exceptions
            log_data = exception.to_dict()
            if context:
                log_data['context'].update(context)
            
            self.logger.error(
                f"[{exception.error_code}] {exception.message}",
                extra=log_data
            )
        else:
            # Log generic exceptions
            self.logger.error(
                f"Exception: {type(exception).__name__}: {str(exception)}",
                exc_info=True,
                extra=context or {}
            )
    
    def log_security_event(self, event_type: str, description: str, 
                          severity: str = "INFO", context: Optional[Dict[str, Any]] = None):
        """
        Log security-related events.
        
        Args:
            event_type: Type of security event
            description: Description of the event
            severity: Event severity
            context: Additional context
        """
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        
        log_method(
            f"SECURITY_EVENT: {event_type} - {description}",
            extra={
                'event_type': event_type,
                'security_event': True,
                'context': context or {}
            }
        )
    
    def log_performance(self, operation: str, duration: float, 
                       context: Optional[Dict[str, Any]] = None):
        """
        Log performance metrics.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            context: Additional context
        """
        self.logger.info(
            f"PERFORMANCE: {operation} completed in {duration:.3f}s",
            extra={
                'operation': operation,
                'duration': duration,
                'performance_metric': True,
                'context': context or {}
            }
        )
    
    def log_user_action(self, action: str, user_id: Optional[str] = None,
                       session_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Log user actions for audit purposes.
        
        Args:
            action: User action performed
            user_id: User identifier
            session_id: Session identifier
            context: Additional context
        """
        self.logger.info(
            f"USER_ACTION: {action}",
            extra={
                'action': action,
                'user_id': user_id,
                'session_id': session_id,
                'user_action': True,
                'context': context or {}
            }
        )
    
    def log_database_operation(self, operation: str, table: Optional[str] = None,
                              duration: Optional[float] = None, context: Optional[Dict[str, Any]] = None):
        """
        Log database operations.
        
        Args:
            operation: Database operation performed
            table: Table name
            duration: Operation duration
            context: Additional context
        """
        message = f"DB_OPERATION: {operation}"
        if table:
            message += f" on table {table}"
        if duration:
            message += f" (duration: {duration:.3f}s)"
        
        self.logger.debug(
            message,
            extra={
                'operation': operation,
                'table': table,
                'duration': duration,
                'database_operation': True,
                'context': context or {}
            }
        )
    
    def log_ai_operation(self, operation: str, model: Optional[str] = None,
                        duration: Optional[float] = None, context: Optional[Dict[str, Any]] = None):
        """
        Log AI/ML operations.
        
        Args:
            operation: AI operation performed
            model: Model name
            duration: Operation duration
            context: Additional context
        """
        message = f"AI_OPERATION: {operation}"
        if model:
            message += f" using model {model}"
        if duration:
            message += f" (duration: {duration:.3f}s)"
        
        self.logger.info(
            message,
            extra={
                'operation': operation,
                'model': model,
                'duration': duration,
                'ai_operation': True,
                'context': context or {}
            }
        )
    
    # Delegate standard logging methods
    def debug(self, message: str, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)


# Global logger instance
_logger_instance: Optional[LegalAssistantLogger] = None


def get_logger(name: str = "legal_assistant", **kwargs) -> LegalAssistantLogger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        **kwargs: Logger configuration options
        
    Returns:
        Configured logger instance
    """
    global _logger_instance
    
    if _logger_instance is None:
        # Get configuration from environment or use defaults
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_dir = os.getenv('LOG_DIR', './logs')
        enable_console = os.getenv('LOG_CONSOLE', 'true').lower() == 'true'
        enable_file = os.getenv('LOG_FILE', 'true').lower() == 'true'
        enable_json = os.getenv('LOG_JSON', 'true').lower() == 'true'
        
        _logger_instance = LegalAssistantLogger(
            name=name,
            log_level=log_level,
            log_dir=log_dir,
            enable_console=enable_console,
            enable_file=enable_file,
            enable_json=enable_json,
            **kwargs
        )
    
    return _logger_instance


# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar('user_id', default=None)
session_id_var: ContextVar[Optional[str]] = ContextVar('session_id', default=None)


def set_request_context(request_id: Optional[str] = None,
                       user_id: Optional[str] = None,
                       session_id: Optional[str] = None):
    """
    Set request context for logging.
    
    Args:
        request_id: Request identifier
        user_id: User identifier
        session_id: Session identifier
    """
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if session_id:
        session_id_var.set(session_id)


def get_request_context() -> Dict[str, Any]:
    """
    Get current request context.
    
    Returns:
        Dictionary with current request context
    """
    return {
        'request_id': request_id_var.get(),
        'user_id': user_id_var.get(),
        'session_id': session_id_var.get()
    }


# Decorator for automatic logging
def log_function_call(logger: Optional[LegalAssistantLogger] = None):
    """
    Decorator to automatically log function calls with timing.
    
    Args:
        logger: Logger instance to use
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if logger is None:
                log = get_logger()
            else:
                log = logger
            
            func_name = func.__name__
            module_name = func.__module__
            
            # Log function entry
            log.debug(f"Entering {module_name}.{func_name}")
            
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful completion
                duration = (datetime.now() - start_time).total_seconds()
                log.debug(f"Completed {module_name}.{func_name} in {duration:.3f}s")
                
                return result
                
            except Exception as e:
                # Log exception
                duration = (datetime.now() - start_time).total_seconds()
                log.error(f"Exception in {module_name}.{func_name} after {duration:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator 