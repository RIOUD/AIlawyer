#!/usr/bin/env python3
"""
Intelligent Calendar & Deadline Management

AI-powered calendar system that understands legal deadlines and workflows,
automatically schedules optimal time slots, and manages critical timelines.

Features:
- Automatic legal deadline calculation
- Intelligent scheduling optimization
- Deadline reminders and notifications
- Integration with case management
- Workload balancing and conflict resolution
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class LegalDeadline:
    """Data class for legal deadlines."""
    deadline_id: str
    case_id: str
    deadline_type: str
    due_date: datetime
    description: str
    priority: str  # high, medium, low
    reminder_days: List[int]  # Days before deadline to send reminders
    auto_generate_document: bool
    auto_prepare_materials: bool
    status: str  # pending, completed, overdue
    created_at: datetime
    lawyer_id: str


@dataclass
class CalendarEvent:
    """Data class for calendar events."""
    event_id: str
    lawyer_id: str
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    event_type: str  # meeting, deadline, court_appearance, etc.
    priority: str
    location: Optional[str]
    attendees: List[str]
    case_id: Optional[str]
    client_id: Optional[str]


class LegalCalendarAI:
    """
    AI-powered calendar system for legal professionals.
    
    Understands legal workflows, automatically calculates deadlines,
    and optimizes scheduling for maximum productivity.
    """
    
    def __init__(self):
        """Initialize the legal calendar AI system."""
        self.deadline_types = {
            "court_filing": {
                "default_reminder_days": [7, 3, 1],
                "auto_generate_document": True,
                "priority": "high",
                "estimated_duration": 2.0  # hours
            },
            "client_meeting": {
                "default_reminder_days": [1],
                "auto_generate_document": False,
                "auto_prepare_materials": True,
                "priority": "medium",
                "estimated_duration": 1.0
            },
            "discovery_deadline": {
                "default_reminder_days": [14, 7, 3, 1],
                "auto_generate_document": True,
                "priority": "high",
                "estimated_duration": 3.0
            },
            "settlement_conference": {
                "default_reminder_days": [3, 1],
                "auto_generate_document": True,
                "auto_prepare_materials": True,
                "priority": "high",
                "estimated_duration": 2.5
            },
            "trial_date": {
                "default_reminder_days": [30, 14, 7, 3, 1],
                "auto_generate_document": True,
                "auto_prepare_materials": True,
                "priority": "high",
                "estimated_duration": 8.0
            },
            "contract_review": {
                "default_reminder_days": [3, 1],
                "auto_generate_document": False,
                "priority": "medium",
                "estimated_duration": 1.5
            }
        }
        
        # In-memory storage (replace with database in production)
        self.deadlines = []
        self.events = []
        self.lawyer_schedules = {}
        
        logger.info("Legal Calendar AI initialized")
    
    def schedule_deadline(self, case_id: str, deadline_type: str, 
                         due_date: datetime, description: str,
                         lawyer_id: str, priority: str = None) -> Dict[str, Any]:
        """
        Schedule legal deadline with AI-powered optimization.
        
        Args:
            case_id: Case identifier
            deadline_type: Type of deadline
            due_date: Due date and time
            description: Deadline description
            lawyer_id: Lawyer identifier
            priority: Priority level (optional, auto-determined if not provided)
            
        Returns:
            Scheduled deadline with reminders and optimization
        """
        try:
            # Validate deadline type
            if deadline_type not in self.deadline_types:
                raise ValueError(f"Invalid deadline type: {deadline_type}")
            
            # Get deadline configuration
            config = self.deadline_types[deadline_type]
            
            # Auto-determine priority if not provided
            if not priority:
                priority = config["priority"]
            
            # Generate deadline ID
            deadline_id = self._generate_deadline_id()
            
            # Create deadline
            deadline = LegalDeadline(
                deadline_id=deadline_id,
                case_id=case_id,
                deadline_type=deadline_type,
                due_date=due_date,
                description=description,
                priority=priority,
                reminder_days=config["default_reminder_days"],
                auto_generate_document=config["auto_generate_document"],
                auto_prepare_materials=config.get("auto_prepare_materials", False),
                status="pending",
                created_at=datetime.utcnow(),
                lawyer_id=lawyer_id
            )
            
            # Store deadline
            self.deadlines.append(deadline)
            
            # Schedule preparation time if needed
            if config.get("auto_prepare_materials", False):
                self._schedule_preparation_time(deadline, config["estimated_duration"])
            
            # Generate calendar event
            event = self._create_calendar_event_from_deadline(deadline)
            self.events.append(event)
            
            result = {
                "deadline_id": deadline_id,
                "case_id": case_id,
                "deadline_type": deadline_type,
                "due_date": due_date.isoformat(),
                "description": description,
                "priority": priority,
                "reminder_days": config["default_reminder_days"],
                "auto_generate_document": config["auto_generate_document"],
                "auto_prepare_materials": config.get("auto_prepare_materials", False),
                "status": "pending",
                "estimated_duration": config["estimated_duration"],
                "ai_recommendations": self._generate_deadline_recommendations(deadline),
                "calendar_event_id": event.event_id
            }
            
            logger.info(f"Deadline scheduled: {deadline_type} for case {case_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error scheduling deadline: {e}")
            raise
    
    def _generate_deadline_id(self) -> str:
        """Generate unique deadline identifier."""
        import uuid
        return f"DEADLINE-{str(uuid.uuid4())[:8].upper()}"
    
    def _schedule_preparation_time(self, deadline: LegalDeadline, duration: float):
        """Schedule preparation time before deadline."""
        # Schedule preparation 1-2 days before deadline
        prep_date = deadline.due_date - timedelta(days=1)
        prep_start = prep_date.replace(hour=9, minute=0, second=0, microsecond=0)
        prep_end = prep_start + timedelta(hours=duration)
        
        prep_event = CalendarEvent(
            event_id=self._generate_event_id(),
            lawyer_id=deadline.lawyer_id,
            title=f"Prepare for {deadline.deadline_type}",
            description=f"Preparation for {deadline.description}",
            start_time=prep_start,
            end_time=prep_end,
            event_type="preparation",
            priority="medium",
            location=None,
            attendees=[deadline.lawyer_id],
            case_id=deadline.case_id,
            client_id=None
        )
        
        self.events.append(prep_event)
    
    def _create_calendar_event_from_deadline(self, deadline: LegalDeadline) -> CalendarEvent:
        """Create calendar event from deadline."""
        return CalendarEvent(
            event_id=self._generate_event_id(),
            lawyer_id=deadline.lawyer_id,
            title=f"{deadline.deadline_type.replace('_', ' ').title()}: {deadline.description}",
            description=deadline.description,
            start_time=deadline.due_date,
            end_time=deadline.due_date + timedelta(hours=1),  # Default 1-hour duration
            event_type=deadline.deadline_type,
            priority=deadline.priority,
            location=None,
            attendees=[deadline.lawyer_id],
            case_id=deadline.case_id,
            client_id=None
        )
    
    def _generate_event_id(self) -> str:
        """Generate unique event identifier."""
        import uuid
        return f"EVENT-{str(uuid.uuid4())[:8].upper()}"
    
    def _generate_deadline_recommendations(self, deadline: LegalDeadline) -> List[str]:
        """Generate AI recommendations for deadline management."""
        recommendations = []
        
        # Time management recommendations
        days_until_deadline = (deadline.due_date - datetime.utcnow()).days
        
        if days_until_deadline > 30:
            recommendations.append("Early deadline - consider starting preparation now")
        elif days_until_deadline < 7:
            recommendations.append("Urgent deadline - prioritize this task")
        
        # Preparation recommendations
        if deadline.auto_prepare_materials:
            recommendations.append("Materials will be auto-prepared 1 day before deadline")
        
        if deadline.auto_generate_document:
            recommendations.append("Required documents will be auto-generated")
        
        # Priority recommendations
        if deadline.priority == "high":
            recommendations.append("High priority - consider blocking calendar time")
        
        return recommendations
    
    def get_lawyer_calendar(self, lawyer_id: str, date_range: str = "current_week") -> Dict[str, Any]:
        """
        Get comprehensive calendar view for a lawyer.
        
        Args:
            lawyer_id: Lawyer identifier
            date_range: Time period to view
            
        Returns:
            Calendar data with deadlines, events, and AI insights
        """
        try:
            # Get date range
            start_date, end_date = self._get_date_range(date_range)
            
            # Filter events and deadlines
            lawyer_events = [
                event for event in self.events 
                if event.lawyer_id == lawyer_id and start_date <= event.start_time <= end_date
            ]
            
            lawyer_deadlines = [
                deadline for deadline in self.deadlines
                if deadline.lawyer_id == lawyer_id and start_date <= deadline.due_date <= end_date
            ]
            
            # Calculate schedule efficiency
            schedule_efficiency = self._calculate_schedule_efficiency(lawyer_events)
            
            # Get upcoming deadlines
            upcoming_deadlines = self._get_upcoming_deadlines(lawyer_id)
            
            # Get workload analysis
            workload_analysis = self._analyze_workload(lawyer_events, lawyer_deadlines)
            
            calendar_data = {
                "lawyer_id": lawyer_id,
                "date_range": date_range,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "events": [
                    {
                        "event_id": event.event_id,
                        "title": event.title,
                        "description": event.description,
                        "start_time": event.start_time.isoformat(),
                        "end_time": event.end_time.isoformat(),
                        "event_type": event.event_type,
                        "priority": event.priority,
                        "location": event.location,
                        "case_id": event.case_id,
                        "client_id": event.client_id
                    }
                    for event in sorted(lawyer_events, key=lambda x: x.start_time)
                ],
                "deadlines": [
                    {
                        "deadline_id": deadline.deadline_id,
                        "case_id": deadline.case_id,
                        "deadline_type": deadline.deadline_type,
                        "due_date": deadline.due_date.isoformat(),
                        "description": deadline.description,
                        "priority": deadline.priority,
                        "status": deadline.status,
                        "days_until_due": (deadline.due_date - datetime.utcnow()).days
                    }
                    for deadline in sorted(lawyer_deadlines, key=lambda x: x.due_date)
                ],
                "schedule_efficiency": schedule_efficiency,
                "upcoming_deadlines": upcoming_deadlines,
                "workload_analysis": workload_analysis,
                "ai_recommendations": self._generate_calendar_recommendations(
                    lawyer_events, lawyer_deadlines, workload_analysis
                )
            }
            
            return calendar_data
            
        except Exception as e:
            logger.error(f"Error getting calendar for lawyer {lawyer_id}: {e}")
            raise
    
    def _get_date_range(self, date_range: str) -> tuple[datetime, datetime]:
        """Get start and end dates for calendar view."""
        now = datetime.utcnow()
        
        if date_range == "current_week":
            start_date = now - timedelta(days=now.weekday())
            end_date = start_date + timedelta(days=6)
        elif date_range == "current_month":
            start_date = datetime(now.year, now.month, 1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        elif date_range == "next_week":
            start_date = now + timedelta(days=7-now.weekday())
            end_date = start_date + timedelta(days=6)
        else:
            # Default to current week
            start_date = now - timedelta(days=now.weekday())
            end_date = start_date + timedelta(days=6)
        
        return start_date, end_date
    
    def _calculate_schedule_efficiency(self, events: List[CalendarEvent]) -> float:
        """Calculate schedule efficiency score (0-100)."""
        if not events:
            return 100.0
        
        # Calculate metrics
        total_hours = sum((event.end_time - event.start_time).total_seconds() / 3600 for event in events)
        high_priority_hours = sum(
            (event.end_time - event.start_time).total_seconds() / 3600 
            for event in events if event.priority == "high"
        )
        
        # Efficiency factors
        priority_efficiency = (high_priority_hours / total_hours * 100) if total_hours > 0 else 0
        time_distribution = self._calculate_time_distribution_efficiency(events)
        
        # Weighted average
        efficiency = (priority_efficiency * 0.6) + (time_distribution * 0.4)
        
        return round(efficiency, 2)
    
    def _calculate_time_distribution_efficiency(self, events: List[CalendarEvent]) -> float:
        """Calculate efficiency based on time distribution."""
        if not events:
            return 100.0
        
        # Check for gaps and overlaps
        sorted_events = sorted(events, key=lambda x: x.start_time)
        gaps = 0
        overlaps = 0
        
        for i in range(len(sorted_events) - 1):
            current_end = sorted_events[i].end_time
            next_start = sorted_events[i + 1].start_time
            
            if next_start > current_end:
                gap_hours = (next_start - current_end).total_seconds() / 3600
                if gap_hours > 2:  # Gap longer than 2 hours
                    gaps += 1
            elif next_start < current_end:
                overlaps += 1
        
        # Calculate efficiency (fewer gaps and overlaps = higher efficiency)
        total_events = len(events)
        efficiency = 100 - ((gaps + overlaps) / total_events * 50)
        
        return max(0, efficiency)
    
    def _get_upcoming_deadlines(self, lawyer_id: str) -> List[Dict[str, Any]]:
        """Get upcoming deadlines for a lawyer."""
        now = datetime.utcnow()
        upcoming = []
        
        for deadline in self.deadlines:
            if deadline.lawyer_id == lawyer_id and deadline.status == "pending":
                days_until = (deadline.due_date - now).days
                if 0 <= days_until <= 30:  # Next 30 days
                    upcoming.append({
                        "deadline_id": deadline.deadline_id,
                        "case_id": deadline.case_id,
                        "deadline_type": deadline.deadline_type,
                        "due_date": deadline.due_date.isoformat(),
                        "description": deadline.description,
                        "priority": deadline.priority,
                        "days_until_due": days_until,
                        "urgency": "critical" if days_until <= 3 else "high" if days_until <= 7 else "medium"
                    })
        
        return sorted(upcoming, key=lambda x: x["days_until_due"])
    
    def _analyze_workload(self, events: List[CalendarEvent], 
                         deadlines: List[LegalDeadline]) -> Dict[str, Any]:
        """Analyze lawyer workload and provide insights."""
        total_hours = sum((event.end_time - event.start_time).total_seconds() / 3600 for event in events)
        
        # Categorize by priority
        high_priority_hours = sum(
            (event.end_time - event.start_time).total_seconds() / 3600 
            for event in events if event.priority == "high"
        )
        
        # Count deadlines by priority
        high_priority_deadlines = len([d for d in deadlines if d.priority == "high"])
        medium_priority_deadlines = len([d for d in deadlines if d.priority == "medium"])
        low_priority_deadlines = len([d for d in deadlines if d.priority == "low"])
        
        # Workload assessment
        if total_hours > 40:
            workload_level = "overloaded"
        elif total_hours > 30:
            workload_level = "busy"
        elif total_hours > 20:
            workload_level = "moderate"
        else:
            workload_level = "light"
        
        return {
            "total_hours": round(total_hours, 2),
            "high_priority_hours": round(high_priority_hours, 2),
            "workload_level": workload_level,
            "deadlines": {
                "high_priority": high_priority_deadlines,
                "medium_priority": medium_priority_deadlines,
                "low_priority": low_priority_deadlines,
                "total": len(deadlines)
            },
            "recommendations": self._generate_workload_recommendations(
                total_hours, high_priority_hours, len(deadlines)
            )
        }
    
    def _generate_workload_recommendations(self, total_hours: float, 
                                         high_priority_hours: float, 
                                         deadline_count: int) -> List[str]:
        """Generate workload optimization recommendations."""
        recommendations = []
        
        if total_hours > 40:
            recommendations.append("High workload detected - consider delegating tasks")
        
        if high_priority_hours / total_hours < 0.6:
            recommendations.append("Low priority work ratio - focus on high-value activities")
        
        if deadline_count > 10:
            recommendations.append("Many pending deadlines - consider deadline prioritization")
        
        if total_hours < 20:
            recommendations.append("Light workload - consider taking on additional cases")
        
        return recommendations
    
    def _generate_calendar_recommendations(self, events: List[CalendarEvent], 
                                         deadlines: List[LegalDeadline],
                                         workload_analysis: Dict[str, Any]) -> List[str]:
        """Generate AI recommendations for calendar optimization."""
        recommendations = []
        
        # Schedule optimization
        if workload_analysis["workload_level"] == "overloaded":
            recommendations.append("Schedule is overloaded - consider rescheduling non-urgent tasks")
        
        # Deadline management
        critical_deadlines = [d for d in deadlines if d.priority == "high" and 
                            (d.due_date - datetime.utcnow()).days <= 3]
        if critical_deadlines:
            recommendations.append(f"{len(critical_deadlines)} critical deadlines approaching - prioritize accordingly")
        
        # Time blocking recommendations
        if len(events) > 10:
            recommendations.append("Many events scheduled - consider time blocking for focused work")
        
        return recommendations
    
    def intelligent_scheduling(self, task: str, duration: float, 
                             lawyer_id: str, priority: str = "medium",
                             preferred_days: List[str] = None) -> datetime:
        """
        Find optimal time slots based on workload and priorities.
        
        Args:
            task: Task description
            duration: Duration in hours
            lawyer_id: Lawyer identifier
            priority: Task priority
            preferred_days: Preferred days of week
            
        Returns:
            Optimal start time for the task
        """
        try:
            # Get current schedule
            start_date, end_date = self._get_date_range("current_week")
            current_events = [
                event for event in self.events 
                if event.lawyer_id == lawyer_id and start_date <= event.start_time <= end_date
            ]
            
            # Find available time slots
            available_slots = self._find_available_slots(current_events, duration, preferred_days)
            
            if not available_slots:
                # Look into next week
                start_date, end_date = self._get_date_range("next_week")
                current_events = [
                    event for event in self.events 
                    if event.lawyer_id == lawyer_id and start_date <= event.start_time <= end_date
                ]
                available_slots = self._find_available_slots(current_events, duration, preferred_days)
            
            if available_slots:
                # Choose optimal slot based on priority and workload
                optimal_slot = self._select_optimal_slot(available_slots, priority)
                return optimal_slot
            else:
                raise ValueError("No available time slots found for the specified duration")
                
        except Exception as e:
            logger.error(f"Error in intelligent scheduling: {e}")
            raise
    
    def _find_available_slots(self, events: List[CalendarEvent], duration: float,
                             preferred_days: List[str] = None) -> List[datetime]:
        """Find available time slots for scheduling."""
        # Business hours: 9 AM to 6 PM
        business_start = 9
        business_end = 18
        
        available_slots = []
        now = datetime.utcnow()
        
        # Check next 7 days
        for day_offset in range(7):
            check_date = now + timedelta(days=day_offset)
            
            # Skip weekends if not preferred
            if preferred_days and check_date.strftime("%A").lower() not in preferred_days:
                continue
            
            # Check each hour during business hours
            for hour in range(business_start, business_end - int(duration)):
                slot_start = check_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                slot_end = slot_start + timedelta(hours=duration)
                
                # Check if slot conflicts with existing events
                conflict = False
                for event in events:
                    if (slot_start < event.end_time and slot_end > event.start_time):
                        conflict = True
                        break
                
                if not conflict and slot_start > now:
                    available_slots.append(slot_start)
        
        return available_slots
    
    def _select_optimal_slot(self, available_slots: List[datetime], priority: str) -> datetime:
        """Select optimal time slot based on priority and preferences."""
        if not available_slots:
            return None
        
        # For high priority tasks, prefer earlier slots
        if priority == "high":
            return min(available_slots)
        
        # For medium priority, prefer mid-morning slots
        elif priority == "medium":
            mid_morning_slots = [slot for slot in available_slots if 10 <= slot.hour <= 12]
            if mid_morning_slots:
                return min(mid_morning_slots)
        
        # Default to earliest available slot
        return min(available_slots) 