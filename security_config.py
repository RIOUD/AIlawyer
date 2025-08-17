#!/usr/bin/env python3
"""
Security Configuration for Legal Assistant AI Platform

Manages environment variables, secrets, and security settings
with proper validation and fallback mechanisms.
"""

import os
import secrets
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class SecurityConfig:
    """Centralized security configuration management."""
    
    def __init__(self, validate_required: bool = True):
        """Initialize security configuration with validation."""
        if validate_required:
            self._validate_required_vars()
        self._set_defaults()
    
    def _validate_required_vars(self):
        """Validate that all required environment variables are set."""
        required_vars = [
            'SECRET_KEY',
            'MASTER_PASSWORD',
            'OLLAMA_BASE_URL'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {missing_vars}\n"
                "Please set these in your .env file or environment:\n"
                "SECRET_KEY=your-secret-key\n"
                "MASTER_PASSWORD=your-master-password\n"
                "OLLAMA_BASE_URL=http://localhost:11434"
            )
    
    def _set_defaults(self):
        """Set default values for optional configuration."""
        self.secret_key = os.getenv('SECRET_KEY')
        self.master_password = os.getenv('MASTER_PASSWORD')
        self.ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        # Security settings with defaults
        self.security_enabled = os.getenv('SECURITY_ENABLED', 'true').lower() == 'true'
        self.enable_audit_logging = os.getenv('ENABLE_AUDIT_LOGGING', 'true').lower() == 'true'
        self.session_timeout = int(os.getenv('SESSION_TIMEOUT', '3600'))
        self.max_failed_attempts = int(os.getenv('MAX_FAILED_ATTEMPTS', '5'))
        self.lockout_duration = int(os.getenv('LOCKOUT_DURATION', '900'))
        
        # Database settings
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///legal_assistant.db')
        
        # Vector store settings
        self.vector_store_path = os.getenv('VECTOR_STORE_PATH', './chroma_db')
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'mistral:7b')
        
        # File paths
        self.security_dir = os.getenv('SECURITY_DIR', './security')
        self.source_documents_path = os.getenv('SOURCE_DOCUMENTS_PATH', './source_documents')
        self.exports_path = os.getenv('EXPORTS_PATH', './exports')
        
        # Monitoring settings
        self.monitoring_enabled = os.getenv('MONITORING_ENABLED', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            'url': self.database_url,
            'echo': os.getenv('DATABASE_ECHO', 'false').lower() == 'true',
            'pool_size': int(os.getenv('DATABASE_POOL_SIZE', '10')),
            'max_overflow': int(os.getenv('DATABASE_MAX_OVERFLOW', '20')),
            'pool_timeout': int(os.getenv('DATABASE_POOL_TIMEOUT', '30')),
            'pool_recycle': int(os.getenv('DATABASE_POOL_RECYCLE', '3600'))
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration."""
        return {
            'enabled': self.security_enabled,
            'audit_logging': self.enable_audit_logging,
            'session_timeout': self.session_timeout,
            'max_failed_attempts': self.max_failed_attempts,
            'lockout_duration': self.lockout_duration,
            'encryption_algorithm': 'AES-256-GCM',
            'key_derivation_rounds': 100000,
            'secure_delete_passes': 3
        }
    
    def get_vector_store_config(self) -> Dict[str, Any]:
        """Get vector store configuration."""
        return {
            'path': self.vector_store_path,
            'embedding_model': self.embedding_model,
            'max_retrieval_docs': int(os.getenv('MAX_RETRIEVAL_DOCS', '4')),
            'chunk_size': int(os.getenv('CHUNK_SIZE', '1000')),
            'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', '200'))
        }
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama configuration."""
        return {
            'base_url': self.ollama_base_url,
            'model': self.ollama_model,
            'temperature': float(os.getenv('OLLAMA_TEMPERATURE', '0.1')),
            'num_ctx': int(os.getenv('OLLAMA_NUM_CTX', '4096')),
            'repeat_penalty': float(os.getenv('OLLAMA_REPEAT_PENALTY', '1.1'))
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration."""
        return {
            'enabled': self.monitoring_enabled,
            'log_level': self.log_level,
            'metrics_port': int(os.getenv('METRICS_PORT', '9090')),
            'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', '30'))
        }
    
    def validate_secrets(self) -> bool:
        """Validate that all secrets are properly configured."""
        if not self.secret_key or len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        
        if not self.master_password or len(self.master_password) < 12:
            raise ValueError("MASTER_PASSWORD must be at least 12 characters long")
        
        return True
    
    def generate_secure_secret_key(self) -> str:
        """Generate a secure secret key for Flask."""
        return secrets.token_urlsafe(32)
    
    def create_env_template(self, output_path: str = '.env.template'):
        """Create a template .env file with all required variables."""
        template_content = """# Legal Assistant AI Platform - Environment Configuration
# Copy this file to .env and fill in your values

# Required Security Settings
SECRET_KEY=your-secret-key-here-minimum-32-characters
MASTER_PASSWORD=your-master-password-here-minimum-12-characters
OLLAMA_BASE_URL=http://localhost:11434

# Optional Security Settings
SECURITY_ENABLED=true
ENABLE_AUDIT_LOGGING=true
SESSION_TIMEOUT=3600
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION=900

# Database Configuration
DATABASE_URL=sqlite:///legal_assistant.db
DATABASE_ECHO=false
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Vector Store Configuration
VECTOR_STORE_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
OLLAMA_MODEL=mixtral
MAX_RETRIEVAL_DOCS=4
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Ollama Configuration
OLLAMA_TEMPERATURE=0.1
OLLAMA_NUM_CTX=4096
OLLAMA_REPEAT_PENALTY=1.1

# File Paths
SECURITY_DIR=./security
SOURCE_DOCUMENTS_PATH=./source_documents
EXPORTS_PATH=./exports

# Monitoring Configuration
MONITORING_ENABLED=false
LOG_LEVEL=INFO
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
"""
        
        with open(output_path, 'w') as f:
            f.write(template_content)
        
        print(f"Environment template created: {output_path}")
        print("Please copy this file to .env and configure your values")


# Global configuration instance
try:
    config = SecurityConfig()
except ValueError:
    # For template generation, don't validate required vars
    config = SecurityConfig(validate_required=False)


def get_config() -> SecurityConfig:
    """Get the global security configuration instance."""
    return config


def validate_environment() -> bool:
    """Validate the entire environment configuration."""
    try:
        config.validate_secrets()
        return True
    except ValueError as e:
        print(f"Configuration validation failed: {e}")
        return False


if __name__ == "__main__":
    # Create environment template if run directly
    config.create_env_template() 