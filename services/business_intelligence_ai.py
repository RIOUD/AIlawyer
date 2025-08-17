#!/usr/bin/env python3
"""
AI-Powered Business Intelligence

AI system that predicts business opportunities and optimizes practice growth
through data-driven insights and strategic recommendations.

Features:
- Revenue opportunity identification and prediction
- Practice growth optimization
- Client retention risk assessment
- Efficiency improvement recommendations
- Market trend analysis and competitive intelligence
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class BusinessMetrics:
    """Data class for business metrics."""
    lawyer_id: str
    total_revenue: float
    billable_hours: float
    client_count: int
    case_count: int
    average_case_value: float
    client_retention_rate: float
    efficiency_score: float
    timestamp: datetime


@dataclass
class RevenueOpportunity:
    """Data class for revenue opportunities."""
    opportunity_id: str
    lawyer_id: str
    opportunity_type: str
    description: str
    potential_revenue: float
    confidence_level: str  # high, medium, low
    implementation_difficulty: str  # easy, medium, hard
    time_to_implement: str  # immediate, short_term, long_term
    risk_level: str  # low, medium, high
    created_at: datetime


@dataclass
class EfficiencyImprovement:
    """Data class for efficiency improvements."""
    improvement_id: str
    lawyer_id: str
    area: str
    current_efficiency: float
    potential_efficiency: float
    time_saved_percentage: float
    cost_savings: float
    implementation_cost: float
    roi: float
    priority: str  # high, medium, low
    created_at: datetime


class BusinessIntelligenceAI:
    """
    AI-powered business intelligence system.
    
    Provides data-driven insights for practice growth,
    revenue optimization, and strategic decision-making.
    """
    
    def __init__(self):
        """Initialize the business intelligence AI system."""
        self.opportunity_types = {
            "upsell_compliance_monitoring": {
                "base_revenue": 25000,
                "implementation_time": "1-2 months",
                "difficulty": "medium",
                "target_clients": "corporate_clients"
            },
            "expand_employment_practice": {
                "base_revenue": 100000,
                "implementation_time": "3-6 months",
                "difficulty": "hard",
                "target_clients": "all_clients"
            },
            "automate_contract_review": {
                "base_revenue": 75000,
                "implementation_time": "2-3 months",
                "difficulty": "medium",
                "target_clients": "high_volume_clients"
            },
            "add_ip_services": {
                "base_revenue": 150000,
                "implementation_time": "4-8 months",
                "difficulty": "hard",
                "target_clients": "tech_clients"
            },
            "implement_retainer_program": {
                "base_revenue": 50000,
                "implementation_time": "1 month",
                "difficulty": "easy",
                "target_clients": "existing_clients"
            }
        }
        
        self.efficiency_areas = {
            "document_generation": {
                "current_avg_efficiency": 0.6,
                "potential_efficiency": 0.9,
                "time_savings": 0.4,
                "implementation_cost": 10000
            },
            "client_communication": {
                "current_avg_efficiency": 0.7,
                "potential_efficiency": 0.95,
                "time_savings": 0.3,
                "implementation_cost": 5000
            },
            "research_efficiency": {
                "current_avg_efficiency": 0.5,
                "potential_efficiency": 0.85,
                "time_savings": 0.6,
                "implementation_cost": 15000
            },
            "billing_optimization": {
                "current_avg_efficiency": 0.8,
                "potential_efficiency": 0.95,
                "time_savings": 0.2,
                "implementation_cost": 3000
            }
        }
        
        # In-memory storage (replace with database in production)
        self.business_metrics = []
        self.revenue_opportunities = []
        self.efficiency_improvements = []
        
        logger.info("Business Intelligence AI initialized")
    
    def get_lawyer_insights(self, lawyer_id: str) -> Dict[str, Any]:
        """
        Get comprehensive business intelligence insights for a lawyer.
        
        Args:
            lawyer_id: Lawyer identifier
            
        Returns:
            Business intelligence insights and recommendations
        """
        try:
            # Get lawyer's business metrics
            metrics = self._get_lawyer_metrics(lawyer_id)
            
            # Generate revenue opportunities
            revenue_opportunities = self._identify_revenue_opportunities(lawyer_id, metrics)
            
            # Calculate efficiency improvements
            efficiency_improvements = self._calculate_efficiency_improvements(lawyer_id, metrics)
            
            # Assess client retention risks
            retention_risks = self._assess_client_retention_risks(lawyer_id)
            
            # Generate growth projections
            growth_projections = self._generate_growth_projections(lawyer_id, metrics)
            
            # Calculate practice optimization recommendations
            optimization_recommendations = self._generate_optimization_recommendations(
                lawyer_id, metrics, revenue_opportunities, efficiency_improvements
            )
            
            insights = {
                "lawyer_id": lawyer_id,
                "current_metrics": {
                    "total_revenue": metrics.total_revenue if metrics else 0,
                    "billable_hours": metrics.billable_hours if metrics else 0,
                    "client_count": metrics.client_count if metrics else 0,
                    "case_count": metrics.case_count if metrics else 0,
                    "average_case_value": metrics.average_case_value if metrics else 0,
                    "client_retention_rate": metrics.client_retention_rate if metrics else 0,
                    "efficiency_score": metrics.efficiency_score if metrics else 0
                },
                "revenue_opportunities": revenue_opportunities,
                "efficiency_improvements": efficiency_improvements,
                "client_retention_risks": retention_risks,
                "growth_projections": growth_projections,
                "optimization_recommendations": optimization_recommendations,
                "ai_insights": self._generate_ai_insights(
                    metrics, revenue_opportunities, efficiency_improvements, retention_risks
                )
            }
            
            logger.info(f"Business intelligence insights generated for lawyer {lawyer_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Error getting lawyer insights: {e}")
            raise
    
    def _get_lawyer_metrics(self, lawyer_id: str) -> Optional[BusinessMetrics]:
        """Get lawyer's business metrics."""
        # Find most recent metrics for the lawyer
        lawyer_metrics = [m for m in self.business_metrics if m.lawyer_id == lawyer_id]
        if lawyer_metrics:
            return max(lawyer_metrics, key=lambda x: x.timestamp)
        return None
    
    def _identify_revenue_opportunities(self, lawyer_id: str, 
                                     metrics: Optional[BusinessMetrics]) -> List[Dict[str, Any]]:
        """Identify revenue optimization opportunities."""
        opportunities = []
        
        # Upselling opportunities
        if metrics and metrics.client_count > 5:
            opportunities.append({
                "type": "upsell_compliance_monitoring",
                "description": "Add compliance monitoring service for existing corporate clients",
                "potential_revenue": 25000,
                "confidence": "high",
                "implementation_difficulty": "medium",
                "time_to_implement": "1-2 months",
                "reason": f"High client count ({metrics.client_count}) suggests upselling potential"
            })
        
        # Service expansion opportunities
        if metrics and metrics.average_case_value < 30000:
            opportunities.append({
                "type": "expand_employment_practice",
                "description": "Expand into employment law for higher-value cases",
                "potential_revenue": 100000,
                "confidence": "medium",
                "implementation_difficulty": "hard",
                "time_to_implement": "3-6 months",
                "reason": "Low average case value suggests opportunity for higher-value practice areas"
            })
        
        # Automation opportunities
        if metrics and metrics.case_count > 10:
            opportunities.append({
                "type": "automate_contract_review",
                "description": "Implement AI-powered contract review automation",
                "potential_revenue": 75000,
                "confidence": "high",
                "implementation_difficulty": "medium",
                "time_to_implement": "2-3 months",
                "reason": f"High case volume ({metrics.case_count}) suggests automation benefits"
            })
        
        # Retainer program opportunities
        if metrics and metrics.client_retention_rate > 0.8:
            opportunities.append({
                "type": "implement_retainer_program",
                "description": "Implement retainer program for stable revenue",
                "potential_revenue": 50000,
                "confidence": "high",
                "implementation_difficulty": "easy",
                "time_to_implement": "1 month",
                "reason": f"High retention rate ({metrics.client_retention_rate:.1%}) supports retainer model"
            })
        
        return opportunities
    
    def _calculate_efficiency_improvements(self, lawyer_id: str, 
                                         metrics: Optional[BusinessMetrics]) -> List[Dict[str, Any]]:
        """Calculate efficiency improvement opportunities."""
        improvements = []
        
        # Document generation efficiency
        current_efficiency = metrics.efficiency_score if metrics else 0.6
        doc_config = self.efficiency_areas["document_generation"]
        
        if current_efficiency < doc_config["potential_efficiency"]:
            time_saved = doc_config["time_savings"] * 100
            cost_savings = time_saved * 250  # Assuming €250/hour rate
            roi = (cost_savings - doc_config["implementation_cost"]) / doc_config["implementation_cost"]
            
            improvements.append({
                "area": "document_generation",
                "current_efficiency": round(current_efficiency * 100, 1),
                "potential_efficiency": round(doc_config["potential_efficiency"] * 100, 1),
                "time_saved_percentage": round(time_saved, 1),
                "cost_savings": round(cost_savings, 0),
                "implementation_cost": doc_config["implementation_cost"],
                "roi": round(roi * 100, 1),
                "priority": "high" if roi > 2 else "medium"
            })
        
        # Client communication efficiency
        comm_config = self.efficiency_areas["client_communication"]
        if current_efficiency < comm_config["potential_efficiency"]:
            time_saved = comm_config["time_savings"] * 100
            cost_savings = time_saved * 250
            roi = (cost_savings - comm_config["implementation_cost"]) / comm_config["implementation_cost"]
            
            improvements.append({
                "area": "client_communication",
                "current_efficiency": round(current_efficiency * 100, 1),
                "potential_efficiency": round(comm_config["potential_efficiency"] * 100, 1),
                "time_saved_percentage": round(time_saved, 1),
                "cost_savings": round(cost_savings, 0),
                "implementation_cost": comm_config["implementation_cost"],
                "roi": round(roi * 100, 1),
                "priority": "high" if roi > 2 else "medium"
            })
        
        # Research efficiency
        research_config = self.efficiency_areas["research_efficiency"]
        if current_efficiency < research_config["potential_efficiency"]:
            time_saved = research_config["time_savings"] * 100
            cost_savings = time_saved * 250
            roi = (cost_savings - research_config["implementation_cost"]) / research_config["implementation_cost"]
            
            improvements.append({
                "area": "research_efficiency",
                "current_efficiency": round(current_efficiency * 100, 1),
                "potential_efficiency": round(research_config["potential_efficiency"] * 100, 1),
                "time_saved_percentage": round(time_saved, 1),
                "cost_savings": round(cost_savings, 0),
                "implementation_cost": research_config["implementation_cost"],
                "roi": round(roi * 100, 1),
                "priority": "high" if roi > 2 else "medium"
            })
        
        return improvements
    
    def _assess_client_retention_risks(self, lawyer_id: str) -> List[Dict[str, Any]]:
        """Assess client retention risks."""
        risks = []
        
        # This would typically integrate with CRM data
        # For now, provide sample risk assessment
        sample_risks = [
            {
                "client_id": "CLIENT-001",
                "client_name": "ABC Corp",
                "risk_level": "high",
                "risk_factors": ["no_recent_contact", "billing_disputes"],
                "potential_revenue_loss": 50000,
                "mitigation_strategy": "Schedule immediate client check-in call"
            },
            {
                "client_id": "CLIENT-002",
                "client_name": "XYZ Ltd",
                "risk_level": "medium",
                "risk_factors": ["delayed_response_times"],
                "potential_revenue_loss": 25000,
                "mitigation_strategy": "Improve response time and communication"
            }
        ]
        
        return sample_risks
    
    def _generate_growth_projections(self, lawyer_id: str, 
                                   metrics: Optional[BusinessMetrics]) -> Dict[str, Any]:
        """Generate growth projections for the lawyer."""
        if not metrics:
            return {
                "current_revenue": 0,
                "projected_revenue_6_months": 0,
                "projected_revenue_12_months": 0,
                "growth_rate": 0,
                "growth_factors": []
            }
        
        # Calculate growth rate based on historical data
        # This would typically use historical metrics
        growth_rate = 0.15  # 15% annual growth rate (sample)
        
        # Project revenue
        projected_6_months = metrics.total_revenue * (1 + growth_rate * 0.5)
        projected_12_months = metrics.total_revenue * (1 + growth_rate)
        
        # Identify growth factors
        growth_factors = []
        if metrics.client_count > 10:
            growth_factors.append("Strong client base supports growth")
        if metrics.efficiency_score > 0.8:
            growth_factors.append("High efficiency enables capacity for growth")
        if metrics.client_retention_rate > 0.9:
            growth_factors.append("Excellent client retention provides stable foundation")
        
        return {
            "current_revenue": metrics.total_revenue,
            "projected_revenue_6_months": round(projected_6_months, 0),
            "projected_revenue_12_months": round(projected_12_months, 0),
            "growth_rate": round(growth_rate * 100, 1),
            "growth_factors": growth_factors
        }
    
    def _generate_optimization_recommendations(self, lawyer_id: str, metrics: Optional[BusinessMetrics],
                                            revenue_opportunities: List[Dict[str, Any]],
                                            efficiency_improvements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate practice optimization recommendations."""
        recommendations = []
        
        # Revenue optimization recommendations
        total_potential_revenue = sum(opp["potential_revenue"] for opp in revenue_opportunities)
        if total_potential_revenue > 100000:
            recommendations.append({
                "type": "revenue_optimization",
                "title": "High Revenue Opportunity",
                "description": f"€{total_potential_revenue:,.0f} in potential revenue identified",
                "priority": "high",
                "timeline": "3-6 months",
                "impact": "significant_revenue_increase"
            })
        
        # Efficiency optimization recommendations
        total_efficiency_savings = sum(imp["cost_savings"] for imp in efficiency_improvements)
        if total_efficiency_savings > 50000:
            recommendations.append({
                "type": "efficiency_optimization",
                "title": "Efficiency Improvement",
                "description": f"€{total_efficiency_savings:,.0f} in potential cost savings",
                "priority": "high",
                "timeline": "1-3 months",
                "impact": "cost_reduction_and_time_savings"
            })
        
        # Client retention recommendations
        if metrics and metrics.client_retention_rate < 0.8:
            recommendations.append({
                "type": "client_retention",
                "title": "Improve Client Retention",
                "description": f"Current retention rate: {metrics.client_retention_rate:.1%}",
                "priority": "medium",
                "timeline": "immediate",
                "impact": "stable_revenue_foundation"
            })
        
        # Practice expansion recommendations
        if metrics and metrics.average_case_value < 25000:
            recommendations.append({
                "type": "practice_expansion",
                "title": "Expand Practice Areas",
                "description": "Consider higher-value practice areas",
                "priority": "medium",
                "timeline": "6-12 months",
                "impact": "increased_case_values"
            })
        
        return recommendations
    
    def _generate_ai_insights(self, metrics: Optional[BusinessMetrics],
                            revenue_opportunities: List[Dict[str, Any]],
                            efficiency_improvements: List[Dict[str, Any]],
                            retention_risks: List[Dict[str, Any]]) -> List[str]:
        """Generate AI insights about the practice."""
        insights = []
        
        if not metrics:
            insights.append("No business metrics available - consider implementing tracking")
            return insights
        
        # Revenue insights
        total_opportunity = sum(opp["potential_revenue"] for opp in revenue_opportunities)
        if total_opportunity > metrics.total_revenue * 0.5:
            insights.append(f"High revenue opportunity: €{total_opportunity:,.0f} potential ({(total_opportunity/metrics.total_revenue)*100:.0f}% of current revenue)")
        
        # Efficiency insights
        if metrics.efficiency_score < 0.7:
            insights.append("Efficiency below target - focus on process optimization")
        elif metrics.efficiency_score > 0.9:
            insights.append("Excellent efficiency - consider expanding capacity")
        
        # Client insights
        if metrics.client_retention_rate < 0.8:
            insights.append("Client retention needs improvement - focus on relationship building")
        elif metrics.client_retention_rate > 0.95:
            insights.append("Outstanding client retention - leverage for referrals and expansion")
        
        # Growth insights
        if metrics.client_count < 5:
            insights.append("Small client base - focus on client acquisition")
        elif metrics.client_count > 20:
            insights.append("Large client base - optimize for efficiency and upselling")
        
        return insights
    
    def practice_optimization(self, practice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI recommendations for practice growth and optimization.
        
        Args:
            practice_data: Practice information and metrics
            
        Returns:
            Practice optimization recommendations
        """
        try:
            # Extract practice metrics
            total_revenue = practice_data.get("total_revenue", 0)
            lawyer_count = practice_data.get("lawyer_count", 1)
            client_count = practice_data.get("client_count", 0)
            average_case_value = practice_data.get("average_case_value", 0)
            
            # Calculate revenue opportunities
            revenue_opportunities = []
            
            # Upselling opportunities
            if client_count > 10:
                revenue_opportunities.append({
                    "type": "upsell_compliance_monitoring",
                    "potential": 50000,
                    "description": "Add compliance monitoring for existing corporate clients",
                    "implementation_time": "1-2 months"
                })
            
            # Practice expansion opportunities
            if average_case_value < 30000:
                revenue_opportunities.append({
                    "type": "expand_employment_practice",
                    "potential": 100000,
                    "description": "Expand into employment law for higher-value cases",
                    "implementation_time": "3-6 months"
                })
            
            # Automation opportunities
            if lawyer_count > 2:
                revenue_opportunities.append({
                    "type": "automate_contract_review",
                    "potential": 75000,
                    "description": "Implement AI-powered contract review automation",
                    "implementation_time": "2-3 months"
                })
            
            # Calculate efficiency improvements
            efficiency_improvements = []
            
            # Document generation efficiency
            efficiency_improvements.append({
                "area": "document_generation",
                "time_saved": "40%",
                "description": "Automate document generation and template management",
                "implementation_cost": 10000
            })
            
            # Client communication efficiency
            efficiency_improvements.append({
                "area": "client_communication",
                "time_saved": "30%",
                "description": "Streamline client communication and status updates",
                "implementation_cost": 5000
            })
            
            # Research efficiency
            efficiency_improvements.append({
                "area": "research_efficiency",
                "time_saved": "60%",
                "description": "Implement AI-powered legal research tools",
                "implementation_cost": 15000
            })
            
            # Assess client retention risks
            client_retention_risks = []
            
            # Sample risk assessment (would integrate with CRM data)
            if client_count > 20:
                client_retention_risks.append({
                    "client": "ABC Corp",
                    "risk_level": "high",
                    "reason": "no_recent_contact",
                    "potential_loss": 50000
                })
            
            if client_count > 15:
                client_retention_risks.append({
                    "client": "XYZ Ltd",
                    "risk_level": "medium",
                    "reason": "billing_concerns",
                    "potential_loss": 25000
                })
            
            optimization_data = {
                "practice_metrics": {
                    "total_revenue": total_revenue,
                    "lawyer_count": lawyer_count,
                    "client_count": client_count,
                    "average_case_value": average_case_value
                },
                "revenue_opportunities": revenue_opportunities,
                "efficiency_improvements": efficiency_improvements,
                "client_retention_risks": client_retention_risks,
                "total_opportunity": sum(opp["potential"] for opp in revenue_opportunities),
                "total_efficiency_savings": sum(imp["implementation_cost"] * 0.5 for imp in efficiency_improvements),
                "ai_recommendations": self._generate_practice_recommendations(
                    total_revenue, lawyer_count, client_count, average_case_value
                )
            }
            
            return optimization_data
            
        except Exception as e:
            logger.error(f"Error in practice optimization: {e}")
            raise
    
    def _generate_practice_recommendations(self, total_revenue: float, lawyer_count: int,
                                         client_count: int, average_case_value: float) -> List[str]:
        """Generate AI recommendations for practice optimization."""
        recommendations = []
        
        # Revenue optimization recommendations
        if total_revenue < 500000:
            recommendations.append("Focus on client acquisition and case value optimization")
        elif total_revenue > 2000000:
            recommendations.append("Consider practice expansion and additional lawyer hiring")
        
        # Client base recommendations
        if client_count < 10:
            recommendations.append("Build client base through networking and marketing")
        elif client_count > 50:
            recommendations.append("Optimize client management and consider client segmentation")
        
        # Case value recommendations
        if average_case_value < 20000:
            recommendations.append("Focus on higher-value practice areas and case types")
        elif average_case_value > 100000:
            recommendations.append("Consider expanding into related high-value practice areas")
        
        # Efficiency recommendations
        if lawyer_count > 3:
            recommendations.append("Implement practice management software for efficiency")
        
        return recommendations
    
    def add_business_metrics(self, lawyer_id: str, total_revenue: float, billable_hours: float,
                           client_count: int, case_count: int, average_case_value: float,
                           client_retention_rate: float, efficiency_score: float):
        """
        Add business metrics for a lawyer.
        
        Args:
            lawyer_id: Lawyer identifier
            total_revenue: Total annual revenue
            billable_hours: Total billable hours
            client_count: Number of active clients
            case_count: Number of active cases
            average_case_value: Average case value
            client_retention_rate: Client retention rate (0-1)
            efficiency_score: Efficiency score (0-1)
        """
        try:
            metrics = BusinessMetrics(
                lawyer_id=lawyer_id,
                total_revenue=total_revenue,
                billable_hours=billable_hours,
                client_count=client_count,
                case_count=case_count,
                average_case_value=average_case_value,
                client_retention_rate=client_retention_rate,
                efficiency_score=efficiency_score,
                timestamp=datetime.utcnow()
            )
            
            self.business_metrics.append(metrics)
            
            logger.info(f"Business metrics added for lawyer {lawyer_id}")
            
        except Exception as e:
            logger.error(f"Error adding business metrics: {e}")
            raise 