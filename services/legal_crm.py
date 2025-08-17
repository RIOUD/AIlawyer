#!/usr/bin/env python3
"""
Client Relationship Management (CRM)

Comprehensive client management system with AI-powered insights,
client retention optimization, and revenue growth opportunities.

Features:
- 360° client view with all interactions
- AI-powered client insights and recommendations
- Revenue optimization and upselling opportunities
- Client satisfaction tracking and retention analysis
- Communication history and relationship building
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class Client:
    """Data class for client information."""
    client_id: str
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    industry: Optional[str]
    client_type: str  # individual, corporate, government
    billing_address: Optional[str]
    created_at: datetime
    last_contact: Optional[datetime]
    status: str  # active, inactive, prospect
    value_tier: str  # platinum, gold, silver, bronze
    lawyer_id: str


@dataclass
class ClientMatter:
    """Data class for client matters/cases."""
    matter_id: str
    client_id: str
    matter_type: str
    title: str
    description: str
    status: str  # active, closed, pending
    start_date: datetime
    end_date: Optional[datetime]
    estimated_value: float
    actual_value: Optional[float]
    priority: str  # high, medium, low
    lawyer_id: str


@dataclass
class ClientInteraction:
    """Data class for client interactions."""
    interaction_id: str
    client_id: str
    interaction_type: str  # meeting, call, email, document_review
    description: str
    timestamp: datetime
    duration: Optional[float]  # in minutes
    outcome: str
    follow_up_required: bool
    follow_up_date: Optional[datetime]
    lawyer_id: str


class LegalCRM:
    """
    AI-powered client relationship management system.
    
    Provides comprehensive client insights, retention optimization,
    and revenue growth opportunities for legal professionals.
    """
    
    def __init__(self):
        """Initialize the legal CRM system."""
        self.client_value_tiers = {
            "platinum": {"min_value": 100000, "retention_priority": "highest"},
            "gold": {"min_value": 50000, "retention_priority": "high"},
            "silver": {"min_value": 20000, "retention_priority": "medium"},
            "bronze": {"min_value": 0, "retention_priority": "standard"}
        }
        
        # In-memory storage (replace with database in production)
        self.clients = []
        self.matters = []
        self.interactions = []
        
        logger.info("Legal CRM initialized")
    
    def get_client_dashboard(self, client_id: str) -> Dict[str, Any]:
        """
        Get comprehensive client dashboard with AI insights.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Complete client overview with AI-powered insights
        """
        try:
            # Get client information
            client = self._get_client(client_id)
            if not client:
                raise ValueError(f"Client {client_id} not found")
            
            # Get client matters
            client_matters = [m for m in self.matters if m.client_id == client_id]
            
            # Get recent interactions
            recent_interactions = self._get_recent_interactions(client_id, days=30)
            
            # Get billing information
            billing_summary = self._get_billing_summary(client_id)
            
            # Generate AI insights
            ai_insights = self._generate_client_insights(client, client_matters, recent_interactions)
            
            # Get retention risk assessment
            retention_risk = self._assess_retention_risk(client, recent_interactions)
            
            # Get upselling opportunities
            upselling_opportunities = self._identify_upselling_opportunities(client, client_matters)
            
            dashboard = {
                "client_info": {
                    "client_id": client.client_id,
                    "name": client.name,
                    "email": client.email,
                    "company": client.company,
                    "industry": client.industry,
                    "client_type": client.client_type,
                    "status": client.status,
                    "value_tier": client.value_tier,
                    "created_at": client.created_at.isoformat(),
                    "last_contact": client.last_contact.isoformat() if client.last_contact else None
                },
                "active_matters": [
                    {
                        "matter_id": matter.matter_id,
                        "matter_type": matter.matter_type,
                        "title": matter.title,
                        "status": matter.status,
                        "priority": matter.priority,
                        "estimated_value": matter.estimated_value,
                        "actual_value": matter.actual_value,
                        "start_date": matter.start_date.isoformat(),
                        "days_active": (datetime.utcnow() - matter.start_date).days
                    }
                    for matter in client_matters if matter.status == "active"
                ],
                "billing_summary": billing_summary,
                "communication_history": [
                    {
                        "interaction_id": interaction.interaction_id,
                        "type": interaction.interaction_type,
                        "description": interaction.description,
                        "timestamp": interaction.timestamp.isoformat(),
                        "outcome": interaction.outcome,
                        "follow_up_required": interaction.follow_up_required
                    }
                    for interaction in recent_interactions
                ],
                "ai_insights": ai_insights,
                "retention_risk": retention_risk,
                "upselling_opportunities": upselling_opportunities,
                "recommended_actions": self._generate_recommended_actions(
                    client, retention_risk, upselling_opportunities
                )
            }
            
            logger.info(f"Client dashboard generated for {client.name}")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting client dashboard: {e}")
            raise
    
    def _get_client(self, client_id: str) -> Optional[Client]:
        """Get client by ID."""
        for client in self.clients:
            if client.client_id == client_id:
                return client
        return None
    
    def _get_recent_interactions(self, client_id: str, days: int = 30) -> List[ClientInteraction]:
        """Get recent client interactions."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [
            interaction for interaction in self.interactions
            if interaction.client_id == client_id and interaction.timestamp >= cutoff_date
        ]
    
    def _get_billing_summary(self, client_id: str) -> Dict[str, Any]:
        """Get billing summary for client."""
        client_matters = [m for m in self.matters if m.client_id == client_id]
        
        total_estimated = sum(m.estimated_value for m in client_matters)
        total_actual = sum(m.actual_value for m in client_matters if m.actual_value)
        active_matters = len([m for m in client_matters if m.status == "active"])
        
        return {
            "total_estimated_value": total_estimated,
            "total_actual_value": total_actual,
            "active_matters": active_matters,
            "average_matter_value": total_estimated / len(client_matters) if client_matters else 0,
            "billing_efficiency": (total_actual / total_estimated * 100) if total_estimated > 0 else 0
        }
    
    def _generate_client_insights(self, client: Client, matters: List[ClientMatter], 
                                interactions: List[ClientInteraction]) -> List[str]:
        """Generate AI insights about the client."""
        insights = []
        
        # Communication preferences
        if interactions:
            interaction_types = [i.interaction_type for i in interactions]
            most_common_type = max(set(interaction_types), key=interaction_types.count)
            insights.append(f"Client prefers {most_common_type} communication")
        
        # Matter analysis
        if matters:
            avg_matter_value = sum(m.estimated_value for m in matters) / len(matters)
            if avg_matter_value > 50000:
                insights.append("High-value client - prioritize responsiveness")
            elif avg_matter_value < 10000:
                insights.append("Consider upselling to higher-value services")
        
        # Engagement analysis
        days_since_last_contact = (datetime.utcnow() - client.last_contact).days if client.last_contact else 999
        if days_since_last_contact > 30:
            insights.append("Client may need re-engagement - consider proactive outreach")
        elif days_since_last_contact < 7:
            insights.append("Recently engaged client - good relationship momentum")
        
        # Industry insights
        if client.industry:
            insights.append(f"Industry expertise in {client.industry} - leverage for referrals")
        
        return insights
    
    def _assess_retention_risk(self, client: Client, 
                             interactions: List[ClientInteraction]) -> Dict[str, Any]:
        """Assess client retention risk."""
        risk_factors = []
        risk_score = 0
        
        # Time since last contact
        if client.last_contact:
            days_since_contact = (datetime.utcnow() - client.last_contact).days
            if days_since_contact > 60:
                risk_factors.append("No recent contact")
                risk_score += 30
            elif days_since_contact > 30:
                risk_factors.append("Limited recent contact")
                risk_score += 15
        
        # Interaction frequency
        if len(interactions) < 3:
            risk_factors.append("Low interaction frequency")
            risk_score += 20
        
        # Matter status
        active_matters = [m for m in self.matters if m.client_id == client.client_id and m.status == "active"]
        if not active_matters:
            risk_factors.append("No active matters")
            risk_score += 25
        
        # Value tier consideration
        if client.value_tier in ["platinum", "gold"]:
            risk_score *= 1.5  # Higher risk for high-value clients
        
        # Determine risk level
        if risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 25:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_score": min(risk_score, 100),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "retention_priority": self.client_value_tiers[client.value_tier]["retention_priority"]
        }
    
    def _identify_upselling_opportunities(self, client: Client, 
                                        matters: List[ClientMatter]) -> List[Dict[str, Any]]:
        """Identify upselling opportunities for the client."""
        opportunities = []
        
        # Service expansion opportunities
        current_services = [m.matter_type for m in matters]
        
        if "employment_contract" in current_services and "compliance_monitoring" not in current_services:
            opportunities.append({
                "type": "service_expansion",
                "description": "Add compliance monitoring service",
                "potential_value": 25000,
                "confidence": "high",
                "reason": "Client has employment contracts but no ongoing compliance"
            })
        
        if "contract_review" in current_services and "contract_automation" not in current_services:
            opportunities.append({
                "type": "service_expansion",
                "description": "Contract automation and template system",
                "potential_value": 15000,
                "confidence": "medium",
                "reason": "Client regularly reviews contracts - automation would add value"
            })
        
        # Volume-based opportunities
        if len(matters) > 5:
            opportunities.append({
                "type": "volume_discount",
                "description": "Volume discount program",
                "potential_value": 10000,
                "confidence": "high",
                "reason": "High volume client - consider retainer arrangement"
            })
        
        # Industry-specific opportunities
        if client.industry == "technology":
            opportunities.append({
                "type": "industry_specialization",
                "description": "IP protection and licensing services",
                "potential_value": 35000,
                "confidence": "medium",
                "reason": "Tech industry clients often need IP services"
            })
        
        return opportunities
    
    def _generate_recommended_actions(self, client: Client, retention_risk: Dict[str, Any],
                                    upselling_opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate recommended actions for client management."""
        actions = []
        
        # Retention actions
        if retention_risk["risk_level"] == "high":
            actions.append({
                "priority": "urgent",
                "action": "Schedule client check-in call",
                "description": "Proactive outreach to address retention concerns",
                "timeline": "within 3 days",
                "type": "retention"
            })
        
        if retention_risk["risk_level"] in ["medium", "high"]:
            actions.append({
                "priority": "high",
                "action": "Send personalized update",
                "description": "Provide value-added information relevant to client's business",
                "timeline": "within 1 week",
                "type": "engagement"
            })
        
        # Upselling actions
        for opportunity in upselling_opportunities[:2]:  # Top 2 opportunities
            actions.append({
                "priority": "medium",
                "action": f"Present {opportunity['description']}",
                "description": f"Upselling opportunity: {opportunity['reason']}",
                "timeline": "within 2 weeks",
                "type": "revenue_growth",
                "potential_value": opportunity["potential_value"]
            })
        
        # Relationship building actions
        if client.value_tier in ["platinum", "gold"]:
            actions.append({
                "priority": "medium",
                "action": "Invite to exclusive client event",
                "description": "Strengthen relationship with high-value client",
                "timeline": "within 1 month",
                "type": "relationship_building"
            })
        
        return actions
    
    def get_lawyer_client_insights(self, lawyer_id: str) -> Dict[str, Any]:
        """
        Get comprehensive client insights for a lawyer.
        
        Args:
            lawyer_id: Lawyer identifier
            
        Returns:
            Client insights and recommendations for the lawyer
        """
        try:
            # Get lawyer's clients
            lawyer_clients = [c for c in self.clients if c.lawyer_id == lawyer_id]
            lawyer_matters = [m for m in self.matters if m.lawyer_id == lawyer_id]
            lawyer_interactions = [i for i in self.interactions if i.lawyer_id == lawyer_id]
            
            # Calculate client metrics
            total_clients = len(lawyer_clients)
            active_clients = len([c for c in lawyer_clients if c.status == "active"])
            high_value_clients = len([c for c in lawyer_clients if c.value_tier in ["platinum", "gold"]])
            
            # Calculate revenue metrics
            total_estimated_revenue = sum(m.estimated_value for m in lawyer_matters)
            total_actual_revenue = sum(m.actual_value for m in lawyer_matters if m.actual_value)
            
            # Client satisfaction analysis
            recent_interactions = [i for i in lawyer_interactions 
                                 if i.timestamp >= datetime.utcnow() - timedelta(days=30)]
            positive_outcomes = len([i for i in recent_interactions if "positive" in i.outcome.lower()])
            satisfaction_rate = (positive_outcomes / len(recent_interactions) * 100) if recent_interactions else 0
            
            # Retention risk analysis
            retention_risks = []
            for client in lawyer_clients:
                client_interactions = [i for i in lawyer_interactions if i.client_id == client.client_id]
                risk = self._assess_retention_risk(client, client_interactions)
                if risk["risk_level"] in ["medium", "high"]:
                    retention_risks.append({
                        "client_id": client.client_id,
                        "client_name": client.name,
                        "risk_level": risk["risk_level"],
                        "risk_score": risk["risk_score"],
                        "risk_factors": risk["risk_factors"]
                    })
            
            # Top clients by value
            top_clients = sorted(lawyer_clients, 
                               key=lambda c: sum(m.estimated_value for m in lawyer_matters if m.client_id == c.client_id),
                               reverse=True)[:5]
            
            insights = {
                "lawyer_id": lawyer_id,
                "client_metrics": {
                    "total_clients": total_clients,
                    "active_clients": active_clients,
                    "high_value_clients": high_value_clients,
                    "client_retention_rate": (active_clients / total_clients * 100) if total_clients > 0 else 0
                },
                "revenue_metrics": {
                    "total_estimated_revenue": total_estimated_revenue,
                    "total_actual_revenue": total_actual_revenue,
                    "revenue_efficiency": (total_actual_revenue / total_estimated_revenue * 100) if total_estimated_revenue > 0 else 0,
                    "average_client_value": total_estimated_revenue / total_clients if total_clients > 0 else 0
                },
                "satisfaction_metrics": {
                    "satisfaction_rate": round(satisfaction_rate, 2),
                    "recent_interactions": len(recent_interactions),
                    "positive_outcomes": positive_outcomes
                },
                "retention_risks": retention_risks,
                "top_clients": [
                    {
                        "client_id": client.client_id,
                        "name": client.name,
                        "value_tier": client.value_tier,
                        "total_value": sum(m.estimated_value for m in lawyer_matters if m.client_id == client.client_id)
                    }
                    for client in top_clients
                ],
                "ai_recommendations": self._generate_lawyer_recommendations(
                    lawyer_clients, lawyer_matters, retention_risks
                )
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting lawyer client insights: {e}")
            raise
    
    def _generate_lawyer_recommendations(self, clients: List[Client], 
                                       matters: List[ClientMatter],
                                       retention_risks: List[Dict[str, Any]]) -> List[str]:
        """Generate AI recommendations for lawyer's client management."""
        recommendations = []
        
        # Retention recommendations
        if retention_risks:
            high_risk_count = len([r for r in retention_risks if r["risk_level"] == "high"])
            if high_risk_count > 0:
                recommendations.append(f"Address {high_risk_count} high-risk client relationships immediately")
        
        # Revenue optimization
        total_estimated = sum(m.estimated_value for m in matters)
        total_actual = sum(m.actual_value for m in matters if m.actual_value)
        if total_estimated > 0 and (total_actual / total_estimated) < 0.8:
            recommendations.append("Revenue efficiency below target - focus on billing optimization")
        
        # Client development
        active_clients = len([c for c in clients if c.status == "active"])
        if active_clients < 10:
            recommendations.append("Consider expanding client base for revenue diversification")
        
        # High-value client focus
        high_value_clients = [c for c in clients if c.value_tier in ["platinum", "gold"]]
        if high_value_clients:
            recommendations.append(f"Focus on {len(high_value_clients)} high-value clients for maximum ROI")
        
        return recommendations
    
    def add_client(self, name: str, email: str, lawyer_id: str, 
                  company: str = None, industry: str = None,
                  client_type: str = "individual") -> Dict[str, Any]:
        """
        Add new client to the CRM system.
        
        Args:
            name: Client name
            email: Client email
            lawyer_id: Assigned lawyer
            company: Company name (optional)
            industry: Industry (optional)
            client_type: Type of client
            
        Returns:
            Created client information
        """
        try:
            # Generate client ID
            client_id = self._generate_client_id()
            
            # Create client
            client = Client(
                client_id=client_id,
                name=name,
                email=email,
                phone=None,
                company=company,
                industry=industry,
                client_type=client_type,
                billing_address=None,
                created_at=datetime.utcnow(),
                last_contact=None,
                status="active",
                value_tier="bronze",  # Will be updated based on matter value
                lawyer_id=lawyer_id
            )
            
            # Store client
            self.clients.append(client)
            
            logger.info(f"Client added: {name} ({client_id})")
            return {
                "client_id": client_id,
                "name": name,
                "email": email,
                "status": "active",
                "created_at": client.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adding client: {e}")
            raise
    
    def _generate_client_id(self) -> str:
        """Generate unique client identifier."""
        import uuid
        return f"CLIENT-{str(uuid.uuid4())[:8].upper()}"
    
    def add_client_interaction(self, client_id: str, interaction_type: str,
                             description: str, lawyer_id: str,
                             outcome: str = "positive", duration: float = None,
                             follow_up_required: bool = False) -> Dict[str, Any]:
        """
        Add client interaction to the CRM system.
        
        Args:
            client_id: Client identifier
            interaction_type: Type of interaction
            description: Interaction description
            lawyer_id: Lawyer identifier
            outcome: Interaction outcome
            duration: Duration in minutes (optional)
            follow_up_required: Whether follow-up is needed
            
        Returns:
            Created interaction information
        """
        try:
            # Generate interaction ID
            interaction_id = self._generate_interaction_id()
            
            # Create interaction
            interaction = ClientInteraction(
                interaction_id=interaction_id,
                client_id=client_id,
                interaction_type=interaction_type,
                description=description,
                timestamp=datetime.utcnow(),
                duration=duration,
                outcome=outcome,
                follow_up_required=follow_up_required,
                follow_up_date=datetime.utcnow() + timedelta(days=7) if follow_up_required else None,
                lawyer_id=lawyer_id
            )
            
            # Store interaction
            self.interactions.append(interaction)
            
            # Update client's last contact
            client = self._get_client(client_id)
            if client:
                client.last_contact = interaction.timestamp
            
            logger.info(f"Interaction added for client {client_id}: {interaction_type}")
            return {
                "interaction_id": interaction_id,
                "client_id": client_id,
                "interaction_type": interaction_type,
                "timestamp": interaction.timestamp.isoformat(),
                "outcome": outcome
            }
            
        except Exception as e:
            logger.error(f"Error adding client interaction: {e}")
            raise
    
    def _generate_interaction_id(self) -> str:
        """Generate unique interaction identifier."""
        import uuid
        return f"INTERACTION-{str(uuid.uuid4())[:8].upper()}" 