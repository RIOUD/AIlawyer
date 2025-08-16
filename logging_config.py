#!/usr/bin/env python3
"""
Logging Configuration for Legal Assistant AI Platform

Provides comprehensive logging configuration for different environments
with structured logging, log rotation, and monitoring integration.
"""

import os
import logging.config
from pathlib import Path
from typing import Dict, Any, Optional


def get_logging_config(environment: str = "development") -> Dict[str, Any]:
    """
    Get logging configuration for the specified environment.
    
    Args:
        environment: Environment name (development, staging, production)
        
    Returns:
        Logging configuration dictionary
    """
    
    # Base configuration
    base_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s'
            },
            'json': {
                '()': 'logger.StructuredFormatter',
                'include_context': True
            },
            'colored': {
                '()': 'logger.ColoredConsoleFormatter',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'filters': {
            'security_filter': {
                '()': 'logger.SecurityFilter'
            },
            'performance_filter': {
                '()': 'logger.PerformanceFilter'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'colored',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filename': 'logs/legal_assistant.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filename': 'logs/errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'security_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filename': 'logs/security.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'filters': ['security_filter']
            },
            'json_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': 'logs/structured.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            },
            'performance_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'json',
                'filename': 'logs/performance.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'filters': ['performance_filter']
            }
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console', 'file', 'json_file'],
                'level': 'INFO',
                'propagate': False
            },
            'legal_assistant': {
                'handlers': ['console', 'file', 'json_file'],
                'level': 'INFO',
                'propagate': False
            },
            'legal_assistant.security': {
                'handlers': ['security_file', 'json_file'],
                'level': 'INFO',
                'propagate': False
            },
            'legal_assistant.performance': {
                'handlers': ['performance_file', 'json_file'],
                'level': 'INFO',
                'propagate': False
            },
            'legal_assistant.database': {
                'handlers': ['file', 'json_file'],
                'level': 'DEBUG',
                'propagate': False
            },
            'legal_assistant.ai': {
                'handlers': ['file', 'json_file'],
                'level': 'INFO',
                'propagate': False
            },
            'legal_assistant.web': {
                'handlers': ['console', 'file', 'json_file'],
                'level': 'INFO',
                'propagate': False
            },
            'legal_assistant.error_handler': {
                'handlers': ['error_file', 'json_file'],
                'level': 'ERROR',
                'propagate': False
            }
        }
    }
    
    # Environment-specific configurations
    if environment == "development":
        base_config['loggers']['']['level'] = 'DEBUG'
        base_config['loggers']['legal_assistant']['level'] = 'DEBUG'
        base_config['handlers']['console']['level'] = 'DEBUG'
        
    elif environment == "staging":
        base_config['loggers']['']['level'] = 'INFO'
        base_config['loggers']['legal_assistant']['level'] = 'INFO'
        base_config['handlers']['console']['level'] = 'INFO'
        
    elif environment == "production":
        base_config['loggers']['']['level'] = 'WARNING'
        base_config['loggers']['legal_assistant']['level'] = 'INFO'
        base_config['handlers']['console']['level'] = 'WARNING'
        
        # Add additional production handlers
        base_config['handlers']['syslog'] = {
            'class': 'logging.handlers.SysLogHandler',
            'level': 'ERROR',
            'formatter': 'json',
            'address': '/dev/log'
        }
        
        # Add syslog to root logger in production
        base_config['loggers']['']['handlers'].append('syslog')
    
    return base_config


def setup_logging(environment: str = None, log_dir: str = "logs"):
    """
    Setup logging configuration for the application.
    
    Args:
        environment: Environment name (auto-detected if None)
        log_dir: Directory for log files
    """
    # Auto-detect environment if not specified
    if environment is None:
        environment = os.getenv('FLASK_ENV', 'development')
    
    # Create log directory
    Path(log_dir).mkdir(exist_ok=True)
    
    # Get configuration
    config = get_logging_config(environment)
    
    # Update log file paths
    for handler_name, handler_config in config['handlers'].items():
        if 'filename' in handler_config:
            handler_config['filename'] = os.path.join(log_dir, os.path.basename(handler_config['filename']))
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log setup completion
    logger = logging.getLogger('legal_assistant')
    logger.info(f"Logging configured for environment: {environment}")


def get_logger(name: str = "legal_assistant") -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Custom filters for specialized logging
class SecurityFilter(logging.Filter):
    """Filter for security-related log records."""
    
    def filter(self, record):
        """Filter security-related log records."""
        return (
            hasattr(record, 'security_event') and record.security_event or
            'security' in record.name.lower() or
            'auth' in record.name.lower() or
            'encrypt' in record.name.lower()
        )


class PerformanceFilter(logging.Filter):
    """Filter for performance-related log records."""
    
    def filter(self, record):
        """Filter performance-related log records."""
        return (
            hasattr(record, 'performance_metric') and record.performance_metric or
            'performance' in record.name.lower() or
            'duration' in getattr(record, 'extra', {})
        )


# Logging utilities
def log_function_performance(logger: logging.Logger):
    """
    Decorator to log function performance.
    
    Args:
        logger: Logger instance
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"Function {func.__name__} completed successfully",
                    extra={
                        'function': func.__name__,
                        'duration': duration,
                        'performance_metric': True
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Function {func.__name__} failed after {duration:.3f}s",
                    extra={
                        'function': func.__name__,
                        'duration': duration,
                        'error': str(e),
                        'performance_metric': True
                    }
                )
                raise
        
        return wrapper
    return decorator


def log_security_event(logger: logging.Logger, event_type: str, description: str, 
                      severity: str = "INFO", **kwargs):
    """
    Log a security event with proper formatting.
    
    Args:
        logger: Logger instance
        description: Event description
        severity: Event severity
        **kwargs: Additional context
    """
    log_method = getattr(logger, severity.lower(), logger.info)
    
    log_method(
        f"SECURITY_EVENT: {event_type} - {description}",
        extra={
            'event_type': event_type,
            'security_event': True,
            **kwargs
        }
    )


def log_database_operation(logger: logging.Logger, operation: str, table: str = None, 
                          duration: float = None, **kwargs):
    """
    Log a database operation.
    
    Args:
        logger: Logger instance
        operation: Database operation
        table: Table name
        duration: Operation duration
        **kwargs: Additional context
    """
    message = f"DB_OPERATION: {operation}"
    if table:
        message += f" on table {table}"
    if duration:
        message += f" (duration: {duration:.3f}s)"
    
    logger.debug(
        message,
        extra={
            'operation': operation,
            'table': table,
            'duration': duration,
            'database_operation': True,
            **kwargs
        }
    )


def log_ai_operation(logger: logging.Logger, operation: str, model: str = None,
                    duration: float = None, **kwargs):
    """
    Log an AI/ML operation.
    
    Args:
        logger: Logger instance
        operation: AI operation
        model: Model name
        duration: Operation duration
        **kwargs: Additional context
    """
    message = f"AI_OPERATION: {operation}"
    if model:
        message += f" using model {model}"
    if duration:
        message += f" (duration: {duration:.3f}s)"
    
    logger.info(
        message,
        extra={
            'operation': operation,
            'model': model,
            'duration': duration,
            'ai_operation': True,
            **kwargs
        }
    )


# Initialize logging when module is imported
if __name__ != "__main__":
    # Only setup logging if not running as main
    try:
        setup_logging()
    except Exception:
        # Fallback to basic logging if setup fails
        logging.basicConfig(level=logging.INFO) 