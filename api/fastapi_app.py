#!/usr/bin/env python3
"""
FastAPI Application

FastAPI application with all endpoints for the legal practice platform.
Provides RESTful API for all platform features.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

from config.settings import get_settings

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Pydantic models for API requests/responses
class TimeEntryRequest(BaseModel):
    lawyer_id: str = Field(..., description="Lawyer identifier")
    activity_type: str = Field(..., description="Type of activity")
    duration: float = Field(..., description="Duration in hours")
    description: str = Field(..., description="Activity description")

class BillingSummaryRequest(BaseModel):
    lawyer_id: str = Field(..., description="Lawyer identifier")
    client_id: Optional[str] = Field(None, description="Client identifier (optional)")
    date_range: str = Field("current_month", description="Billing period")

class DeadlineRequest(BaseModel):
    case_id: str = Field(..., description="Case identifier")
    deadline_type: str = Field(..., description="Type of deadline")
    due_date: datetime = Field(..., description="Due date and time")
    description: str = Field(..., description="Deadline description")
    lawyer_id: str = Field(..., description="Lawyer identifier")
    priority: Optional[str] = Field("medium", description="Priority level")

class DocumentWorkflowRequest(BaseModel):
    document_type: str = Field(..., description="Type of document")
    client_data: Dict[str, Any] = Field(..., description="Client information")

class ClientRequest(BaseModel):
    name: str = Field(..., description="Client name")
    email: str = Field(..., description="Client email")
    lawyer_id: str = Field(..., description="Assigned lawyer")
    company: Optional[str] = Field(None, description="Company name")
    industry: Optional[str] = Field(None, description="Industry")
    client_type: str = Field("individual", description="Type of client")

class ClientInteractionRequest(BaseModel):
    client_id: str = Field(..., description="Client identifier")
    interaction_type: str = Field(..., description="Type of interaction")
    description: str = Field(..., description="Interaction description")
    lawyer_id: str = Field(..., description="Lawyer identifier")
    outcome: str = Field("positive", description="Interaction outcome")
    duration: Optional[float] = Field(None, description="Duration in minutes")
    follow_up_required: bool = Field(False, description="Whether follow-up is needed")

class BusinessMetricsRequest(BaseModel):
    lawyer_id: str = Field(..., description="Lawyer identifier")
    total_revenue: float = Field(..., description="Total annual revenue")
    billable_hours: float = Field(..., description="Total billable hours")
    client_count: int = Field(..., description="Number of active clients")
    case_count: int = Field(..., description="Number of active cases")
    average_case_value: float = Field(..., description="Average case value")
    client_retention_rate: float = Field(..., description="Client retention rate (0-1)")
    efficiency_score: float = Field(..., description="Efficiency score (0-1)")


def create_app(platform=None) -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI-Powered Legal Practice Management Platform",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Dependency to get platform instance
    def get_platform():
        return platform
    
    # Dependency to verify authentication (simplified for demo)
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
        # In production, implement proper JWT token verification
        if not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return credentials.credentials
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION
        }
    
    # Time tracking endpoints
    @app.post("/api/time-tracking/track")
    async def track_activity(
        request: TimeEntryRequest,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Track lawyer activity automatically."""
        try:
            result = platform.auto_track_activity(
                lawyer_id=request.lawyer_id,
                activity_type=request.activity_type,
                duration=request.duration,
                description=request.description
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error tracking activity: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/time-tracking/billing-summary")
    async def generate_billing_summary(
        request: BillingSummaryRequest,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Generate professional billing summary."""
        try:
            result = platform.generate_billing_summary(
                lawyer_id=request.lawyer_id,
                client_id=request.client_id,
                date_range=request.date_range
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error generating billing summary: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/time-tracking/summary/{lawyer_id}")
    async def get_time_summary(
        lawyer_id: str,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Get time tracking summary for a lawyer."""
        try:
            result = platform.time_tracker.get_lawyer_time_summary(lawyer_id)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error getting time summary: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Calendar and deadline endpoints
    @app.post("/api/calendar/schedule-deadline")
    async def schedule_deadline(
        request: DeadlineRequest,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Schedule legal deadline with AI optimization."""
        try:
            result = platform.schedule_deadline(
                case_id=request.case_id,
                deadline_type=request.deadline_type,
                due_date=request.due_date,
                description=request.description,
                lawyer_id=request.lawyer_id,
                priority=request.priority
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error scheduling deadline: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/calendar/{lawyer_id}")
    async def get_lawyer_calendar(
        lawyer_id: str,
        date_range: str = "current_week",
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Get lawyer's calendar with AI insights."""
        try:
            result = platform.calendar_ai.get_lawyer_calendar(lawyer_id, date_range)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error getting calendar: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # CRM endpoints
    @app.post("/api/crm/add-client")
    async def add_client(
        request: ClientRequest,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Add new client to CRM."""
        try:
            result = platform.crm.add_client(
                name=request.name,
                email=request.email,
                lawyer_id=request.lawyer_id,
                company=request.company,
                industry=request.industry,
                client_type=request.client_type
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error adding client: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/crm/add-interaction")
    async def add_client_interaction(
        request: ClientInteractionRequest,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Add client interaction to CRM."""
        try:
            result = platform.crm.add_client_interaction(
                client_id=request.client_id,
                interaction_type=request.interaction_type,
                description=request.description,
                lawyer_id=request.lawyer_id,
                outcome=request.outcome,
                duration=request.duration,
                follow_up_required=request.follow_up_required
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error adding client interaction: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/crm/client/{client_id}")
    async def get_client_dashboard(
        client_id: str,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Get comprehensive client dashboard."""
        try:
            result = platform.get_client_dashboard(client_id)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error getting client dashboard: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/crm/lawyer/{lawyer_id}/insights")
    async def get_lawyer_client_insights(
        lawyer_id: str,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Get lawyer's client insights."""
        try:
            result = platform.crm.get_lawyer_client_insights(lawyer_id)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error getting lawyer client insights: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Document workflow endpoints
    @app.post("/api/documents/workflow")
    async def start_document_workflow(
        request: DocumentWorkflowRequest,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Start automated document workflow."""
        try:
            result = platform.auto_document_workflow(
                document_type=request.document_type,
                client_data=request.client_data
            )
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error starting document workflow: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Case management endpoints
    @app.get("/api/cases/{case_id}/intelligence")
    async def get_case_intelligence(
        case_id: str,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Get AI-powered case intelligence."""
        try:
            result = platform.get_case_intelligence(case_id)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error getting case intelligence: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/cases/lawyer/{lawyer_id}/overview")
    async def get_lawyer_case_overview(
        lawyer_id: str,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Get lawyer's case overview."""
        try:
            result = platform.case_management.get_lawyer_case_overview(lawyer_id)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error getting lawyer case overview: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # AI personality endpoints
    @app.get("/api/ai/personality/{lawyer_id}")
    async def get_personalized_recommendations(
        lawyer_id: str,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Get personalized AI recommendations."""
        try:
            result = platform.ai_personality.get_personalized_recommendations(lawyer_id)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/ai/personality/update-profile")
    async def update_ai_profile(
        lawyer_id: str,
        interaction_type: str,
        content: str,
        lawyer_response: str,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Update AI personality profile from interaction."""
        try:
            platform.ai_personality.update_profile_from_interaction(
                lawyer_id=lawyer_id,
                interaction_type=interaction_type,
                content=content,
                lawyer_response=lawyer_response
            )
            return {"success": True, "message": "Profile updated successfully"}
        except Exception as e:
            logger.error(f"Error updating AI profile: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Business intelligence endpoints
    @app.post("/api/business-intelligence/metrics")
    async def add_business_metrics(
        request: BusinessMetricsRequest,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Add business metrics for analysis."""
        try:
            platform.business_intelligence.add_business_metrics(
                lawyer_id=request.lawyer_id,
                total_revenue=request.total_revenue,
                billable_hours=request.billable_hours,
                client_count=request.client_count,
                case_count=request.case_count,
                average_case_value=request.average_case_value,
                client_retention_rate=request.client_retention_rate,
                efficiency_score=request.efficiency_score
            )
            return {"success": True, "message": "Business metrics added successfully"}
        except Exception as e:
            logger.error(f"Error adding business metrics: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/business-intelligence/{lawyer_id}/insights")
    async def get_business_insights(
        lawyer_id: str,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Get business intelligence insights."""
        try:
            result = platform.business_intelligence.get_lawyer_insights(lawyer_id)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error getting business insights: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/business-intelligence/practice-optimization")
    async def get_practice_optimization(
        practice_data: Dict[str, Any],
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Get practice optimization recommendations."""
        try:
            result = platform.business_intelligence.practice_optimization(practice_data)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error getting practice optimization: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Main dashboard endpoint
    @app.get("/api/dashboard/{lawyer_id}")
    async def get_lawyer_dashboard(
        lawyer_id: str,
        platform = Depends(get_platform),
        token: str = Depends(verify_token)
    ):
        """Get comprehensive lawyer dashboard."""
        try:
            result = platform.get_lawyer_dashboard(lawyer_id)
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"Error getting lawyer dashboard: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with platform information."""
        return {
            "message": "AI-Powered Legal Practice Management Platform",
            "version": settings.APP_VERSION,
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


def run_app(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI application."""
    uvicorn.run(
        "api.fastapi_app:create_app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_app() 