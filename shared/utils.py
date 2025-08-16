"""
Shared Utilities for Legal Assistant AI Platform Microservices

Provides common utility functions used across all services.
"""

import os
import re
import json
import hashlib
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
import jwt
import bcrypt

from .models import SecurityContext, ServiceResponse, AuditEvent


def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """Set up logging for a service."""
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(f"{log_dir}/{service_name}.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def validate_input(user_input: str, max_length: int = 10000) -> tuple[bool, Optional[str], List[str]]:
    """
    Validate user input for security.
    
    Returns:
        Tuple of (is_valid, sanitized_input, errors)
    """
    errors = []
    
    # Check for None or empty input
    if not user_input or not user_input.strip():
        return False, None, ["Input cannot be empty"]
    
    # Check length
    if len(user_input) > max_length:
        errors.append(f"Input too long (max {max_length} characters)")
    
    # Check for forbidden patterns
    forbidden_patterns = [
        r'<script.*?>.*?</script>',  # Script tags
        r'javascript:',              # JavaScript protocol
        r'data:text/html',           # Data URLs
        r'vbscript:',                # VBScript
        r'on\w+\s*=',                # Event handlers
        r'<iframe.*?>',              # Iframe tags
        r'<object.*?>',              # Object tags
        r'<embed.*?>',               # Embed tags
        r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',  # SQL keywords
        r'(\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|ipconfig)\b)',  # System commands
        r'\.\./',                     # Directory traversal
        r'\.\.\\',                    # Windows directory traversal
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            errors.append(f"Security violation: forbidden pattern detected")
            break
    
    if errors:
        return False, None, errors
    
    # Sanitize input
    sanitized = sanitize_input(user_input)
    
    return True, sanitized, []


def sanitize_input(user_input: str) -> str:
    """Sanitize user input while preserving legal terminology."""
    # Remove dangerous characters and sequences
    sanitized = user_input.strip()
    
    # Remove HTML/XML tags
    sanitized = re.sub(r'<[^>]*>', '', sanitized)
    
    # Remove dangerous characters but preserve legal punctuation
    sanitized = re.sub(r'[<>"\']', '', sanitized)
    
    # Remove multiple consecutive special characters
    sanitized = re.sub(r'[;=&\|]{2,}', '', sanitized)
    
    # Remove URL schemes except http/https
    sanitized = re.sub(r'(?!https?://)[a-zA-Z]+://', '', sanitized)
    
    # Remove JavaScript and data URLs
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'data:text/html', '', sanitized, flags=re.IGNORECASE)
    
    # Remove path traversal attempts
    sanitized = re.sub(r'\.\./', '', sanitized)
    sanitized = re.sub(r'\.\.\\', '', sanitized)
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Normalize common legal abbreviations
    sanitized = re.sub(r'\bvs\.\b', 'versus', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'\bet al\.\b', 'et alii', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()


def generate_id() -> str:
    """Generate a secure random ID."""
    return secrets.token_hex(16)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode())


def generate_jwt_token(payload: Dict[str, Any], secret: str, expiry_hours: int = 24) -> str:
    """Generate a JWT token."""
    payload.update({
        'exp': datetime.now(timezone.utc) + timedelta(hours=expiry_hours),
        'iat': datetime.now(timezone.utc)
    })
    return jwt.encode(payload, secret, algorithm='HS256')


def verify_jwt_token(token: str, secret: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        return jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return None


def extract_security_context(token: str, secret: str) -> Optional[SecurityContext]:
    """Extract security context from JWT token."""
    payload = verify_jwt_token(token, secret)
    if not payload:
        return None
    
    return SecurityContext(
        user_id=payload.get('user_id'),
        username=payload.get('username'),
        role=payload.get('role'),
        session_id=payload.get('session_id'),
        permissions=payload.get('permissions', []),
        ip_address=payload.get('ip_address')
    )


def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This would be implemented in each service
        # based on their specific authentication needs
        return f(*args, **kwargs)
    return decorated_function


def require_role(required_role: str):
    """Decorator to require specific role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would be implemented in each service
            # based on their specific authorization needs
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def create_service_response(
    success: bool,
    data: Any = None,
    error: str = None,
    message: str = None
) -> ServiceResponse:
    """Create a standardized service response."""
    return ServiceResponse(
        success=success,
        data=data,
        error=error,
        message=message
    )


def create_audit_event(
    service_name: str,
    event_type: str,
    user_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Dict[str, Any] = None,
    ip_address: Optional[str] = None,
    success: bool = True
) -> AuditEvent:
    """Create an audit event."""
    return AuditEvent(
        id=generate_id(),
        service_name=service_name,
        event_type=event_type,
        user_id=user_id,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
        success=success
    )


def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format."""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))


def safe_json_dumps(obj: Any) -> str:
    """Safely serialize object to JSON."""
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)
    
    return json.dumps(obj, default=default_serializer, ensure_ascii=False)


def calculate_hash(data: str) -> str:
    """Calculate SHA-256 hash of data."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def mask_sensitive_data(data: str, mask_char: str = '*') -> str:
    """Mask sensitive data in strings."""
    # Mask email addresses
    data = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 
                  lambda m: m.group(0)[:3] + mask_char * (len(m.group(0)) - 6) + m.group(0)[-3:], data)
    
    # Mask phone numbers
    data = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 
                  lambda m: m.group(0)[:3] + mask_char * (len(m.group(0)) - 6) + m.group(0)[-3:], data)
    
    return data


def rate_limit_key(user_id: str, action: str) -> str:
    """Generate rate limiting key."""
    return f"rate_limit:{user_id}:{action}"


def is_valid_filename(filename: str) -> bool:
    """Check if filename is valid and safe."""
    # Check for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    if any(char in filename for char in dangerous_chars):
        return False
    
    # Check for reserved names (Windows)
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
    if filename.upper() in reserved_names:
        return False
    
    # Check length
    if len(filename) > 255:
        return False
    
    return True


def get_file_extension(filename: str) -> str:
    """Get file extension safely."""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file type is allowed."""
    extension = get_file_extension(filename)
    return extension in allowed_extensions


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def get_client_ip(request) -> str:
    """Extract client IP address from request."""
    # Check for forwarded headers
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fallback to remote address
    return request.remote_addr or 'unknown' 