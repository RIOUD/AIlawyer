#!/usr/bin/env python3
"""
Database Manager

Database management and data models for the legal practice platform.
Provides SQLAlchemy integration and data persistence.
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Create base class for declarative models
Base = declarative_base()


class Lawyer(Base):
    """Lawyer data model."""
    __tablename__ = "lawyers"
    
    id = Column(Integer, primary_key=True, index=True)
    lawyer_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hourly_rate = Column(Float, default=250.0)
    specialties = Column(Text)  # JSON string
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    time_entries = relationship("TimeEntry", back_populates="lawyer")
    cases = relationship("Case", back_populates="lawyer")
    clients = relationship("Client", back_populates="lawyer")


class Client(Base):
    """Client data model."""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20))
    company = Column(String(100))
    industry = Column(String(50))
    client_type = Column(String(20), default="individual")
    billing_address = Column(Text)
    created_at = Column(DateTime, default=func.now())
    last_contact = Column(DateTime)
    status = Column(String(20), default="active")
    value_tier = Column(String(20), default="bronze")
    lawyer_id = Column(String(50), ForeignKey("lawyers.lawyer_id"))
    
    # Relationships
    lawyer = relationship("Lawyer", back_populates="clients")
    cases = relationship("Case", back_populates="client")
    interactions = relationship("ClientInteraction", back_populates="client")


class TimeEntry(Base):
    """Time entry data model."""
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(String(50), unique=True, index=True, nullable=False)
    lawyer_id = Column(String(50), ForeignKey("lawyers.lawyer_id"), nullable=False)
    activity_type = Column(String(50), nullable=False)
    duration = Column(Float, nullable=False)  # in hours
    description = Column(Text, nullable=False)
    client_matter = Column(String(100))
    billable = Column(Boolean, default=True)
    rate = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    category = Column(String(50), nullable=False)
    session_id = Column(String(50))
    
    # Relationships
    lawyer = relationship("Lawyer", back_populates="time_entries")


class Case(Base):
    """Case data model."""
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(50), unique=True, index=True, nullable=False)
    client_id = Column(String(50), ForeignKey("clients.client_id"), nullable=False)
    case_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")
    priority = Column(String(20), default="medium")
    start_date = Column(DateTime, default=func.now())
    estimated_end_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    estimated_value = Column(Float, default=0.0)
    actual_value = Column(Float)
    lawyer_id = Column(String(50), ForeignKey("lawyers.lawyer_id"), nullable=False)
    assigned_team = Column(Text)  # JSON string
    jurisdiction = Column(String(100))
    court = Column(String(100))
    
    # Relationships
    client = relationship("Client", back_populates="cases")
    lawyer = relationship("Lawyer", back_populates="cases")
    tasks = relationship("CaseTask", back_populates="case")
    milestones = relationship("CaseMilestone", back_populates="case")


class CaseTask(Base):
    """Case task data model."""
    __tablename__ = "case_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(50), unique=True, index=True, nullable=False)
    case_id = Column(String(50), ForeignKey("cases.case_id"), nullable=False)
    task_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="pending")
    priority = Column(String(20), default="medium")
    assigned_to = Column(String(50), nullable=False)
    due_date = Column(DateTime, nullable=False)
    estimated_hours = Column(Float, default=0.0)
    actual_hours = Column(Float)
    dependencies = Column(Text)  # JSON string
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    
    # Relationships
    case = relationship("Case", back_populates="tasks")


class CaseMilestone(Base):
    """Case milestone data model."""
    __tablename__ = "case_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(String(50), unique=True, index=True, nullable=False)
    case_id = Column(String(50), ForeignKey("cases.case_id"), nullable=False)
    milestone_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    target_date = Column(DateTime, nullable=False)
    actual_date = Column(DateTime)
    status = Column(String(20), default="pending")
    importance = Column(String(20), default="standard")
    
    # Relationships
    case = relationship("Case", back_populates="milestones")


class ClientInteraction(Base):
    """Client interaction data model."""
    __tablename__ = "client_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(String(50), unique=True, index=True, nullable=False)
    client_id = Column(String(50), ForeignKey("clients.client_id"), nullable=False)
    interaction_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    duration = Column(Float)  # in minutes
    outcome = Column(String(50), default="positive")
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime)
    lawyer_id = Column(String(50), nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="interactions")


class DocumentWorkflow(Base):
    """Document workflow data model."""
    __tablename__ = "document_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(50), unique=True, index=True, nullable=False)
    document_type = Column(String(50), nullable=False)
    client_data = Column(Text)  # JSON string
    status = Column(String(20), default="draft")
    current_step = Column(Integer, default=1)
    total_steps = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    lawyer_id = Column(String(50), nullable=False)
    client_id = Column(String(50), nullable=False)
    estimated_completion = Column(DateTime)
    priority = Column(String(20), default="medium")


class DocumentStep(Base):
    """Document workflow step data model."""
    __tablename__ = "document_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(String(50), unique=True, index=True, nullable=False)
    workflow_id = Column(String(50), ForeignKey("document_workflows.workflow_id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    step_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")
    description = Column(Text, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    output = Column(Text)  # JSON string
    ai_analysis = Column(Text)  # JSON string


class BusinessMetrics(Base):
    """Business metrics data model."""
    __tablename__ = "business_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    lawyer_id = Column(String(50), nullable=False)
    total_revenue = Column(Float, default=0.0)
    billable_hours = Column(Float, default=0.0)
    client_count = Column(Integer, default=0)
    case_count = Column(Integer, default=0)
    average_case_value = Column(Float, default=0.0)
    client_retention_rate = Column(Float, default=0.0)
    efficiency_score = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=func.now())


class DatabaseManager:
    """
    Database manager for the legal practice platform.
    
    Handles database initialization, session management, and data operations.
    """
    
    def __init__(self, database_url: str = "sqlite:///legal_platform.db"):
        """Initialize database manager."""
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and session."""
        try:
            # Create engine
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            logger.info(f"Database initialized: {self.database_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def initialize_database(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session."""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Close database session."""
        if session:
            session.close()
    
    def add_lawyer(self, lawyer_id: str, name: str, email: str, 
                  hourly_rate: float = 250.0, specialties: list = None) -> Dict[str, Any]:
        """Add a new lawyer to the database."""
        session = self.get_session()
        try:
            lawyer = Lawyer(
                lawyer_id=lawyer_id,
                name=name,
                email=email,
                hourly_rate=hourly_rate,
                specialties=json.dumps(specialties) if specialties else None
            )
            
            session.add(lawyer)
            session.commit()
            session.refresh(lawyer)
            
            logger.info(f"Lawyer added: {name} ({lawyer_id})")
            return {
                "lawyer_id": lawyer.lawyer_id,
                "name": lawyer.name,
                "email": lawyer.email,
                "hourly_rate": lawyer.hourly_rate,
                "created_at": lawyer.created_at.isoformat()
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding lawyer: {e}")
            raise
        finally:
            self.close_session(session)
    
    def add_client(self, client_id: str, name: str, email: str, lawyer_id: str,
                  company: str = None, industry: str = None, 
                  client_type: str = "individual") -> Dict[str, Any]:
        """Add a new client to the database."""
        session = self.get_session()
        try:
            client = Client(
                client_id=client_id,
                name=name,
                email=email,
                lawyer_id=lawyer_id,
                company=company,
                industry=industry,
                client_type=client_type
            )
            
            session.add(client)
            session.commit()
            session.refresh(client)
            
            logger.info(f"Client added: {name} ({client_id})")
            return {
                "client_id": client.client_id,
                "name": client.name,
                "email": client.email,
                "lawyer_id": client.lawyer_id,
                "created_at": client.created_at.isoformat()
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding client: {e}")
            raise
        finally:
            self.close_session(session)
    
    def add_time_entry(self, entry_id: str, lawyer_id: str, activity_type: str,
                      duration: float, description: str, rate: float,
                      category: str, client_matter: str = None,
                      billable: bool = True) -> Dict[str, Any]:
        """Add a new time entry to the database."""
        session = self.get_session()
        try:
            time_entry = TimeEntry(
                entry_id=entry_id,
                lawyer_id=lawyer_id,
                activity_type=activity_type,
                duration=duration,
                description=description,
                rate=rate,
                category=category,
                client_matter=client_matter,
                billable=billable
            )
            
            session.add(time_entry)
            session.commit()
            session.refresh(time_entry)
            
            logger.info(f"Time entry added: {activity_type} ({duration}h)")
            return {
                "entry_id": time_entry.entry_id,
                "lawyer_id": time_entry.lawyer_id,
                "activity_type": time_entry.activity_type,
                "duration": time_entry.duration,
                "billable_amount": time_entry.duration * time_entry.rate if time_entry.billable else 0
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding time entry: {e}")
            raise
        finally:
            self.close_session(session)
    
    def add_case(self, case_id: str, client_id: str, case_type: str, title: str,
                lawyer_id: str, description: str = None, priority: str = "medium",
                estimated_value: float = 0.0) -> Dict[str, Any]:
        """Add a new case to the database."""
        session = self.get_session()
        try:
            case = Case(
                case_id=case_id,
                client_id=client_id,
                case_type=case_type,
                title=title,
                lawyer_id=lawyer_id,
                description=description,
                priority=priority,
                estimated_value=estimated_value
            )
            
            session.add(case)
            session.commit()
            session.refresh(case)
            
            logger.info(f"Case added: {title} ({case_id})")
            return {
                "case_id": case.case_id,
                "title": case.title,
                "case_type": case.case_type,
                "status": case.status,
                "priority": case.priority,
                "created_at": case.start_date.isoformat()
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding case: {e}")
            raise
        finally:
            self.close_session(session)
    
    def get_lawyer_time_entries(self, lawyer_id: str, limit: int = 100) -> list:
        """Get time entries for a lawyer."""
        session = self.get_session()
        try:
            entries = session.query(TimeEntry).filter(
                TimeEntry.lawyer_id == lawyer_id
            ).order_by(TimeEntry.timestamp.desc()).limit(limit).all()
            
            return [
                {
                    "entry_id": entry.entry_id,
                    "activity_type": entry.activity_type,
                    "duration": entry.duration,
                    "description": entry.description,
                    "billable": entry.billable,
                    "rate": entry.rate,
                    "timestamp": entry.timestamp.isoformat()
                }
                for entry in entries
            ]
            
        except Exception as e:
            logger.error(f"Error getting time entries: {e}")
            raise
        finally:
            self.close_session(session)
    
    def get_lawyer_cases(self, lawyer_id: str) -> list:
        """Get cases for a lawyer."""
        session = self.get_session()
        try:
            cases = session.query(Case).filter(
                Case.lawyer_id == lawyer_id
            ).order_by(Case.start_date.desc()).all()
            
            return [
                {
                    "case_id": case.case_id,
                    "title": case.title,
                    "case_type": case.case_type,
                    "status": case.status,
                    "priority": case.priority,
                    "estimated_value": case.estimated_value,
                    "start_date": case.start_date.isoformat()
                }
                for case in cases
            ]
            
        except Exception as e:
            logger.error(f"Error getting cases: {e}")
            raise
        finally:
            self.close_session(session)
    
    def get_lawyer_clients(self, lawyer_id: str) -> list:
        """Get clients for a lawyer."""
        session = self.get_session()
        try:
            clients = session.query(Client).filter(
                Client.lawyer_id == lawyer_id
            ).order_by(Client.created_at.desc()).all()
            
            return [
                {
                    "client_id": client.client_id,
                    "name": client.name,
                    "email": client.email,
                    "company": client.company,
                    "status": client.status,
                    "value_tier": client.value_tier,
                    "created_at": client.created_at.isoformat()
                }
                for client in clients
            ]
            
        except Exception as e:
            logger.error(f"Error getting clients: {e}")
            raise
        finally:
            self.close_session(session)
    
    def add_business_metrics(self, lawyer_id: str, total_revenue: float,
                           billable_hours: float, client_count: int,
                           case_count: int, average_case_value: float,
                           client_retention_rate: float, efficiency_score: float):
        """Add business metrics for a lawyer."""
        session = self.get_session()
        try:
            metrics = BusinessMetrics(
                lawyer_id=lawyer_id,
                total_revenue=total_revenue,
                billable_hours=billable_hours,
                client_count=client_count,
                case_count=case_count,
                average_case_value=average_case_value,
                client_retention_rate=client_retention_rate,
                efficiency_score=efficiency_score
            )
            
            session.add(metrics)
            session.commit()
            
            logger.info(f"Business metrics added for lawyer {lawyer_id}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding business metrics: {e}")
            raise
        finally:
            self.close_session(session) 