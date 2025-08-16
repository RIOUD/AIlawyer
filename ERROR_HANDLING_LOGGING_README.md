# Error Handling and Logging Strategy - Legal Assistant AI Platform

This document outlines the comprehensive error handling and logging strategy implemented for the Legal Assistant AI Platform, addressing the inconsistent error handling patterns identified in the code review.

## 🔧 **Architecture Overview**

### **Exception Hierarchy** (`exceptions.py`)
- **Base Exception**: `LegalAssistantError` with context, severity, and structured information
- **Category-Specific Exceptions**: Database, Security, AI/ML, Validation, Configuration, Network, Resource, Business Logic
- **Context-Aware**: Automatic request tracking and user session information
- **Structured Data**: JSON-serializable error information for logging and monitoring

### **Logging System** (`logger.py`)
- **Structured Logging**: JSON format for log aggregation systems
- **Multiple Handlers**: Console, file, JSON, security, and performance logs
- **Log Rotation**: Automatic file rotation with configurable size limits
- **Context Tracking**: Request ID, user ID, session ID propagation
- **Performance Monitoring**: Automatic timing and metrics collection

### **Error Handler Middleware** (`error_handler.py`)
- **Flask Integration**: Comprehensive error handling for web requests
- **Structured Responses**: Consistent JSON error responses
- **Security Protection**: No sensitive information exposure in production
- **Request Tracking**: Automatic request ID generation and logging

## 🚀 **Quick Start**

### **1. Basic Usage**

```python
from exceptions import ValidationError, DatabaseError
from logger import get_logger, ErrorContext
from error_handler import handle_errors

# Get logger
logger = get_logger("my_module")

# Use error context
with ErrorContext("database_operation", logger):
    # Your code here
    if not data:
        raise ValidationError("Data is required", field="data")
    
    # Database operation
    result = database.query(data)
    logger.info("Database operation completed successfully")

# Use decorator for automatic error handling
@handle_errors(logger)
def my_function():
    # Function with automatic error handling
    pass
```

### **2. Flask Integration**

```python
from flask import Flask
from error_handler import init_error_handling

app = Flask(__name__)
error_handler = init_error_handling(app)

@app.route('/api/data')
@handle_errors()
def get_data():
    # Automatic error handling and logging
    return {"data": "example"}
```

### **3. Custom Exceptions**

```python
from exceptions import LegalAssistantError

class MyCustomError(LegalAssistantError):
    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="MY_CUSTOM_ERROR", **kwargs)

# Usage
raise MyCustomError("Something went wrong", context={"detail": "info"})
```

## 📊 **Exception Categories**

### **Database Exceptions**
- `DatabaseError`: Base database exception
- `DatabaseConnectionError`: Connection failures
- `DatabaseQueryError`: Query execution failures
- `DatabaseConstraintError`: Constraint violations

### **Security Exceptions**
- `SecurityError`: Base security exception
- `AuthenticationError`: Authentication failures
- `AuthorizationError`: Authorization failures
- `EncryptionError`: Encryption/decryption failures

### **AI/ML Exceptions**
- `AIError`: Base AI exception
- `ModelLoadError`: Model loading failures
- `EmbeddingError`: Embedding operation failures
- `VectorStoreError`: Vector store operation failures
- `LLMError`: LLM operation failures

### **Validation Exceptions**
- `ValidationError`: Base validation exception
- `InputValidationError`: Input validation failures
- `QueryValidationError`: Query validation failures

### **Configuration Exceptions**
- `ConfigurationError`: Configuration issues
- `EnvironmentError`: Missing environment variables

### **Network Exceptions**
- `NetworkError`: Base network exception
- `APIError`: API call failures
- `ConnectionError`: Connection failures

### **Resource Exceptions**
- `ResourceError`: Base resource exception
- `FileNotFoundError`: File not found
- `PermissionError`: Permission denied

### **Business Logic Exceptions**
- `BusinessLogicError`: Base business logic exception
- `SessionError`: Session management failures
- `TemplateError`: Template operation failures

## 🔍 **Logging Features**

### **Structured Logging**
```json
{
  "timestamp": "2025-08-16T10:30:00.123456",
  "level": "ERROR",
  "logger": "legal_assistant.web",
  "message": "[VALIDATION_ERROR] Query cannot be empty",
  "module": "web_app",
  "function": "process_query",
  "line": 45,
  "thread_id": 12345,
  "process_id": 67890,
  "context": {
    "request_id": "uuid-1234-5678",
    "user_id": "user123",
    "session_id": "session456"
  },
  "error_code": "VALIDATION_ERROR",
  "field": "query"
}
```

### **Log Categories**
- **General Logs**: `legal_assistant.log`
- **Error Logs**: `errors.log`
- **Security Logs**: `security.log`
- **Structured Logs**: `structured.log`
- **Performance Logs**: `performance.log`

### **Log Levels**
- **DEBUG**: Detailed debugging information
- **INFO**: General information messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical error messages

## 🛠️ **Configuration**

### **Environment Variables**
```bash
# Logging configuration
LOG_LEVEL=INFO
LOG_DIR=./logs
LOG_CONSOLE=true
LOG_FILE=true
LOG_JSON=true

# Flask environment
FLASK_ENV=development
```

### **Logging Configuration**
```python
from logging_config import setup_logging

# Setup for different environments
setup_logging(environment="production", log_dir="logs")
```

## 📈 **Monitoring and Observability**

### **Request Tracking**
- **Request ID**: Automatically generated for each request
- **User Context**: User ID and session ID tracking
- **Performance Metrics**: Request duration and response size
- **Error Correlation**: Link errors to specific requests

### **Performance Monitoring**
```python
from logger import log_function_call

@log_function_call()
def expensive_operation():
    # Function execution is automatically logged with timing
    pass
```

### **Security Monitoring**
```python
from logger import get_logger

logger = get_logger("security")
logger.log_security_event(
    event_type="LOGIN_ATTEMPT",
    description="User login attempt",
    severity="INFO",
    user_id="user123",
    ip_address="192.168.1.1"
)
```

## 🔒 **Security Features**

### **Error Information Protection**
- **Development Mode**: Full error details and stack traces
- **Production Mode**: Generic error messages, no sensitive data
- **Security Events**: Separate logging for security-related events
- **Audit Trail**: Complete audit trail for all operations

### **Input Validation**
```python
from exceptions import InputValidationError

def validate_user_input(data):
    if not data.get('query'):
        raise InputValidationError(
            "Query is required",
            field="query",
            value=data.get('query')
        )
```

## 📋 **Best Practices**

### **1. Exception Handling**
```python
# Good: Specific exception handling
try:
    result = database.query(data)
except DatabaseConnectionError as e:
    logger.error("Database connection failed", extra=e.to_dict())
    raise
except DatabaseQueryError as e:
    logger.error("Database query failed", extra=e.to_dict())
    raise

# Avoid: Generic exception handling
try:
    result = database.query(data)
except Exception as e:
    print(f"Error: {e}")  # Don't do this
```

### **2. Logging**
```python
# Good: Structured logging with context
logger.info(
    "User query processed",
    extra={
        'user_id': user_id,
        'query_length': len(query),
        'processing_time': duration
    }
)

# Avoid: Simple print statements
print("Query processed")  # Don't do this
```

### **3. Error Context**
```python
# Good: Use error context for operations
with ErrorContext("document_processing", logger):
    result = process_document(document)
    logger.info("Document processed successfully")

# Good: Use decorators for automatic handling
@handle_errors(logger)
def api_endpoint():
    return process_request()
```

## 🔧 **Troubleshooting**

### **Common Issues**

**1. Missing Log Files**
```bash
# Check log directory permissions
ls -la logs/
chmod 755 logs/

# Check disk space
df -h
```

**2. High Log Volume**
```python
# Adjust log levels
LOG_LEVEL=WARNING  # Reduce log verbosity

# Configure log rotation
maxBytes=10485760  # 10MB
backupCount=5      # Keep 5 backup files
```

**3. Performance Impact**
```python
# Use async logging for high-volume operations
import asyncio
from logger import get_logger

async def log_async(message):
    logger = get_logger()
    await asyncio.to_thread(logger.info, message)
```

### **Debugging**

**1. Enable Debug Logging**
```python
import logging
logging.getLogger('legal_assistant').setLevel(logging.DEBUG)
```

**2. Check Log Files**
```bash
# Monitor logs in real-time
tail -f logs/legal_assistant.log

# Search for specific errors
grep "ERROR" logs/errors.log

# Check security events
grep "SECURITY_EVENT" logs/security.log
```

**3. Analyze Structured Logs**
```bash
# Parse JSON logs
jq '.level' logs/structured.log | sort | uniq -c

# Find slow operations
jq 'select(.duration > 1.0)' logs/structured.log
```

## 📊 **Metrics and Monitoring**

### **Key Metrics**
- **Error Rate**: Percentage of requests with errors
- **Response Time**: Average and percentile response times
- **Throughput**: Requests per second
- **Resource Usage**: CPU, memory, disk usage

### **Alerting**
```python
# Example alerting configuration
ALERT_THRESHOLDS = {
    'error_rate': 0.05,      # 5% error rate
    'response_time': 2.0,    # 2 second response time
    'disk_usage': 0.9        # 90% disk usage
}
```

## 🔗 **Integration**

### **CI/CD Integration**
```yaml
# GitHub Actions example
- name: Run tests with logging
  run: |
    LOG_LEVEL=DEBUG python -m pytest tests/
    
- name: Check log files
  run: |
    python -c "from logging_config import setup_logging; setup_logging()"
```

### **Monitoring Tools**
- **ELK Stack**: Elasticsearch, Logstash, Kibana
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking

## 📚 **API Reference**

### **Exception Classes**
See `exceptions.py` for complete exception hierarchy.

### **Logger Methods**
```python
logger.debug(message, **kwargs)
logger.info(message, **kwargs)
logger.warning(message, **kwargs)
logger.error(message, **kwargs)
logger.critical(message, **kwargs)

# Specialized methods
logger.log_exception(exception, context=None)
logger.log_security_event(event_type, description, severity="INFO", context=None)
logger.log_performance(operation, duration, context=None)
logger.log_user_action(action, user_id=None, session_id=None, context=None)
logger.log_database_operation(operation, table=None, duration=None, context=None)
logger.log_ai_operation(operation, model=None, duration=None, context=None)
```

### **Error Handler Methods**
```python
init_error_handling(app, logger=None)
handle_errors(logger=None)
ErrorContext(operation, logger=None, context=None)
```

---

**Status**: ✅ ERROR HANDLING AND LOGGING IMPLEMENTED
**Coverage**: 🔒 COMPREHENSIVE (All Exception Types)
**Integration**: 🔗 FULL (Flask, Database, AI/ML, Security)
**Monitoring**: 📊 COMPLETE (Structured Logging, Metrics, Alerting) 