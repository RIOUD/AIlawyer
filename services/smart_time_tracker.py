#!/usr/bin/env python3
"""
Smart Time Tracking & Billing Automation

AI-powered time tracking that automatically captures billable work,
intelligently categorizes activities, and generates professional billing summaries.

Features:
- Automatic time capture for legal activities
- Intelligent categorization and billing rates
- Professional billing summary generation
- Revenue optimization through missed time detection
- Integration with calendar and case management
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class TimeEntry:
    """Data class for time tracking entries."""
    lawyer_id: str
    activity_type: str
    duration: float  # in hours
    description: str
    client_matter: Optional[str]
    billable: bool
    rate: float
    timestamp: datetime
    category: str
    session_id: Optional[str] = None


class SmartTimeTracker:
    """
    AI-powered time tracking system for legal professionals.
    
    Automatically captures, categorizes, and optimizes billable time
    to maximize revenue and efficiency.
    """
    
    def __init__(self):
        """Initialize the smart time tracker."""
        self.activity_categories = {
            "legal_research": {
                "billable": True,
                "default_rate": 250.0,
                "keywords": ["research", "analysis", "review", "investigation"]
            },
            "document_review": {
                "billable": True,
                "default_rate": 300.0,
                "keywords": ["review", "document", "contract", "agreement"]
            },
            "client_consultation": {
                "billable": True,
                "default_rate": 350.0,
                "keywords": ["consultation", "meeting", "advice", "counsel"]
            },
            "court_appearance": {
                "billable": True,
                "default_rate": 400.0,
                "keywords": ["court", "hearing", "trial", "appearance"]
            },
            "document_generation": {
                "billable": True,
                "default_rate": 275.0,
                "keywords": ["draft", "prepare", "generate", "create"]
            },
            "case_management": {
                "billable": True,
                "default_rate": 200.0,
                "keywords": ["case", "file", "organize", "coordinate"]
            },
            "administrative": {
                "billable": False,
                "default_rate": 0.0,
                "keywords": ["admin", "billing", "scheduling", "email"]
            }
        }
        
        # In-memory storage (replace with database in production)
        self.time_entries = []
        self.lawyer_profiles = {}
        
        logger.info("Smart Time Tracker initialized")
    
    def auto_track_activity(self, lawyer_id: str, activity_type: str, 
                          duration: float, description: str) -> Dict[str, Any]:
        """
        Automatically track lawyer activity with intelligent categorization.
        
        Args:
            lawyer_id: Lawyer identifier
            activity_type: Type of activity performed
            duration: Duration in hours
            description: Activity description
            
        Returns:
            Tracked activity with billing information
        """
        try:
            # Determine category and billing information
            category = self._categorize_activity(activity_type, description)
            client_matter = self._auto_detect_client_matter(description)
            rate = self._get_billing_rate(lawyer_id, category)
            
            # Create time entry
            time_entry = TimeEntry(
                lawyer_id=lawyer_id,
                activity_type=activity_type,
                duration=duration,
                description=description,
                client_matter=client_matter,
                billable=self.activity_categories[category]["billable"],
                rate=rate,
                timestamp=datetime.utcnow(),
                category=category,
                session_id=self._generate_session_id()
            )
            
            # Store entry
            self.time_entries.append(time_entry)
            
            # Calculate billing information
            billable_amount = time_entry.duration * time_entry.rate if time_entry.billable else 0
            
            result = {
                "entry_id": len(self.time_entries),
                "lawyer_id": lawyer_id,
                "activity_type": activity_type,
                "duration": duration,
                "description": description,
                "category": category,
                "client_matter": client_matter,
                "billable": time_entry.billable,
                "rate": rate,
                "billable_amount": billable_amount,
                "timestamp": time_entry.timestamp.isoformat(),
                "session_id": time_entry.session_id,
                "ai_insights": self._generate_activity_insights(time_entry)
            }
            
            logger.info(f"Activity tracked for lawyer {lawyer_id}: {activity_type} ({duration}h)")
            return result
            
        except Exception as e:
            logger.error(f"Error tracking activity: {e}")
            raise
    
    def _categorize_activity(self, activity_type: str, description: str) -> str:
        """Intelligently categorize activity based on type and description."""
        description_lower = description.lower()
        
        # Check each category for keyword matches
        for category, config in self.activity_categories.items():
            for keyword in config["keywords"]:
                if keyword in description_lower or keyword in activity_type.lower():
                    return category
        
        # Default to case management if no specific match
        return "case_management"
    
    def _auto_detect_client_matter(self, description: str) -> Optional[str]:
        """Automatically detect client matter from activity description."""
        # Simple pattern matching (enhance with NLP in production)
        import re
        
        # Look for common patterns
        patterns = [
            r"client[:\s]+([A-Za-z0-9\s]+)",
            r"matter[:\s]+([A-Za-z0-9\s]+)",
            r"case[:\s]+([A-Za-z0-9\s]+)",
            r"file[:\s]+([A-Za-z0-9\s]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _get_billing_rate(self, lawyer_id: str, category: str) -> float:
        """Get billing rate for lawyer and activity category."""
        # Check lawyer-specific rate first
        if lawyer_id in self.lawyer_profiles:
            lawyer_rate = self.lawyer_profiles[lawyer_id].get("hourly_rate")
            if lawyer_rate:
                return lawyer_rate
        
        # Use category default rate
        return self.activity_categories[category]["default_rate"]
    
    def _generate_session_id(self) -> str:
        """Generate unique session identifier."""
        import uuid
        return str(uuid.uuid4())
    
    def _generate_activity_insights(self, time_entry: TimeEntry) -> List[str]:
        """Generate AI insights for the tracked activity."""
        insights = []
        
        # Efficiency insights
        if time_entry.duration > 4:
            insights.append("Consider breaking long sessions into smaller chunks for better focus")
        
        if time_entry.billable and time_entry.rate < 200:
            insights.append("This activity may be underpriced - consider rate adjustment")
        
        # Productivity insights
        if time_entry.category == "administrative":
            insights.append("Consider delegating administrative tasks to support staff")
        
        if time_entry.category == "legal_research":
            insights.append("Research time is well-invested - consider creating reusable templates")
        
        return insights
    
    def generate_billing_summary(self, lawyer_id: str, client_id: str = None, 
                               date_range: str = "current_month") -> Dict[str, Any]:
        """
        Generate professional billing summary for client submission.
        
        Args:
            lawyer_id: Lawyer identifier
            client_id: Client identifier (optional)
            date_range: Time period for billing
            
        Returns:
            Professional billing summary ready for client
        """
        try:
            # Filter entries based on criteria
            filtered_entries = self._filter_entries(lawyer_id, client_id, date_range)
            
            # Calculate totals
            total_hours = sum(entry.duration for entry in filtered_entries)
            total_amount = sum(entry.duration * entry.rate for entry in filtered_entries if entry.billable)
            
            # Group by activity type
            activity_breakdown = {}
            for entry in filtered_entries:
                if entry.billable:
                    if entry.activity_type not in activity_breakdown:
                        activity_breakdown[entry.activity_type] = {
                            "hours": 0,
                            "amount": 0,
                            "rate": entry.rate
                        }
                    activity_breakdown[entry.activity_type]["hours"] += entry.duration
                    activity_breakdown[entry.activity_type]["amount"] += entry.duration * entry.rate
            
            # Generate professional summary
            summary = {
                "lawyer_id": lawyer_id,
                "client_id": client_id,
                "billing_period": self._get_billing_period(date_range),
                "total_hours": round(total_hours, 2),
                "billable_hours": round(sum(entry.duration for entry in filtered_entries if entry.billable), 2),
                "total_amount": round(total_amount, 2),
                "activity_breakdown": [
                    {
                        "activity": activity,
                        "hours": round(data["hours"], 2),
                        "rate": f"€{data['rate']}/h",
                        "amount": f"€{round(data['amount'], 2)}"
                    }
                    for activity, data in activity_breakdown.items()
                ],
                "detailed_entries": [
                    {
                        "date": entry.timestamp.strftime("%Y-%m-%d"),
                        "activity": entry.activity_type,
                        "description": entry.description,
                        "hours": round(entry.duration, 2),
                        "rate": f"€{entry.rate}/h",
                        "amount": f"€{round(entry.duration * entry.rate, 2)}" if entry.billable else "N/A"
                    }
                    for entry in filtered_entries if entry.billable
                ],
                "ai_recommendations": self._generate_billing_recommendations(filtered_entries),
                "ready_for_client": True,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Billing summary generated for lawyer {lawyer_id}: €{total_amount}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating billing summary: {e}")
            raise
    
    def _filter_entries(self, lawyer_id: str, client_id: str = None, 
                       date_range: str = "current_month") -> List[TimeEntry]:
        """Filter time entries based on criteria."""
        filtered = [entry for entry in self.time_entries if entry.lawyer_id == lawyer_id]
        
        # Filter by client if specified
        if client_id:
            filtered = [entry for entry in filtered if entry.client_matter == client_id]
        
        # Filter by date range
        start_date = self._get_start_date(date_range)
        filtered = [entry for entry in filtered if entry.timestamp >= start_date]
        
        return filtered
    
    def _get_billing_period(self, date_range: str) -> str:
        """Get human-readable billing period."""
        if date_range == "current_month":
            now = datetime.utcnow()
            return f"{now.strftime('%B %Y')}"
        elif date_range == "last_month":
            last_month = datetime.utcnow() - timedelta(days=30)
            return f"{last_month.strftime('%B %Y')}"
        else:
            return date_range
    
    def _get_start_date(self, date_range: str) -> datetime:
        """Get start date for filtering."""
        now = datetime.utcnow()
        
        if date_range == "current_month":
            return datetime(now.year, now.month, 1)
        elif date_range == "last_month":
            last_month = now - timedelta(days=30)
            return datetime(last_month.year, last_month.month, 1)
        elif date_range == "current_week":
            return now - timedelta(days=now.weekday())
        else:
            # Default to current month
            return datetime(now.year, now.month, 1)
    
    def _generate_billing_recommendations(self, entries: List[TimeEntry]) -> List[str]:
        """Generate AI recommendations for billing optimization."""
        recommendations = []
        
        total_hours = sum(entry.duration for entry in entries)
        billable_hours = sum(entry.duration for entry in entries if entry.billable)
        
        # Efficiency recommendations
        if billable_hours / total_hours < 0.8:
            recommendations.append("Consider reducing non-billable administrative time")
        
        # Rate optimization
        avg_rate = sum(entry.rate for entry in entries if entry.billable) / len([e for e in entries if e.billable]) if any(e.billable for e in entries) else 0
        if avg_rate < 250:
            recommendations.append("Your average billing rate may be below market - consider rate review")
        
        # Time tracking recommendations
        if total_hours > 40:
            recommendations.append("High workload detected - consider delegating tasks to maintain quality")
        
        return recommendations
    
    def get_lawyer_time_summary(self, lawyer_id: str) -> Dict[str, Any]:
        """
        Get comprehensive time summary for a lawyer.
        
        Args:
            lawyer_id: Lawyer identifier
            
        Returns:
            Time tracking summary with insights
        """
        try:
            lawyer_entries = [entry for entry in self.time_entries if entry.lawyer_id == lawyer_id]
            
            if not lawyer_entries:
                return {
                    "lawyer_id": lawyer_id,
                    "total_hours": 0,
                    "billable_hours": 0,
                    "billable_efficiency": 0,
                    "average_hourly_rate": 0,
                    "missed_billable_hours": 0,
                    "revenue_opportunities": []
                }
            
            total_hours = sum(entry.duration for entry in lawyer_entries)
            billable_hours = sum(entry.duration for entry in lawyer_entries if entry.billable)
            billable_efficiency = (billable_hours / total_hours * 100) if total_hours > 0 else 0
            
            billable_entries = [entry for entry in lawyer_entries if entry.billable]
            avg_rate = sum(entry.rate for entry in billable_entries) / len(billable_entries) if billable_entries else 0
            
            # Estimate missed billable time (conservative estimate)
            missed_hours = total_hours * 0.1  # Assume 10% of time could be better categorized
            
            summary = {
                "lawyer_id": lawyer_id,
                "total_hours": round(total_hours, 2),
                "billable_hours": round(billable_hours, 2),
                "billable_efficiency": round(billable_efficiency, 2),
                "average_hourly_rate": round(avg_rate, 2),
                "missed_billable_hours": round(missed_hours, 2),
                "potential_revenue": round(missed_hours * avg_rate, 2),
                "revenue_opportunities": self._identify_revenue_opportunities(lawyer_entries),
                "activity_distribution": self._get_activity_distribution(lawyer_entries),
                "recent_activities": [
                    {
                        "activity": entry.activity_type,
                        "duration": entry.duration,
                        "billable": entry.billable,
                        "timestamp": entry.timestamp.isoformat()
                    }
                    for entry in sorted(lawyer_entries, key=lambda x: x.timestamp, reverse=True)[:10]
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting time summary for lawyer {lawyer_id}: {e}")
            raise
    
    def _identify_revenue_opportunities(self, entries: List[TimeEntry]) -> List[Dict[str, Any]]:
        """Identify revenue optimization opportunities."""
        opportunities = []
        
        # Low-rate activities
        low_rate_entries = [e for e in entries if e.billable and e.rate < 200]
        if low_rate_entries:
            opportunities.append({
                "type": "rate_optimization",
                "description": f"{len(low_rate_entries)} activities with rates below €200/h",
                "potential_revenue": sum(e.duration * (250 - e.rate) for e in low_rate_entries)
            })
        
        # Non-billable activities that could be billable
        non_billable = [e for e in entries if not e.billable and e.category != "administrative"]
        if non_billable:
            opportunities.append({
                "type": "categorization_improvement",
                "description": f"{len(non_billable)} activities could be reclassified as billable",
                "potential_revenue": sum(e.duration * 200 for e in non_billable)
            })
        
        return opportunities
    
    def _get_activity_distribution(self, entries: List[TimeEntry]) -> Dict[str, float]:
        """Get distribution of activities by category."""
        total_hours = sum(entry.duration for entry in entries)
        if total_hours == 0:
            return {}
        
        distribution = {}
        for entry in entries:
            if entry.category not in distribution:
                distribution[entry.category] = 0
            distribution[entry.category] += entry.duration
        
        # Convert to percentages
        return {category: round((hours / total_hours) * 100, 2) 
                for category, hours in distribution.items()}
    
    def set_lawyer_profile(self, lawyer_id: str, hourly_rate: float, 
                          specialties: List[str] = None) -> Dict[str, Any]:
        """
        Set lawyer profile with billing rate and specialties.
        
        Args:
            lawyer_id: Lawyer identifier
            hourly_rate: Default hourly billing rate
            specialties: List of legal specialties
            
        Returns:
            Updated lawyer profile
        """
        try:
            self.lawyer_profiles[lawyer_id] = {
                "hourly_rate": hourly_rate,
                "specialties": specialties or [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Lawyer profile set for {lawyer_id}: €{hourly_rate}/h")
            return self.lawyer_profiles[lawyer_id]
            
        except Exception as e:
            logger.error(f"Error setting lawyer profile: {e}")
            raise 