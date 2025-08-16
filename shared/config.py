"""
Shared Configuration for Legal Assistant AI Platform Microservices

Provides configuration management utilities used across all services.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "require"
    
    @classmethod
    def from_env(cls, prefix: str = "DB") -> "DatabaseConfig":
        """Create database config from environment variables."""
        return cls(
            host=os.getenv(f"{prefix}_HOST", "localhost"),
            port=int(os.getenv(f"{prefix}_PORT", "5432")),
            database=os.getenv(f"{prefix}_NAME", "legal_assistant"),
            username=os.getenv(f"{prefix}_USER", "postgres"),
            password=os.getenv(f"{prefix}_PASSWORD", ""),
            ssl_mode=os.getenv(f"{prefix}_SSL_MODE", "require")
        )


@dataclass
class SecurityConfig:
    """Security configuration."""
    jwt_secret: str
    jwt_expiry_hours: int
    bcrypt_rounds: int
    max_failed_attempts: int
    lockout_duration_minutes: int
    
    @classmethod
    def from_env(cls) -> "SecurityConfig":
        """Create security config from environment variables."""
        return cls(
            jwt_secret=os.getenv("JWT_SECRET", ""),
            jwt_expiry_hours=int(os.getenv("JWT_EXPIRY_HOURS", "24")),
            bcrypt_rounds=int(os.getenv("BCRYPT_ROUNDS", "100000")),
            max_failed_attempts=int(os.getenv("MAX_FAILED_ATTEMPTS", "5")),
            lockout_duration_minutes=int(os.getenv("LOCKOUT_DURATION", "15"))
        )


@dataclass
class ServiceConfig:
    """Service configuration."""
    name: str
    host: str
    port: int
    debug: bool
    log_level: str
    
    @classmethod
    def from_env(cls, service_name: str) -> "ServiceConfig":
        """Create service config from environment variables."""
        prefix = service_name.upper()
        return cls(
            name=service_name,
            host=os.getenv(f"{prefix}_HOST", "0.0.0.0"),
            port=int(os.getenv(f"{prefix}_PORT", "8000")),
            debug=os.getenv(f"{prefix}_DEBUG", "false").lower() == "true",
            log_level=os.getenv(f"{prefix}_LOG_LEVEL", "INFO")
        )


@dataclass
class RedisConfig:
    """Redis configuration."""
    host: str
    port: int
    password: Optional[str]
    database: int
    
    @classmethod
    def from_env(cls) -> "RedisConfig":
        """Create Redis config from environment variables."""
        return cls(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            database=int(os.getenv("REDIS_DB", "0"))
        )


@dataclass
class OllamaConfig:
    """Ollama configuration."""
    base_url: str
    model: str
    timeout: int
    
    @classmethod
    def from_env(cls) -> "OllamaConfig":
        """Create Ollama config from environment variables."""
        return cls(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "mixtral"),
            timeout=int(os.getenv("OLLAMA_TIMEOUT", "30"))
        )


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""
    path: str
    embedding_model: str
    max_retrieval_docs: int
    
    @classmethod
    def from_env(cls) -> "VectorStoreConfig":
        """Create vector store config from environment variables."""
        return cls(
            path=os.getenv("VECTOR_STORE_PATH", "./chroma_db"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            max_retrieval_docs=int(os.getenv("MAX_RETRIEVAL_DOCS", "4"))
        )


class ConfigManager:
    """Configuration manager for microservices."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.service_config = ServiceConfig.from_env(service_name)
        self.security_config = SecurityConfig.from_env()
        self.redis_config = RedisConfig.from_env()
        self.ollama_config = OllamaConfig.from_env()
        self.vector_store_config = VectorStoreConfig.from_env()
    
    def get_database_config(self, db_name: str) -> DatabaseConfig:
        """Get database configuration for specific database."""
        prefix = f"{db_name.upper()}_DB"
        return DatabaseConfig.from_env(prefix)
    
    def validate(self) -> bool:
        """Validate configuration."""
        errors = []
        
        # Check required environment variables
        if not self.security_config.jwt_secret:
            errors.append("JWT_SECRET is required")
        
        if not os.getenv("SECRET_KEY"):
            errors.append("SECRET_KEY is required")
        
        # Check service-specific requirements
        if self.service_name == "security":
            if not os.getenv("MASTER_PASSWORD"):
                errors.append("MASTER_PASSWORD is required for security service")
        
        if errors:
            print("Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "service": {
                "name": self.service_config.name,
                "host": self.service_config.host,
                "port": self.service_config.port,
                "debug": self.service_config.debug,
                "log_level": self.service_config.log_level
            },
            "security": {
                "jwt_expiry_hours": self.security_config.jwt_expiry_hours,
                "bcrypt_rounds": self.security_config.bcrypt_rounds,
                "max_failed_attempts": self.security_config.max_failed_attempts,
                "lockout_duration_minutes": self.security_config.lockout_duration_minutes
            },
            "redis": {
                "host": self.redis_config.host,
                "port": self.redis_config.port,
                "database": self.redis_config.database
            },
            "ollama": {
                "base_url": self.ollama_config.base_url,
                "model": self.ollama_config.model,
                "timeout": self.ollama_config.timeout
            },
            "vector_store": {
                "path": self.vector_store_config.path,
                "embedding_model": self.vector_store_config.embedding_model,
                "max_retrieval_docs": self.vector_store_config.max_retrieval_docs
            }
        } 