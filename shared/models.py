"""
Shared Data Models for Legal Assistant AI Platform

Defines common data structures used across all microservices.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class DocumentType(str, Enum):
    """Document type enumeration."""
    WETBOEKEN = "wetboeken"
    JURISPRUDENTIE = "jurisprudentie"
    CONTRACTEN = "contracten"
    ADVOCATENSTUKKEN = "advocatenstukken"
    RECHTSLEER = "rechtsleer"
    REGLEMENTERING = "reglementering"


class Jurisdiction(str, Enum):
    """Jurisdiction enumeration."""
    FEDERAAL = "federaal"
    VLAAMS = "vlaams"
    WAALS = "waals"
    BRUSSELS = "brussels"
    GEMEENTELIJK = "gemeentelijk"
    PROVINCIAAL = "provinciaal"
    EU = "eu"


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"


@dataclass
class Document:
    """Document data model."""
    id: str
    title: str
    content: str
    document_type: DocumentType
    jurisdiction: Jurisdiction
    language: str
    source_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Query:
    """Query data model."""
    id: str
    user_id: str
    question: str
    answer: Optional[str] = None
    sources: List[Dict[str, Any]] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    processing_time: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class User:
    """User data model."""
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None


@dataclass
class Session:
    """Session data model."""
    id: str
    user_id: str
    token: str
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AuditEvent:
    """Audit event data model."""
    id: str
    service_name: str
    event_type: str
    user_id: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    success: bool = True
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityContext:
    """Security context for inter-service communication."""
    user_id: str
    username: str
    role: UserRole
    session_id: str
    permissions: List[str] = field(default_factory=list)
    ip_address: Optional[str] = None


@dataclass
class ServiceResponse:
    """Standard service response model."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessingRequest:
    """Document processing request model."""
    document_id: str
    operation: str  # 'ingest', 'update', 'delete'
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1=low, 5=high


@dataclass
class QueryRequest:
    """Query processing request model."""
    question: str
    user_id: str
    session_id: str
    filters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1


@dataclass
class QueryResponse:
    """Query processing response model."""
    answer: str
    sources: List[Dict[str, Any]]
    processing_time: float
    confidence_score: float
    related_queries: List[str] = field(default_factory=list) 