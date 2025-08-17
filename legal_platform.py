#!/usr/bin/env python3
"""
AI-Powered Legal Practice Management Platform

A comprehensive, enterprise-grade platform designed to maximize lawyer productivity
through intelligent automation, smart time tracking, and AI-powered insights.

Core Features:
- Smart Time Tracking & Billing Automation
- Intelligent Calendar & Deadline Management  
- Client Relationship Management (CRM)
- Document Workflow Automation
- Case Management with Predictive Analytics
- AI Legal Assistant Personality
- Business Intelligence & Revenue Optimization

Security Features:
- End-to-end encryption for all sensitive data
- Role-based access control
- Audit logging for compliance
- Secure API authentication
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('legal_platform.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import core modules
from services.smart_time_tracker import SmartTimeTracker
from services.legal_calendar_ai import LegalCalendarAI
from services.legal_crm import LegalCRM
from services.document_workflow_ai import DocumentWorkflowAI
from services.case_management_ai import CaseManagementAI
from services.legal_ai_personality import LegalAIPersonality
from services.business_intelligence_ai import BusinessIntelligenceAI
from models.database import DatabaseManager
from api.fastapi_app import create_app
from config.settings import Settings


class LegalPracticePlatform:
    """
    Main platform class that orchestrates all AI-powered legal practice features.
    
    This is the central hub that coordinates all productivity tools and provides
    a unified interface for lawyers to maximize their efficiency and revenue.
    """
    
    def __init__(self):
        """Initialize the legal practice platform with all core services."""
        self.settings = Settings()
        self.db_manager = DatabaseManager()
        
        # Initialize core services
        self.time_tracker = SmartTimeTracker()
        self.calendar_ai = LegalCalendarAI()
        self.crm = LegalCRM()
        self.document_workflow = DocumentWorkflowAI()
        self.case_management = CaseManagementAI()
        self.ai_personality = LegalAIPersonality()
        self.business_intelligence = BusinessIntelligenceAI()
        
        # FastAPI application
        self.app = create_app(self)
        
        logger.info("🚀 Legal Practice Platform initialized successfully")
    
    def start_platform(self):
        """Start the legal practice platform."""
        try:
            # Initialize database
            self.db_manager.initialize_database()
            
            # Start FastAPI server
            import uvicorn
            uvicorn.run(
                self.app,
                host=self.settings.HOST,
                port=self.settings.PORT,
                log_level="info"
            )
            
        except Exception as e:
            logger.error(f"Failed to start platform: {e}")
            raise
    
    def get_lawyer_dashboard(self, lawyer_id: str) -> Dict[str, Any]:
        """
        Get comprehensive dashboard for a lawyer with all key metrics and insights.
        
        Args:
            lawyer_id: Unique identifier for the lawyer
            
        Returns:
            Complete dashboard data with productivity metrics and AI insights
        """
        try:
            # Get time tracking data
            time_data = self.time_tracker.get_lawyer_time_summary(lawyer_id)
            
            # Get calendar and deadlines
            calendar_data = self.calendar_ai.get_lawyer_calendar(lawyer_id)
            
            # Get client insights
            client_insights = self.crm.get_lawyer_client_insights(lawyer_id)
            
            # Get case intelligence
            case_intelligence = self.case_management.get_lawyer_case_overview(lawyer_id)
            
            # Get business intelligence
            business_insights = self.business_intelligence.get_lawyer_insights(lawyer_id)
            
            # Get AI personality recommendations
            ai_recommendations = self.ai_personality.get_personalized_recommendations(lawyer_id)
            
            dashboard = {
                "lawyer_id": lawyer_id,
                "timestamp": datetime.utcnow().isoformat(),
                "time_tracking": time_data,
                "calendar": calendar_data,
                "clients": client_insights,
                "cases": case_intelligence,
                "business_intelligence": business_insights,
                "ai_recommendations": ai_recommendations,
                "productivity_score": self._calculate_productivity_score(
                    time_data, calendar_data, client_insights, case_intelligence
                ),
                "revenue_optimization": self._calculate_revenue_opportunities(
                    time_data, client_insights, business_insights
                )
            }
            
            logger.info(f"Dashboard generated for lawyer {lawyer_id}")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating dashboard for lawyer {lawyer_id}: {e}")
            raise
    
    def _calculate_productivity_score(self, time_data: Dict, calendar_data: Dict, 
                                    client_insights: Dict, case_intelligence: Dict) -> float:
        """Calculate overall productivity score based on various metrics."""
        try:
            # Time tracking efficiency (0-100)
            time_efficiency = time_data.get("billable_efficiency", 0)
            
            # Calendar optimization (0-100)
            calendar_efficiency = calendar_data.get("schedule_efficiency", 0)
            
            # Client satisfaction (0-100)
            client_satisfaction = client_insights.get("average_satisfaction", 0)
            
            # Case progress (0-100)
            case_progress = case_intelligence.get("average_progress", 0)
            
            # Weighted average
            productivity_score = (
                time_efficiency * 0.3 +
                calendar_efficiency * 0.25 +
                client_satisfaction * 0.25 +
                case_progress * 0.2
            )
            
            return round(productivity_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating productivity score: {e}")
            return 0.0
    
    def _calculate_revenue_opportunities(self, time_data: Dict, client_insights: Dict, 
                                       business_insights: Dict) -> Dict[str, Any]:
        """Calculate revenue optimization opportunities."""
        try:
            opportunities = {
                "missed_billable_time": time_data.get("missed_billable_hours", 0) * 
                                      time_data.get("average_hourly_rate", 0),
                "upselling_opportunities": business_insights.get("upselling_potential", 0),
                "client_retention_risk": business_insights.get("retention_risk_revenue", 0),
                "efficiency_gains": business_insights.get("efficiency_savings", 0),
                "total_opportunity": 0
            }
            
            opportunities["total_opportunity"] = sum([
                opportunities["missed_billable_time"],
                opportunities["upselling_opportunities"],
                opportunities["efficiency_gains"]
            ]) - opportunities["client_retention_risk"]
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error calculating revenue opportunities: {e}")
            return {"total_opportunity": 0}
    
    def auto_track_activity(self, lawyer_id: str, activity_type: str, 
                          duration: float, description: str) -> Dict[str, Any]:
        """
        Automatically track lawyer activity and categorize for billing.
        
        Args:
            lawyer_id: Lawyer identifier
            activity_type: Type of activity (research, document_review, etc.)
            duration: Duration in hours
            description: Activity description
            
        Returns:
            Tracked activity with billing information
        """
        try:
            return self.time_tracker.auto_track_activity(
                lawyer_id, activity_type, duration, description
            )
        except Exception as e:
            logger.error(f"Error auto-tracking activity: {e}")
            raise
    
    def generate_billing_summary(self, lawyer_id: str, client_id: str = None, 
                               date_range: str = "current_month") -> Dict[str, Any]:
        """
        Generate professional billing summary for client submission.
        
        Args:
            lawyer_id: Lawyer identifier
            client_id: Client identifier (optional, for specific client)
            date_range: Time period for billing
            
        Returns:
            Professional billing summary ready for client
        """
        try:
            return self.time_tracker.generate_billing_summary(
                lawyer_id, client_id, date_range
            )
        except Exception as e:
            logger.error(f"Error generating billing summary: {e}")
            raise
    
    def schedule_deadline(self, case_id: str, deadline_type: str, 
                         due_date: datetime, description: str) -> Dict[str, Any]:
        """
        Schedule legal deadline with AI-powered optimization.
        
        Args:
            case_id: Case identifier
            deadline_type: Type of deadline (court_filing, client_meeting, etc.)
            due_date: Due date and time
            description: Deadline description
            
        Returns:
            Scheduled deadline with reminders and optimization
        """
        try:
            return self.calendar_ai.schedule_deadline(
                case_id, deadline_type, due_date, description
            )
        except Exception as e:
            logger.error(f"Error scheduling deadline: {e}")
            raise
    
    def get_client_dashboard(self, client_id: str) -> Dict[str, Any]:
        """
        Get comprehensive client dashboard with AI insights.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Complete client overview with AI-powered insights
        """
        try:
            return self.crm.get_client_dashboard(client_id)
        except Exception as e:
            logger.error(f"Error getting client dashboard: {e}")
            raise
    
    def auto_document_workflow(self, document_type: str, client_data: Dict) -> Dict[str, Any]:
        """
        Automatically handle complete document workflow.
        
        Args:
            document_type: Type of document to create
            client_data: Client information for document generation
            
        Returns:
            Complete document workflow status
        """
        try:
            return self.document_workflow.auto_document_pipeline(document_type, client_data)
        except Exception as e:
            logger.error(f"Error in document workflow: {e}")
            raise
    
    def get_case_intelligence(self, case_id: str) -> Dict[str, Any]:
        """
        Get AI-powered case analysis with predictions and recommendations.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Case intelligence with predictions and automated tasks
        """
        try:
            return self.case_management.get_case_intelligence(case_id)
        except Exception as e:
            logger.error(f"Error getting case intelligence: {e}")
            raise


def main():
    """Main entry point for the legal practice platform."""
    try:
        # Initialize platform
        platform = LegalPracticePlatform()
        
        # Start the platform
        platform.start_platform()
        
    except KeyboardInterrupt:
        logger.info("Platform shutdown requested by user")
    except Exception as e:
        logger.error(f"Platform startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 