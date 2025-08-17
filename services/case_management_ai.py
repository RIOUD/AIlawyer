#!/usr/bin/env python3
"""
AI-Powered Case Management

Intelligent case management system with predictive analytics,
automated task management, and resource optimization.

Features:
- Predictive case outcome analysis
- Automated task generation and scheduling
- Resource allocation optimization
- Risk assessment and mitigation
- Case progress tracking and analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class Case:
    """Data class for case information."""
    case_id: str
    client_id: str
    case_type: str
    title: str
    description: str
    status: str  # active, closed, pending, settled
    priority: str  # high, medium, low
    start_date: datetime
    estimated_end_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    estimated_value: float
    actual_value: Optional[float]
    lawyer_id: str
    assigned_team: List[str]
    jurisdiction: Optional[str]
    court: Optional[str]


@dataclass
class CaseTask:
    """Data class for case tasks."""
    task_id: str
    case_id: str
    task_type: str
    title: str
    description: str
    status: str  # pending, in_progress, completed, overdue
    priority: str  # high, medium, low
    assigned_to: str
    due_date: datetime
    estimated_hours: float
    actual_hours: Optional[float]
    dependencies: List[str]
    created_at: datetime
    completed_at: Optional[datetime]


@dataclass
class CaseMilestone:
    """Data class for case milestones."""
    milestone_id: str
    case_id: str
    milestone_type: str
    title: str
    description: str
    target_date: datetime
    actual_date: Optional[datetime]
    status: str  # pending, completed, overdue
    importance: str  # critical, important, standard


class CaseManagementAI:
    """
    AI-powered case management system.
    
    Provides predictive analytics, automated task management,
    and resource optimization for legal cases.
    """
    
    def __init__(self):
        """Initialize the case management AI system."""
        self.case_types = {
            "employment_litigation": {
                "estimated_duration": "6-12 months",
                "success_rate": 0.65,
                "average_value": 50000,
                "key_milestones": ["filing", "discovery", "mediation", "trial"],
                "required_tasks": ["client_interview", "document_review", "motion_filing", "discovery_requests"]
            },
            "contract_dispute": {
                "estimated_duration": "3-8 months",
                "success_rate": 0.75,
                "average_value": 75000,
                "key_milestones": ["demand_letter", "negotiation", "mediation", "arbitration"],
                "required_tasks": ["contract_analysis", "damages_calculation", "settlement_negotiation"]
            },
            "intellectual_property": {
                "estimated_duration": "12-24 months",
                "success_rate": 0.55,
                "average_value": 150000,
                "key_milestones": ["filing", "discovery", "expert_reports", "trial"],
                "required_tasks": ["ip_analysis", "expert_retention", "technical_review"]
            },
            "personal_injury": {
                "estimated_duration": "8-18 months",
                "success_rate": 0.70,
                "average_value": 100000,
                "key_milestones": ["investigation", "demand", "negotiation", "settlement"],
                "required_tasks": ["medical_review", "liability_analysis", "damages_assessment"]
            }
        }
        
        # In-memory storage (replace with database in production)
        self.cases = []
        self.tasks = []
        self.milestones = []
        
        logger.info("Case Management AI initialized")
    
    def get_case_intelligence(self, case_id: str) -> Dict[str, Any]:
        """
        Get AI-powered case analysis with predictions and recommendations.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Case intelligence with predictions and automated tasks
        """
        try:
            # Get case information
            case = self._get_case(case_id)
            if not case:
                raise ValueError(f"Case {case_id} not found")
            
            # Get case tasks
            case_tasks = [task for task in self.tasks if task.case_id == case_id]
            
            # Get case milestones
            case_milestones = [milestone for milestone in self.milestones if milestone.case_id == case_id]
            
            # Generate AI predictions
            ai_predictions = self._generate_case_predictions(case, case_tasks, case_milestones)
            
            # Generate automated tasks
            automated_tasks = self._generate_automated_tasks(case, case_tasks)
            
            # Calculate resource allocation
            resource_allocation = self._calculate_resource_allocation(case, case_tasks)
            
            # Assess risks
            risk_assessment = self._assess_case_risks(case, case_tasks, case_milestones)
            
            # Calculate progress
            progress_metrics = self._calculate_case_progress(case, case_tasks, case_milestones)
            
            intelligence = {
                "case_overview": {
                    "case_id": case.case_id,
                    "title": case.title,
                    "case_type": case.case_type,
                    "status": case.status,
                    "priority": case.priority,
                    "start_date": case.start_date.isoformat(),
                    "estimated_end_date": case.estimated_end_date.isoformat() if case.estimated_end_date else None,
                    "estimated_value": case.estimated_value,
                    "actual_value": case.actual_value,
                    "lawyer_id": case.lawyer_id,
                    "assigned_team": case.assigned_team
                },
                "ai_predictions": ai_predictions,
                "automated_tasks": automated_tasks,
                "resource_allocation": resource_allocation,
                "risk_assessment": risk_assessment,
                "progress_metrics": progress_metrics,
                "key_milestones": [
                    {
                        "milestone_id": milestone.milestone_id,
                        "type": milestone.milestone_type,
                        "title": milestone.title,
                        "target_date": milestone.target_date.isoformat(),
                        "actual_date": milestone.actual_date.isoformat() if milestone.actual_date else None,
                        "status": milestone.status,
                        "importance": milestone.importance
                    }
                    for milestone in sorted(case_milestones, key=lambda x: x.target_date)
                ],
                "recent_tasks": [
                    {
                        "task_id": task.task_id,
                        "title": task.title,
                        "status": task.status,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat(),
                        "assigned_to": task.assigned_to
                    }
                    for task in sorted(case_tasks, key=lambda x: x.due_date, reverse=True)[:10]
                ],
                "ai_recommendations": self._generate_case_recommendations(
                    case, ai_predictions, risk_assessment, progress_metrics
                )
            }
            
            logger.info(f"Case intelligence generated for {case.title}")
            return intelligence
            
        except Exception as e:
            logger.error(f"Error getting case intelligence: {e}")
            raise
    
    def _get_case(self, case_id: str) -> Optional[Case]:
        """Get case by ID."""
        for case in self.cases:
            if case.case_id == case_id:
                return case
        return None
    
    def _generate_case_predictions(self, case: Case, tasks: List[CaseTask], 
                                 milestones: List[CaseMilestone]) -> Dict[str, Any]:
        """Generate AI predictions for case outcomes."""
        case_config = self.case_types.get(case.case_type, {})
        
        # Base success probability from case type
        base_success_rate = case_config.get("success_rate", 0.5)
        
        # Adjust based on case factors
        success_probability = base_success_rate
        
        # Task completion rate adjustment
        completed_tasks = len([t for t in tasks if t.status == "completed"])
        total_tasks = len(tasks)
        if total_tasks > 0:
            task_completion_rate = completed_tasks / total_tasks
            success_probability += (task_completion_rate - 0.5) * 0.2
        
        # Milestone progress adjustment
        completed_milestones = len([m for m in milestones if m.status == "completed"])
        total_milestones = len(milestones)
        if total_milestones > 0:
            milestone_progress = completed_milestones / total_milestones
            success_probability += (milestone_progress - 0.5) * 0.15
        
        # Priority adjustment
        if case.priority == "high":
            success_probability += 0.1
        elif case.priority == "low":
            success_probability -= 0.05
        
        # Calculate estimated duration
        estimated_duration = self._calculate_estimated_duration(case, tasks, milestones)
        
        # Calculate cost estimate
        cost_estimate = self._calculate_cost_estimate(case, tasks)
        
        # Determine recommended strategy
        recommended_strategy = self._determine_recommended_strategy(case, success_probability)
        
        # Identify key risks
        key_risks = self._identify_key_risks(case, tasks, milestones)
        
        return {
            "success_probability": round(success_probability, 3),
            "estimated_duration": estimated_duration,
            "recommended_strategy": recommended_strategy,
            "key_risks": key_risks,
            "cost_estimate": cost_estimate,
            "confidence_level": "high" if success_probability > 0.7 else "medium" if success_probability > 0.5 else "low"
        }
    
    def _calculate_estimated_duration(self, case: Case, tasks: List[CaseTask], 
                                    milestones: List[CaseMilestone]) -> str:
        """Calculate estimated case duration."""
        case_config = self.case_types.get(case.case_type, {})
        base_duration = case_config.get("estimated_duration", "6-12 months")
        
        # Adjust based on progress
        days_elapsed = (datetime.utcnow() - case.start_date).days
        completed_milestones = len([m for m in milestones if m.status == "completed"])
        total_milestones = len(milestones)
        
        if total_milestones > 0:
            progress_ratio = completed_milestones / total_milestones
            if progress_ratio > 0.7:
                return "1-2 months"
            elif progress_ratio > 0.5:
                return "2-4 months"
        
        return base_duration
    
    def _calculate_cost_estimate(self, case: Case, tasks: List[CaseTask]) -> str:
        """Calculate estimated case cost."""
        # Base cost from case type
        case_config = self.case_types.get(case.case_type, {})
        base_cost = case_config.get("average_value", 50000)
        
        # Adjust based on complexity (number of tasks)
        complexity_multiplier = 1 + (len(tasks) / 20)  # More tasks = more complex
        
        # Adjust based on priority
        if case.priority == "high":
            complexity_multiplier *= 1.2
        elif case.priority == "low":
            complexity_multiplier *= 0.8
        
        estimated_cost = base_cost * complexity_multiplier
        
        return f"€{int(estimated_cost):,}-€{int(estimated_cost * 1.5):,}"
    
    def _determine_recommended_strategy(self, case: Case, success_probability: float) -> str:
        """Determine recommended case strategy."""
        if success_probability > 0.8:
            return "aggressive_litigation"
        elif success_probability > 0.6:
            return "balanced_approach"
        elif success_probability > 0.4:
            return "settlement_focused"
        else:
            return "defensive_strategy"
    
    def _identify_key_risks(self, case: Case, tasks: List[CaseTask], 
                           milestones: List[CaseMilestone]) -> List[str]:
        """Identify key risks for the case."""
        risks = []
        
        # Overdue tasks
        overdue_tasks = [t for t in tasks if t.status == "overdue"]
        if overdue_tasks:
            risks.append(f"{len(overdue_tasks)} overdue tasks may impact case timeline")
        
        # Overdue milestones
        overdue_milestones = [m for m in milestones if m.status == "overdue"]
        if overdue_milestones:
            risks.append(f"{len(overdue_milestones)} critical milestones are overdue")
        
        # Resource constraints
        high_priority_tasks = [t for t in tasks if t.priority == "high" and t.status != "completed"]
        if len(high_priority_tasks) > 5:
            risks.append("High workload may impact case quality")
        
        # Timeline risks
        if case.estimated_end_date:
            days_until_deadline = (case.estimated_end_date - datetime.utcnow()).days
            if days_until_deadline < 30:
                risks.append("Case deadline approaching - requires immediate attention")
        
        return risks
    
    def _generate_automated_tasks(self, case: Case, existing_tasks: List[CaseTask]) -> List[Dict[str, Any]]:
        """Generate automated tasks for the case."""
        case_config = self.case_types.get(case.case_type, {})
        required_tasks = case_config.get("required_tasks", [])
        
        automated_tasks = []
        
        # Check for missing required tasks
        existing_task_types = [task.task_type for task in existing_tasks]
        for required_task in required_tasks:
            if required_task not in existing_task_types:
                automated_tasks.append({
                    "task": f"Complete {required_task.replace('_', ' ')}",
                    "due": self._calculate_task_due_date(case, required_task),
                    "priority": "high" if "filing" in required_task else "medium",
                    "estimated_hours": self._estimate_task_hours(required_task),
                    "reason": f"Required task for {case.case_type} cases"
                })
        
        # Generate timeline-based tasks
        if case.estimated_end_date:
            days_until_deadline = (case.estimated_end_date - datetime.utcnow()).days
            if days_until_deadline < 60:
                automated_tasks.append({
                    "task": "Prepare case summary for settlement discussions",
                    "due": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                    "priority": "high",
                    "estimated_hours": 4.0,
                    "reason": "Case approaching deadline - prepare for settlement"
                })
        
        return automated_tasks
    
    def _calculate_task_due_date(self, case: Case, task_type: str) -> str:
        """Calculate due date for automated task."""
        # Base due date on case timeline
        if case.estimated_end_date:
            days_until_deadline = (case.estimated_end_date - datetime.utcnow()).days
            
            if "filing" in task_type:
                # Filing tasks should be done early
                due_days = min(days_until_deadline - 30, 14)
            elif "discovery" in task_type:
                # Discovery tasks in middle
                due_days = min(days_until_deadline - 15, 30)
            else:
                # Other tasks near end
                due_days = min(days_until_deadline - 7, 7)
            
            return (datetime.utcnow() + timedelta(days=max(due_days, 1))).isoformat()
        
        # Default to 2 weeks from now
        return (datetime.utcnow() + timedelta(days=14)).isoformat()
    
    def _estimate_task_hours(self, task_type: str) -> float:
        """Estimate hours required for task type."""
        task_estimates = {
            "client_interview": 2.0,
            "document_review": 4.0,
            "motion_filing": 3.0,
            "discovery_requests": 2.0,
            "contract_analysis": 6.0,
            "damages_calculation": 4.0,
            "settlement_negotiation": 3.0,
            "ip_analysis": 8.0,
            "expert_retention": 2.0,
            "technical_review": 6.0,
            "medical_review": 4.0,
            "liability_analysis": 5.0,
            "damages_assessment": 4.0
        }
        
        return task_estimates.get(task_type, 3.0)
    
    def _calculate_resource_allocation(self, case: Case, tasks: List[CaseTask]) -> Dict[str, Any]:
        """Calculate optimal resource allocation for the case."""
        # Calculate total estimated hours
        total_estimated_hours = sum(task.estimated_hours for task in tasks)
        total_actual_hours = sum(task.actual_hours for task in tasks if task.actual_hours)
        
        # Calculate remaining hours
        remaining_hours = total_estimated_hours - total_actual_hours
        
        # Determine team size based on case complexity
        if total_estimated_hours > 100:
            recommended_team_size = 3
        elif total_estimated_hours > 50:
            recommended_team_size = 2
        else:
            recommended_team_size = 1
        
        # Identify required roles
        required_roles = ["senior_associate"]
        if total_estimated_hours > 80:
            required_roles.append("paralegal")
        if "expert" in str(tasks).lower():
            required_roles.append("expert_witness")
        if "court" in str(tasks).lower():
            required_roles.append("court_reporter")
        
        return {
            "recommended_hours": round(remaining_hours, 1),
            "team_members": required_roles,
            "external_resources": [role for role in required_roles if role not in ["senior_associate", "paralegal"]],
            "estimated_completion_weeks": round(remaining_hours / 40, 1),  # Assuming 40-hour work week
            "resource_efficiency": round((total_actual_hours / total_estimated_hours * 100) if total_estimated_hours > 0 else 0, 1)
        }
    
    def _assess_case_risks(self, case: Case, tasks: List[CaseTask], 
                          milestones: List[CaseMilestone]) -> Dict[str, Any]:
        """Assess risks associated with the case."""
        risk_factors = []
        risk_score = 0
        
        # Timeline risks
        if case.estimated_end_date:
            days_until_deadline = (case.estimated_end_date - datetime.utcnow()).days
            if days_until_deadline < 30:
                risk_factors.append("Critical timeline pressure")
                risk_score += 30
            elif days_until_deadline < 60:
                risk_factors.append("Approaching deadline")
                risk_score += 15
        
        # Task completion risks
        overdue_tasks = len([t for t in tasks if t.status == "overdue"])
        if overdue_tasks > 3:
            risk_factors.append(f"{overdue_tasks} overdue tasks")
            risk_score += 25
        
        # Milestone risks
        overdue_milestones = len([m for m in milestones if m.status == "overdue" and m.importance == "critical"])
        if overdue_milestones > 0:
            risk_factors.append(f"{overdue_milestones} critical milestones overdue")
            risk_score += 40
        
        # Resource risks
        high_priority_tasks = len([t for t in tasks if t.priority == "high" and t.status != "completed"])
        if high_priority_tasks > 5:
            risk_factors.append("Resource overload")
            risk_score += 20
        
        # Value risks
        if case.estimated_value > 100000 and case.priority == "low":
            risk_factors.append("High-value case with low priority")
            risk_score += 15
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "critical"
        elif risk_score >= 40:
            risk_level = "high"
        elif risk_score >= 20:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_score": min(risk_score, 100),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_strategies": self._generate_risk_mitigation_strategies(risk_factors)
        }
    
    def _generate_risk_mitigation_strategies(self, risk_factors: List[str]) -> List[str]:
        """Generate strategies to mitigate identified risks."""
        strategies = []
        
        for factor in risk_factors:
            if "timeline" in factor.lower():
                strategies.append("Expedite critical tasks and consider settlement options")
            elif "overdue" in factor.lower():
                strategies.append("Prioritize overdue items and reallocate resources")
            elif "resource" in factor.lower():
                strategies.append("Consider additional staffing or task delegation")
            elif "high-value" in factor.lower():
                strategies.append("Elevate case priority and increase oversight")
        
        return strategies
    
    def _calculate_case_progress(self, case: Case, tasks: List[CaseTask], 
                               milestones: List[CaseMilestone]) -> Dict[str, Any]:
        """Calculate comprehensive case progress metrics."""
        # Task progress
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == "completed"])
        task_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Milestone progress
        total_milestones = len(milestones)
        completed_milestones = len([m for m in milestones if m.status == "completed"])
        milestone_progress = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
        
        # Timeline progress
        if case.estimated_end_date:
            total_days = (case.estimated_end_date - case.start_date).days
            elapsed_days = (datetime.utcnow() - case.start_date).days
            timeline_progress = min((elapsed_days / total_days * 100), 100) if total_days > 0 else 0
        else:
            timeline_progress = 0
        
        # Overall progress (weighted average)
        overall_progress = (task_progress * 0.4 + milestone_progress * 0.4 + timeline_progress * 0.2)
        
        return {
            "overall_progress": round(overall_progress, 1),
            "task_progress": round(task_progress, 1),
            "milestone_progress": round(milestone_progress, 1),
            "timeline_progress": round(timeline_progress, 1),
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "completed_milestones": completed_milestones,
            "total_milestones": total_milestones,
            "progress_status": "ahead" if overall_progress > 75 else "on_track" if overall_progress > 50 else "behind"
        }
    
    def _generate_case_recommendations(self, case: Case, predictions: Dict[str, Any], 
                                     risk_assessment: Dict[str, Any], 
                                     progress_metrics: Dict[str, Any]) -> List[str]:
        """Generate AI recommendations for case management."""
        recommendations = []
        
        # Strategy recommendations
        if predictions["success_probability"] < 0.4:
            recommendations.append("Consider early settlement to minimize costs and risks")
        elif predictions["success_probability"] > 0.8:
            recommendations.append("Strong case position - consider aggressive litigation strategy")
        
        # Risk mitigation recommendations
        if risk_assessment["risk_level"] in ["high", "critical"]:
            recommendations.append("Implement immediate risk mitigation strategies")
        
        # Progress recommendations
        if progress_metrics["progress_status"] == "behind":
            recommendations.append("Case is behind schedule - consider resource reallocation")
        elif progress_metrics["progress_status"] == "ahead":
            recommendations.append("Case is ahead of schedule - consider early resolution options")
        
        # Resource recommendations
        if len(case.assigned_team) < 2 and case.estimated_value > 50000:
            recommendations.append("Consider adding paralegal support for high-value case")
        
        return recommendations
    
    def get_lawyer_case_overview(self, lawyer_id: str) -> Dict[str, Any]:
        """
        Get comprehensive case overview for a lawyer.
        
        Args:
            lawyer_id: Lawyer identifier
            
        Returns:
            Case overview with analytics and insights
        """
        try:
            # Get lawyer's cases
            lawyer_cases = [c for c in self.cases if c.lawyer_id == lawyer_id]
            lawyer_tasks = [t for t in self.tasks if t.assigned_to == lawyer_id]
            
            # Calculate case metrics
            active_cases = len([c for c in lawyer_cases if c.status == "active"])
            high_priority_cases = len([c for c in lawyer_cases if c.priority == "high"])
            total_case_value = sum(c.estimated_value for c in lawyer_cases if c.status == "active")
            
            # Calculate task metrics
            pending_tasks = len([t for t in lawyer_tasks if t.status == "pending"])
            overdue_tasks = len([t for t in lawyer_tasks if t.status == "overdue"])
            completed_tasks = len([t for t in lawyer_tasks if t.status == "completed"])
            
            # Calculate average progress
            case_progresses = []
            for case in lawyer_cases:
                case_tasks = [t for t in lawyer_tasks if t.case_id == case.case_id]
                case_milestones = [m for m in self.milestones if m.case_id == case.case_id]
                progress = self._calculate_case_progress(case, case_tasks, case_milestones)
                case_progresses.append(progress["overall_progress"])
            
            average_progress = sum(case_progresses) / len(case_progresses) if case_progresses else 0
            
            # Get top cases by value
            top_cases = sorted(lawyer_cases, key=lambda c: c.estimated_value, reverse=True)[:5]
            
            overview = {
                "lawyer_id": lawyer_id,
                "case_metrics": {
                    "total_cases": len(lawyer_cases),
                    "active_cases": active_cases,
                    "high_priority_cases": high_priority_cases,
                    "total_case_value": total_case_value,
                    "average_case_value": total_case_value / active_cases if active_cases > 0 else 0
                },
                "task_metrics": {
                    "pending_tasks": pending_tasks,
                    "overdue_tasks": overdue_tasks,
                    "completed_tasks": completed_tasks,
                    "task_completion_rate": (completed_tasks / (completed_tasks + pending_tasks) * 100) if (completed_tasks + pending_tasks) > 0 else 0
                },
                "progress_metrics": {
                    "average_progress": round(average_progress, 1),
                    "cases_ahead": len([p for p in case_progresses if p > 75]),
                    "cases_behind": len([p for p in case_progresses if p < 50])
                },
                "top_cases": [
                    {
                        "case_id": case.case_id,
                        "title": case.title,
                        "case_type": case.case_type,
                        "priority": case.priority,
                        "estimated_value": case.estimated_value,
                        "status": case.status
                    }
                    for case in top_cases
                ],
                "ai_recommendations": self._generate_lawyer_recommendations(
                    lawyer_cases, lawyer_tasks, average_progress
                )
            }
            
            return overview
            
        except Exception as e:
            logger.error(f"Error getting lawyer case overview: {e}")
            raise
    
    def _generate_lawyer_recommendations(self, cases: List[Case], tasks: List[CaseTask], 
                                       average_progress: float) -> List[str]:
        """Generate AI recommendations for lawyer's case management."""
        recommendations = []
        
        # Workload recommendations
        active_cases = len([c for c in cases if c.status == "active"])
        if active_cases > 10:
            recommendations.append("High case load detected - consider delegating or prioritizing")
        
        # Task management recommendations
        overdue_tasks = len([t for t in tasks if t.status == "overdue"])
        if overdue_tasks > 5:
            recommendations.append(f"Address {overdue_tasks} overdue tasks to maintain case quality")
        
        # Progress recommendations
        if average_progress < 50:
            recommendations.append("Overall case progress is below target - review resource allocation")
        elif average_progress > 80:
            recommendations.append("Excellent case progress - consider taking on additional cases")
        
        # Priority recommendations
        high_priority_cases = len([c for c in cases if c.priority == "high" and c.status == "active"])
        if high_priority_cases > 3:
            recommendations.append("Multiple high-priority cases - ensure adequate focus on each")
        
        return recommendations 