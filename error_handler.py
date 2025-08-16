#!/usr/bin/env python3
"""
Error Handler Middleware for Legal Assistant AI Platform

Provides comprehensive error handling for Flask applications with
integration to the exception hierarchy and logging system.
"""

import traceback
from typing import Dict, Any, Optional, Union, Callable
from datetime import datetime
import uuid

from flask import Flask, request, jsonify, g, current_app
from werkzeug.exceptions import HTTPException

from exceptions import (
    LegalAssistantError, DatabaseError, SecurityError, AIError, 
    ValidationError, ConfigurationError, NetworkError, ResourceError,
    BusinessLogicError, wrap_exception, get_exception_context
)
from logger import get_logger, set_request_context, get_request_context


class ErrorHandlerMiddleware:
    """
    Comprehensive error handling middleware for Flask applications.
    
    Provides structured error responses, logging, and monitoring
    for all types of errors in the application.
    """
    
    def __init__(self, app: Flask, logger=None):
        """
        Initialize the error handler middleware.
        
        Args:
            app: Flask application instance
            logger: Logger instance (optional)
        """
        self.app = app
        self.logger = logger or get_logger("error_handler")
        
        # Register error handlers
        self._register_error_handlers()
        
        # Register request middleware
        self._register_request_middleware()
    
    def _register_error_handlers(self):
        """Register error handlers for different exception types."""
        
        @self.app.errorhandler(LegalAssistantError)
        def handle_legal_assistant_error(error: LegalAssistantError):
            """Handle custom LegalAssistantError exceptions."""
            return self._handle_custom_error(error)
        
        @self.app.errorhandler(DatabaseError)
        def handle_database_error(error: DatabaseError):
            """Handle database-related errors."""
            return self._handle_database_error(error)
        
        @self.app.errorhandler(SecurityError)
        def handle_security_error(error: SecurityError):
            """Handle security-related errors."""
            return self._handle_security_error(error)
        
        @self.app.errorhandler(AIError)
        def handle_ai_error(error: AIError):
            """Handle AI/ML-related errors."""
            return self._handle_ai_error(error)
        
        @self.app.errorhandler(ValidationError)
        def handle_validation_error(error: ValidationError):
            """Handle validation errors."""
            return self._handle_validation_error(error)
        
        @self.app.errorhandler(ConfigurationError)
        def handle_configuration_error(error: ConfigurationError):
            """Handle configuration errors."""
            return self._handle_configuration_error(error)
        
        @self.app.errorhandler(NetworkError)
        def handle_network_error(error: NetworkError):
            """Handle network-related errors."""
            return self._handle_network_error(error)
        
        @self.app.errorhandler(ResourceError)
        def handle_resource_error(error: ResourceError):
            """Handle resource-related errors."""
            return self._handle_resource_error(error)
        
        @self.app.errorhandler(BusinessLogicError)
        def handle_business_logic_error(error: BusinessLogicError):
            """Handle business logic errors."""
            return self._handle_business_logic_error(error)
        
        @self.app.errorhandler(HTTPException)
        def handle_http_error(error: HTTPException):
            """Handle HTTP exceptions."""
            return self._handle_http_error(error)
        
        @self.app.errorhandler(Exception)
        def handle_generic_error(error: Exception):
            """Handle all other exceptions."""
            return self._handle_generic_error(error)
    
    def _register_request_middleware(self):
        """Register request middleware for context tracking."""
        
        @self.app.before_request
        def before_request():
            """Set up request context and tracking."""
            # Generate request ID
            request_id = str(uuid.uuid4())
            g.request_id = request_id
            
            # Set request context for logging
            set_request_context(
                request_id=request_id,
                user_id=getattr(g, 'user_id', None),
                session_id=getattr(g, 'session_id', None)
            )
            
            # Log request start
            self.logger.info(
                f"Request started: {request.method} {request.path}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.path,
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent')
                }
            )
        
        @self.app.after_request
        def after_request(response):
            """Log request completion and add headers."""
            request_id = getattr(g, 'request_id', None)
            
            # Add request ID to response headers
            if request_id:
                response.headers['X-Request-ID'] = request_id
            
            # Log request completion
            self.logger.info(
                f"Request completed: {request.method} {request.path} - {response.status_code}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'response_size': len(response.get_data())
                }
            )
            
            return response
    
    def _handle_custom_error(self, error: LegalAssistantError) -> tuple:
        """Handle custom LegalAssistantError exceptions."""
        # Log the error
        self.logger.log_exception(error, get_request_context())
        
        # Determine HTTP status code based on error type
        status_code = self._get_status_code_for_error(error)
        
        # Create error response
        response_data = {
            'error': {
                'type': error.__class__.__name__,
                'code': error.error_code,
                'message': error.message,
                'timestamp': error.timestamp.isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        # Add context in development mode
        if current_app.debug:
            response_data['error']['context'] = error.context
            if error.original_exception:
                response_data['error']['original_exception'] = str(error.original_exception)
        
        return jsonify(response_data), status_code
    
    def _handle_database_error(self, error: DatabaseError) -> tuple:
        """Handle database-related errors."""
        self.logger.log_exception(error, get_request_context())
        
        # Don't expose database details in production
        if current_app.debug:
            message = error.message
        else:
            message = "Database operation failed"
        
        response_data = {
            'error': {
                'type': 'DatabaseError',
                'code': error.error_code,
                'message': message,
                'timestamp': error.timestamp.isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        return jsonify(response_data), 500
    
    def _handle_security_error(self, error: SecurityError) -> tuple:
        """Handle security-related errors."""
        self.logger.log_security_event(
            event_type="SECURITY_ERROR",
            description=error.message,
            severity="ERROR",
            context=get_request_context()
        )
        
        # Don't expose security details
        response_data = {
            'error': {
                'type': 'SecurityError',
                'code': 'SECURITY_ERROR',
                'message': 'Security operation failed',
                'timestamp': error.timestamp.isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        return jsonify(response_data), 403
    
    def _handle_ai_error(self, error: AIError) -> tuple:
        """Handle AI/ML-related errors."""
        self.logger.log_exception(error, get_request_context())
        
        response_data = {
            'error': {
                'type': 'AIError',
                'code': error.error_code,
                'message': error.message,
                'timestamp': error.timestamp.isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        return jsonify(response_data), 500
    
    def _handle_validation_error(self, error: ValidationError) -> tuple:
        """Handle validation errors."""
        self.logger.log_exception(error, get_request_context())
        
        response_data = {
            'error': {
                'type': 'ValidationError',
                'code': error.error_code,
                'message': error.message,
                'timestamp': error.timestamp.isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        # Add validation details
        if error.context.get('field'):
            response_data['error']['field'] = error.context['field']
        
        return jsonify(response_data), 400
    
    def _handle_configuration_error(self, error: ConfigurationError) -> tuple:
        """Handle configuration errors."""
        self.logger.log_exception(error, get_request_context())
        
        response_data = {
            'error': {
                'type': 'ConfigurationError',
                'code': error.error_code,
                'message': 'Configuration error occurred',
                'timestamp': error.timestamp.isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        return jsonify(response_data), 500
    
    def _handle_network_error(self, error: NetworkError) -> tuple:
        """Handle network-related errors."""
        self.logger.log_exception(error, get_request_context())
        
        response_data = {
            'error': {
                'type': 'NetworkError',
                'code': error.error_code,
                'message': 'Network operation failed',
                'timestamp': error.timestamp.isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        return jsonify(response_data), 503
    
    def _handle_resource_error(self, error: ResourceError) -> tuple:
        """Handle resource-related errors."""
        self.logger.log_exception(error, get_request_context())
        
        response_data = {
            'error': {
                'type': 'ResourceError',
                'code': error.error_code,
                'message': error.message,
                'timestamp': error.timestamp.isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        return jsonify(response_data), 404
    
    def _handle_business_logic_error(self, error: BusinessLogicError) -> tuple:
        """Handle business logic errors."""
        self.logger.log_exception(error, get_request_context())
        
        response_data = {
            'error': {
                'type': 'BusinessLogicError',
                'code': error.error_code,
                'message': error.message,
                'timestamp': error.timestamp.isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        return jsonify(response_data), 400
    
    def _handle_http_error(self, error: HTTPException) -> tuple:
        """Handle HTTP exceptions."""
        self.logger.warning(
            f"HTTP error: {error.code} - {error.description}",
            extra={
                'status_code': error.code,
                'description': error.description,
                **get_request_context()
            }
        )
        
        response_data = {
            'error': {
                'type': 'HTTPError',
                'code': f'HTTP_{error.code}',
                'message': error.description,
                'timestamp': datetime.now().isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        return jsonify(response_data), error.code
    
    def _handle_generic_error(self, error: Exception) -> tuple:
        """Handle all other exceptions."""
        # Wrap generic exception
        wrapped_error = wrap_exception(error, context=get_request_context())
        
        self.logger.log_exception(wrapped_error, get_request_context())
        
        # Don't expose internal details in production
        if current_app.debug:
            message = str(error)
            include_traceback = True
        else:
            message = "An unexpected error occurred"
            include_traceback = False
        
        response_data = {
            'error': {
                'type': 'InternalError',
                'code': 'INTERNAL_ERROR',
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        if include_traceback:
            response_data['error']['traceback'] = traceback.format_exc()
        
        return jsonify(response_data), 500
    
    def _get_status_code_for_error(self, error: LegalAssistantError) -> int:
        """Get appropriate HTTP status code for error type."""
        error_type = type(error)
        
        if issubclass(error_type, ValidationError):
            return 400
        elif issubclass(error_type, SecurityError):
            return 403
        elif issubclass(error_type, ResourceError):
            return 404
        elif issubclass(error_type, BusinessLogicError):
            return 400
        elif issubclass(error_type, NetworkError):
            return 503
        elif issubclass(error_type, (DatabaseError, AIError, ConfigurationError)):
            return 500
        else:
            return 500


def init_error_handling(app: Flask, logger=None):
    """
    Initialize error handling for a Flask application.
    
    Args:
        app: Flask application instance
        logger: Logger instance (optional)
    
    Returns:
        ErrorHandlerMiddleware instance
    """
    return ErrorHandlerMiddleware(app, logger)


# Decorator for automatic error handling
def handle_errors(logger=None):
    """
    Decorator for automatic error handling in route functions.
    
    Args:
        logger: Logger instance (optional)
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            log = logger or get_logger()
            
            try:
                return func(*args, **kwargs)
            except LegalAssistantError as e:
                # Re-raise custom exceptions (they'll be handled by the middleware)
                raise
            except Exception as e:
                # Wrap and re-raise generic exceptions
                wrapped_error = wrap_exception(e, context=get_request_context())
                log.log_exception(wrapped_error, get_request_context())
                raise wrapped_error
        
        return wrapper
    return decorator


# Context manager for error handling
class ErrorContext:
    """
    Context manager for error handling with automatic logging.
    """
    
    def __init__(self, operation: str, logger=None, context: Optional[Dict[str, Any]] = None):
        """
        Initialize error context.
        
        Args:
            operation: Name of the operation being performed
            logger: Logger instance (optional)
            context: Additional context information
        """
        self.operation = operation
        self.logger = logger or get_logger()
        self.context = context or {}
        self.start_time = None
    
    def __enter__(self):
        """Enter the error context."""
        self.start_time = datetime.now()
        self.logger.debug(f"Starting operation: {self.operation}", extra=self.context)
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Exit the error context with error handling."""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            # Operation completed successfully
            self.logger.info(
                f"Operation completed: {self.operation}",
                extra={
                    'operation': self.operation,
                    'duration': duration,
                    'status': 'success',
                    **self.context
                }
            )
        else:
            # Operation failed
            if isinstance(exc_value, LegalAssistantError):
                self.logger.log_exception(exc_value, {
                    'operation': self.operation,
                    'duration': duration,
                    'status': 'failed',
                    **self.context
                })
            else:
                wrapped_error = wrap_exception(
                    exc_value,
                    context={
                        'operation': self.operation,
                        'duration': duration,
                        'status': 'failed',
                        **self.context
                    }
                )
                self.logger.log_exception(wrapped_error)
            
            # Re-raise the exception
            return False 