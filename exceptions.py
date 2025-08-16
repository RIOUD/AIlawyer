#!/usr/bin/env python3
"""
Exception classes for Secure Offline Legal Assistant

Defines a comprehensive exception hierarchy for proper error handling
and categorization throughout the application.
"""

from typing import Optional, Dict, Any, List


class LegalAssistantError(Exception):
    """Base exception for Legal Assistant application."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ValidationError(LegalAssistantError):
    """Base class for validation errors."""
    pass


class InputValidationError(ValidationError):
    """Raised when user input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[str] = None, errors: Optional[List[str]] = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value
        self.errors = errors or []


class QueryValidationError(ValidationError):
    """Raised when query validation fails."""
    
    def __init__(self, message: str, query: Optional[str] = None, 
                 validation_errors: Optional[List[str]] = None):
        super().__init__(message, "QUERY_VALIDATION_ERROR")
        self.query = query
        self.validation_errors = validation_errors or []


class SecurityError(LegalAssistantError):
    """Base class for security-related errors."""
    pass


class AuthenticationError(SecurityError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, user_id: Optional[str] = None, 
                 failed_attempts: Optional[int] = None):
        super().__init__(message, "AUTHENTICATION_ERROR")
        self.user_id = user_id
        self.failed_attempts = failed_attempts


class AuthorizationError(SecurityError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str, required_permissions: Optional[List[str]] = None,
                 user_permissions: Optional[List[str]] = None):
        super().__init__(message, "AUTHORIZATION_ERROR")
        self.required_permissions = required_permissions or []
        self.user_permissions = user_permissions or []


class EncryptionError(SecurityError):
    """Raised when encryption/decryption operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None,
                 file_path: Optional[str] = None):
        super().__init__(message, "ENCRYPTION_ERROR")
        self.operation = operation
        self.file_path = file_path


class DatabaseError(LegalAssistantError):
    """Base class for database-related errors."""
    pass


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    
    def __init__(self, message: str, db_path: Optional[str] = None):
        super().__init__(message, "DB_CONNECTION_ERROR")
        self.db_path = db_path


class QueryError(DatabaseError):
    """Raised when database query fails."""
    
    def __init__(self, message: str, query: Optional[str] = None,
                 parameters: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DB_QUERY_ERROR")
        self.query = query
        self.parameters = parameters


class EmbeddingError(LegalAssistantError):
    """Raised when embedding model operations fail."""
    
    def __init__(self, message: str, embedding_model: Optional[str] = None,
                 operation: Optional[str] = None):
        super().__init__(message, "EMBEDDING_ERROR")
        self.embedding_model = embedding_model
        self.operation = operation


class VectorStoreError(LegalAssistantError):
    """Raised when vector store operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None,
                 store_path: Optional[str] = None):
        super().__init__(message, "VECTOR_STORE_ERROR")
        self.operation = operation
        self.store_path = store_path


class LLMError(LegalAssistantError):
    """Raised when LLM operations fail."""
    
    def __init__(self, message: str, model_name: Optional[str] = None,
                 operation: Optional[str] = None):
        super().__init__(message, "LLM_ERROR")
        self.model_name = model_name
        self.operation = operation


class DocumentProcessingError(LegalAssistantError):
    """Raised when document processing fails."""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 document_type: Optional[str] = None):
        super().__init__(message, "DOCUMENT_PROCESSING_ERROR")
        self.file_path = file_path
        self.document_type = document_type


class SessionError(LegalAssistantError):
    """Raised when session management fails."""
    
    def __init__(self, message: str, session_id: Optional[str] = None,
                 operation: Optional[str] = None):
        super().__init__(message, "SESSION_ERROR")
        self.session_id = session_id
        self.operation = operation


class TemplateError(LegalAssistantError):
    """Raised when template operations fail."""
    
    def __init__(self, message: str, template_id: Optional[str] = None,
                 operation: Optional[str] = None):
        super().__init__(message, "TEMPLATE_ERROR")
        self.template_id = template_id
        self.operation = operation


class ExportError(LegalAssistantError):
    """Raised when export operations fail."""
    
    def __init__(self, message: str, export_format: Optional[str] = None,
                 file_path: Optional[str] = None):
        super().__init__(message, "EXPORT_ERROR")
        self.export_format = export_format
        self.file_path = file_path


class ConfigurationError(LegalAssistantError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_file: Optional[str] = None):
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_key = config_key
        self.config_file = config_file


class NetworkError(LegalAssistantError):
    """Raised when network operations fail."""
    
    def __init__(self, message: str, url: Optional[str] = None,
                 status_code: Optional[int] = None):
        super().__init__(message, "NETWORK_ERROR")
        self.url = url
        self.status_code = status_code


class ResourceError(LegalAssistantError):
    """Raised when resource operations fail."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 resource_path: Optional[str] = None):
        super().__init__(message, "RESOURCE_ERROR")
        self.resource_type = resource_type
        self.resource_path = resource_path


class AIError(LegalAssistantError):
    """Base class for AI/ML-related errors."""
    pass


class ModelLoadError(AIError):
    """Raised when AI model loading fails."""
    
    def __init__(self, message: str, model_name: Optional[str] = None,
                 model_path: Optional[str] = None):
        super().__init__(message, "MODEL_LOAD_ERROR")
        self.model_name = model_name
        self.model_path = model_path


class EmbeddingError(AIError):
    """Raised when embedding operations fail."""
    
    def __init__(self, message: str, text: Optional[str] = None,
                 embedding_model: Optional[str] = None):
        super().__init__(message, "EMBEDDING_ERROR")
        self.text = text
        self.embedding_model = embedding_model


class VectorStoreError(AIError):
    """Raised when vector store operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None,
                 store_path: Optional[str] = None):
        super().__init__(message, "VECTOR_STORE_ERROR")
        self.operation = operation
        self.store_path = store_path


class LLMError(AIError):
    """Raised when LLM operations fail."""
    
    def __init__(self, message: str, prompt: Optional[str] = None,
                 model_name: Optional[str] = None):
        super().__init__(message, "LLM_ERROR")
        self.prompt = prompt
        self.model_name = model_name


class BusinessLogicError(LegalAssistantError):
    """Raised when business logic operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None,
                 business_rule: Optional[str] = None):
        super().__init__(message, "BUSINESS_LOGIC_ERROR")
        self.operation = operation
        self.business_rule = business_rule


# Error handling utilities
def handle_exception(exception: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Handle exceptions and return structured error information.
    
    Args:
        exception: The exception that occurred
        context: Additional context information
        
    Returns:
        Dictionary with error information
    """
    if isinstance(exception, LegalAssistantError):
        return {
            "success": False,
            "error": exception.message,
            "error_code": exception.error_code,
            "details": exception.details,
            "context": context or {}
        }
    else:
        return {
            "success": False,
            "error": str(exception),
            "error_code": "UNKNOWN_ERROR",
            "details": {},
            "context": context or {}
        }


def is_retryable_error(exception: Exception) -> bool:
    """
    Determine if an error is retryable.
    
    Args:
        exception: The exception to check
        
    Returns:
        True if the error is retryable, False otherwise
    """
    retryable_errors = [
        ConnectionError,
        NetworkError,
        LLMError,
        DatabaseError
    ]
    
    return any(isinstance(exception, error_type) for error_type in retryable_errors)


def get_error_severity(exception: Exception) -> str:
    """
    Get the severity level of an error.
    
    Args:
        exception: The exception to check
        
    Returns:
        Severity level: 'low', 'medium', 'high', 'critical'
    """
    if isinstance(exception, (AuthenticationError, AuthorizationError, SecurityError)):
        return 'critical'
    elif isinstance(exception, (DatabaseError, VectorStoreError)):
        return 'high'
    elif isinstance(exception, (ValidationError, ConfigurationError)):
        return 'medium'
    else:
        return 'low'


def get_exception_context() -> Dict[str, Any]:
    """
    Get the current exception context for logging and debugging.
    
    Returns:
        Dictionary with exception context information
    """
    import traceback
    import sys
    
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    if exc_type is None:
        return {}
    
    return {
        "exception_type": exc_type.__name__,
        "exception_message": str(exc_value),
        "traceback": traceback.format_exc(),
        "frame_info": traceback.extract_tb(exc_traceback)[-1] if exc_traceback else None
    }


def wrap_exception(exception: Exception, context: Optional[Dict[str, Any]] = None) -> LegalAssistantError:
    """
    Wrap a generic exception in a LegalAssistantError with context.
    
    Args:
        exception: The original exception
        context: Additional context information
        
    Returns:
        Wrapped LegalAssistantError
    """
    if isinstance(exception, LegalAssistantError):
        return exception
    
    return LegalAssistantError(
        message=str(exception),
        error_code="WRAPPED_ERROR",
        details={"original_exception": type(exception).__name__, "context": context or {}}
    ) 