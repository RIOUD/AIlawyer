#!/usr/bin/env python3
"""
AI Legal Assistant Personality

AI system that adapts to lawyer's working style and preferences,
providing personalized assistance and recommendations.

Features:
- Personalized communication style adaptation
- Work style preference learning
- Risk tolerance assessment
- Collaborative vs independent work preferences
- Adaptive recommendations based on lawyer's profile
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class LawyerProfile:
    """Data class for lawyer personality profile."""
    lawyer_id: str
    communication_style: str  # direct_and_efficient, detailed_and_thorough, collaborative, analytical
    research_preference: str  # practical_applications, academic_depth, case_law_focused, industry_trends
    risk_tolerance: str  # conservative, moderate, aggressive
    work_style: str  # collaborative, independent, structured, flexible
    decision_making: str  # data_driven, experience_based, client_focused, precedent_oriented
    created_at: datetime
    updated_at: datetime
    confidence_score: float  # 0-1, how confident we are in the profile


@dataclass
class InteractionHistory:
    """Data class for AI interaction history."""
    interaction_id: str
    lawyer_id: str
    interaction_type: str  # recommendation, analysis, suggestion, question
    content: str
    lawyer_response: Optional[str]  # positive, negative, neutral, ignored
    timestamp: datetime
    context: Dict[str, Any]


class LegalAIPersonality:
    """
    AI legal assistant personality system.
    
    Adapts to lawyer's working style and provides personalized
    assistance and recommendations.
    """
    
    def __init__(self):
        """Initialize the AI personality system."""
        self.communication_styles = {
            "direct_and_efficient": {
                "tone": "concise and actionable",
                "format": "bullet points and summaries",
                "detail_level": "high-level with key points"
            },
            "detailed_and_thorough": {
                "tone": "comprehensive and analytical",
                "format": "detailed explanations with examples",
                "detail_level": "in-depth analysis"
            },
            "collaborative": {
                "tone": "supportive and team-oriented",
                "format": "discussion points and options",
                "detail_level": "balanced with collaboration focus"
            },
            "analytical": {
                "tone": "data-driven and logical",
                "format": "structured analysis with metrics",
                "detail_level": "evidence-based recommendations"
            }
        }
        
        self.risk_profiles = {
            "conservative": {
                "approach": "minimize risks and ensure compliance",
                "recommendations": "defensive strategies and thorough documentation",
                "threshold": "low risk tolerance"
            },
            "moderate": {
                "approach": "balanced risk-reward optimization",
                "recommendations": "standard practices with calculated risks",
                "threshold": "medium risk tolerance"
            },
            "aggressive": {
                "approach": "maximize opportunities and outcomes",
                "recommendations": "innovative strategies and competitive advantages",
                "threshold": "high risk tolerance"
            }
        }
        
        # In-memory storage (replace with database in production)
        self.lawyer_profiles = {}
        self.interaction_history = []
        
        logger.info("Legal AI Personality system initialized")
    
    def get_personalized_recommendations(self, lawyer_id: str) -> Dict[str, Any]:
        """
        Get personalized AI recommendations based on lawyer's profile.
        
        Args:
            lawyer_id: Lawyer identifier
            
        Returns:
            Personalized recommendations and insights
        """
        try:
            # Get or create lawyer profile
            profile = self._get_or_create_profile(lawyer_id)
            
            # Get recent interactions
            recent_interactions = self._get_recent_interactions(lawyer_id, days=30)
            
            # Generate personalized recommendations
            recommendations = self._generate_personalized_recommendations(profile, recent_interactions)
            
            # Generate communication suggestions
            communication_suggestions = self._generate_communication_suggestions(profile)
            
            # Generate work style insights
            work_style_insights = self._generate_work_style_insights(profile, recent_interactions)
            
            # Generate risk-based advice
            risk_advice = self._generate_risk_based_advice(profile)
            
            personalized_data = {
                "lawyer_id": lawyer_id,
                "profile": {
                    "communication_style": profile.communication_style,
                    "research_preference": profile.research_preference,
                    "risk_tolerance": profile.risk_tolerance,
                    "work_style": profile.work_style,
                    "decision_making": profile.decision_making,
                    "confidence_score": profile.confidence_score
                },
                "recommendations": recommendations,
                "communication_suggestions": communication_suggestions,
                "work_style_insights": work_style_insights,
                "risk_advice": risk_advice,
                "ai_adaptation": self._get_ai_adaptation_insights(profile),
                "interaction_summary": self._summarize_interactions(recent_interactions)
            }
            
            logger.info(f"Personalized recommendations generated for lawyer {lawyer_id}")
            return personalized_data
            
        except Exception as e:
            logger.error(f"Error getting personalized recommendations: {e}")
            raise
    
    def _get_or_create_profile(self, lawyer_id: str) -> LawyerProfile:
        """Get existing profile or create default profile."""
        if lawyer_id in self.lawyer_profiles:
            return self.lawyer_profiles[lawyer_id]
        
        # Create default profile
        profile = LawyerProfile(
            lawyer_id=lawyer_id,
            communication_style="direct_and_efficient",
            research_preference="practical_applications",
            risk_tolerance="moderate",
            work_style="collaborative",
            decision_making="experience_based",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            confidence_score=0.3  # Low confidence for new profile
        )
        
        self.lawyer_profiles[lawyer_id] = profile
        return profile
    
    def _get_recent_interactions(self, lawyer_id: str, days: int = 30) -> List[InteractionHistory]:
        """Get recent AI interactions for the lawyer."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [
            interaction for interaction in self.interaction_history
            if interaction.lawyer_id == lawyer_id and interaction.timestamp >= cutoff_date
        ]
    
    def _generate_personalized_recommendations(self, profile: LawyerProfile, 
                                             interactions: List[InteractionHistory]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations based on profile and interactions."""
        recommendations = []
        
        # Communication style-based recommendations
        if profile.communication_style == "direct_and_efficient":
            recommendations.append({
                "type": "communication",
                "title": "Optimize for Efficiency",
                "description": "Based on your preference for direct communication, I'll provide concise, actionable recommendations with clear next steps.",
                "priority": "high",
                "reasoning": "Your communication style indicates preference for efficiency"
            })
        elif profile.communication_style == "detailed_and_thorough":
            recommendations.append({
                "type": "communication",
                "title": "Comprehensive Analysis",
                "description": "I'll provide detailed analysis with multiple perspectives and thorough explanations for complex legal matters.",
                "priority": "high",
                "reasoning": "Your preference for detailed communication suggests thorough analysis is valued"
            })
        
        # Research preference-based recommendations
        if profile.research_preference == "practical_applications":
            recommendations.append({
                "type": "research",
                "title": "Focus on Practical Solutions",
                "description": "I'll prioritize practical, actionable legal solutions over theoretical analysis.",
                "priority": "medium",
                "reasoning": "Your research preference indicates practical application focus"
            })
        elif profile.research_preference == "academic_depth":
            recommendations.append({
                "type": "research",
                "title": "Academic Rigor",
                "description": "I'll provide in-depth legal analysis with academic references and theoretical frameworks.",
                "priority": "medium",
                "reasoning": "Your preference for academic depth suggests thorough theoretical understanding"
            })
        
        # Risk tolerance-based recommendations
        risk_profile = self.risk_profiles.get(profile.risk_tolerance, {})
        recommendations.append({
            "type": "strategy",
            "title": f"{profile.risk_tolerance.title()} Risk Approach",
            "description": f"I'll recommend {risk_profile.get('approach', 'balanced')} strategies aligned with your risk tolerance.",
            "priority": "high",
            "reasoning": f"Your {profile.risk_tolerance} risk profile guides strategic recommendations"
        })
        
        # Work style-based recommendations
        if profile.work_style == "collaborative":
            recommendations.append({
                "type": "workflow",
                "title": "Collaborative Approach",
                "description": "I'll suggest collaborative strategies and team-based solutions for complex cases.",
                "priority": "medium",
                "reasoning": "Your collaborative work style suggests team-oriented solutions"
            })
        elif profile.work_style == "independent":
            recommendations.append({
                "type": "workflow",
                "title": "Independent Decision Making",
                "description": "I'll provide comprehensive information for independent decision-making with minimal team dependencies.",
                "priority": "medium",
                "reasoning": "Your independent work style suggests self-sufficient approaches"
            })
        
        return recommendations
    
    def _generate_communication_suggestions(self, profile: LawyerProfile) -> List[str]:
        """Generate communication style suggestions."""
        suggestions = []
        
        style_config = self.communication_styles.get(profile.communication_style, {})
        
        suggestions.append(f"Based on your {profile.communication_style} style, I'll provide {style_config.get('tone', 'balanced')} recommendations")
        
        if profile.communication_style == "direct_and_efficient":
            suggestions.append("I'll use bullet points and executive summaries for quick decision-making")
            suggestions.append("Focus on actionable next steps rather than lengthy explanations")
        elif profile.communication_style == "detailed_and_thorough":
            suggestions.append("I'll provide comprehensive analysis with multiple perspectives")
            suggestions.append("Include detailed explanations and case law references")
        elif profile.communication_style == "collaborative":
            suggestions.append("I'll present options for discussion rather than single recommendations")
            suggestions.append("Focus on team-based solutions and stakeholder considerations")
        elif profile.communication_style == "analytical":
            suggestions.append("I'll provide data-driven analysis with metrics and evidence")
            suggestions.append("Include risk assessments and probability calculations")
        
        return suggestions
    
    def _generate_work_style_insights(self, profile: LawyerProfile, 
                                    interactions: List[InteractionHistory]) -> List[str]:
        """Generate work style insights based on profile and interactions."""
        insights = []
        
        # Analyze interaction patterns
        positive_interactions = len([i for i in interactions if i.lawyer_response == "positive"])
        total_interactions = len(interactions)
        
        if total_interactions > 0:
            satisfaction_rate = positive_interactions / total_interactions
            if satisfaction_rate > 0.8:
                insights.append("You respond well to AI recommendations - I'll continue providing proactive suggestions")
            elif satisfaction_rate < 0.5:
                insights.append("You prefer to review recommendations carefully - I'll provide more detailed reasoning")
        
        # Work style insights
        if profile.work_style == "collaborative":
            insights.append("Your collaborative approach suggests you value team input - I'll highlight opportunities for team involvement")
        elif profile.work_style == "independent":
            insights.append("Your independent work style suggests you prefer comprehensive information for self-directed decisions")
        elif profile.work_style == "structured":
            insights.append("Your structured approach suggests you value systematic processes - I'll provide step-by-step recommendations")
        elif profile.work_style == "flexible":
            insights.append("Your flexible work style suggests adaptability - I'll provide multiple options and approaches")
        
        return insights
    
    def _generate_risk_based_advice(self, profile: LawyerProfile) -> List[Dict[str, Any]]:
        """Generate risk-based advice based on lawyer's risk tolerance."""
        risk_profile = self.risk_profiles.get(profile.risk_tolerance, {})
        
        advice = [
            {
                "type": "risk_strategy",
                "title": f"{profile.risk_tolerance.title()} Risk Strategy",
                "description": risk_profile.get("approach", "Balanced approach"),
                "recommendations": risk_profile.get("recommendations", "Standard practices"),
                "threshold": risk_profile.get("threshold", "Medium risk tolerance")
            }
        ]
        
        # Add specific advice based on risk tolerance
        if profile.risk_tolerance == "conservative":
            advice.append({
                "type": "compliance",
                "title": "Compliance Focus",
                "description": "Prioritize regulatory compliance and thorough documentation",
                "recommendations": "Implement strict compliance monitoring and regular audits",
                "threshold": "Low risk tolerance"
            })
        elif profile.risk_tolerance == "aggressive":
            advice.append({
                "type": "opportunity",
                "title": "Opportunity Maximization",
                "description": "Focus on competitive advantages and innovative strategies",
                "recommendations": "Consider aggressive litigation strategies and novel legal approaches",
                "threshold": "High risk tolerance"
            })
        
        return advice
    
    def _get_ai_adaptation_insights(self, profile: LawyerProfile) -> List[str]:
        """Get insights about how AI adapts to the lawyer's preferences."""
        insights = []
        
        # Communication adaptation
        style_config = self.communication_styles.get(profile.communication_style, {})
        insights.append(f"I adapt my communication to your {profile.communication_style} style: {style_config.get('tone', 'balanced')} tone")
        
        # Research adaptation
        if profile.research_preference == "practical_applications":
            insights.append("I prioritize practical, actionable solutions over theoretical analysis")
        elif profile.research_preference == "academic_depth":
            insights.append("I provide in-depth legal analysis with academic rigor and theoretical frameworks")
        
        # Risk adaptation
        risk_profile = self.risk_profiles.get(profile.risk_tolerance, {})
        insights.append(f"I align my risk recommendations with your {profile.risk_tolerance} tolerance: {risk_profile.get('approach', 'balanced')}")
        
        # Work style adaptation
        if profile.work_style == "collaborative":
            insights.append("I suggest collaborative strategies and team-based solutions")
        elif profile.work_style == "independent":
            insights.append("I provide comprehensive information for independent decision-making")
        
        return insights
    
    def _summarize_interactions(self, interactions: List[InteractionHistory]) -> Dict[str, Any]:
        """Summarize recent AI interactions."""
        if not interactions:
            return {
                "total_interactions": 0,
                "satisfaction_rate": 0,
                "most_common_type": None,
                "recent_trend": "no_data"
            }
        
        # Calculate satisfaction rate
        positive_interactions = len([i for i in interactions if i.lawyer_response == "positive"])
        total_interactions = len(interactions)
        satisfaction_rate = (positive_interactions / total_interactions * 100) if total_interactions > 0 else 0
        
        # Find most common interaction type
        interaction_types = [i.interaction_type for i in interactions]
        most_common_type = max(set(interaction_types), key=interaction_types.count) if interaction_types else None
        
        # Analyze recent trend
        recent_interactions = [i for i in interactions if i.timestamp >= datetime.utcnow() - timedelta(days=7)]
        if recent_interactions:
            recent_positive = len([i for i in recent_interactions if i.lawyer_response == "positive"])
            recent_total = len(recent_interactions)
            recent_satisfaction = (recent_positive / recent_total * 100) if recent_total > 0 else 0
            
            if recent_satisfaction > satisfaction_rate + 10:
                recent_trend = "improving"
            elif recent_satisfaction < satisfaction_rate - 10:
                recent_trend = "declining"
            else:
                recent_trend = "stable"
        else:
            recent_trend = "no_recent_data"
        
        return {
            "total_interactions": total_interactions,
            "satisfaction_rate": round(satisfaction_rate, 1),
            "most_common_type": most_common_type,
            "recent_trend": recent_trend,
            "interaction_frequency": f"{total_interactions} interactions in last 30 days"
        }
    
    def update_profile_from_interaction(self, lawyer_id: str, interaction_type: str,
                                      content: str, lawyer_response: str, context: Dict[str, Any] = None):
        """
        Update lawyer profile based on AI interaction.
        
        Args:
            lawyer_id: Lawyer identifier
            interaction_type: Type of interaction
            content: AI content provided
            lawyer_response: Lawyer's response (positive, negative, neutral, ignored)
            context: Additional context about the interaction
        """
        try:
            # Record interaction
            interaction = InteractionHistory(
                interaction_id=self._generate_interaction_id(),
                lawyer_id=lawyer_id,
                interaction_type=interaction_type,
                content=content,
                lawyer_response=lawyer_response,
                timestamp=datetime.utcnow(),
                context=context or {}
            )
            
            self.interaction_history.append(interaction)
            
            # Update profile based on interaction
            profile = self._get_or_create_profile(lawyer_id)
            self._update_profile_from_interaction(profile, interaction)
            
            logger.info(f"Profile updated for lawyer {lawyer_id} based on interaction")
            
        except Exception as e:
            logger.error(f"Error updating profile from interaction: {e}")
            raise
    
    def _generate_interaction_id(self) -> str:
        """Generate unique interaction identifier."""
        import uuid
        return f"INTERACTION-{str(uuid.uuid4())[:8].upper()}"
    
    def _update_profile_from_interaction(self, profile: LawyerProfile, interaction: InteractionHistory):
        """Update profile based on interaction analysis."""
        # Analyze interaction content and response
        content_lower = interaction.content.lower()
        response = interaction.lawyer_response
        
        # Update communication style based on response patterns
        if response == "positive":
            # Analyze what worked well
            if "bullet" in content_lower or "summary" in content_lower:
                profile.communication_style = "direct_and_efficient"
            elif "detailed" in content_lower or "analysis" in content_lower:
                profile.communication_style = "detailed_and_thorough"
            elif "collaborative" in content_lower or "team" in content_lower:
                profile.communication_style = "collaborative"
            elif "data" in content_lower or "metrics" in content_lower:
                profile.communication_style = "analytical"
        
        # Update research preference based on content type
        if "practical" in content_lower or "actionable" in content_lower:
            profile.research_preference = "practical_applications"
        elif "academic" in content_lower or "theoretical" in content_lower:
            profile.research_preference = "academic_depth"
        elif "case law" in content_lower or "precedent" in content_lower:
            profile.research_preference = "case_law_focused"
        elif "industry" in content_lower or "trend" in content_lower:
            profile.research_preference = "industry_trends"
        
        # Update risk tolerance based on response to risk-related content
        if "risk" in content_lower or "aggressive" in content_lower:
            if response == "positive":
                profile.risk_tolerance = "aggressive"
            elif response == "negative":
                profile.risk_tolerance = "conservative"
        
        # Update work style based on collaboration mentions
        if "team" in content_lower or "collaborative" in content_lower:
            if response == "positive":
                profile.work_style = "collaborative"
            elif response == "negative":
                profile.work_style = "independent"
        
        # Update decision making preference
        if "data" in content_lower or "metrics" in content_lower:
            if response == "positive":
                profile.decision_making = "data_driven"
        elif "experience" in content_lower or "intuition" in content_lower:
            if response == "positive":
                profile.decision_making = "experience_based"
        elif "client" in content_lower:
            if response == "positive":
                profile.decision_making = "client_focused"
        elif "precedent" in content_lower or "case law" in content_lower:
            if response == "positive":
                profile.decision_making = "precedent_oriented"
        
        # Increase confidence score with more interactions
        profile.confidence_score = min(profile.confidence_score + 0.05, 1.0)
        profile.updated_at = datetime.utcnow()
    
    def get_communication_style_guide(self, lawyer_id: str) -> Dict[str, Any]:
        """
        Get personalized communication style guide for the lawyer.
        
        Args:
            lawyer_id: Lawyer identifier
            
        Returns:
            Communication style guide and preferences
        """
        try:
            profile = self._get_or_create_profile(lawyer_id)
            style_config = self.communication_styles.get(profile.communication_style, {})
            
            guide = {
                "lawyer_id": lawyer_id,
                "communication_style": profile.communication_style,
                "style_description": style_config.get("tone", "balanced"),
                "format_preferences": style_config.get("format", "standard"),
                "detail_level": style_config.get("detail_level", "balanced"),
                "recommendations": [
                    f"Use {style_config.get('tone', 'balanced')} tone in communications",
                    f"Format information as {style_config.get('format', 'standard')}",
                    f"Provide {style_config.get('detail_level', 'balanced')} level of detail"
                ],
                "examples": self._get_communication_examples(profile.communication_style)
            }
            
            return guide
            
        except Exception as e:
            logger.error(f"Error getting communication style guide: {e}")
            raise
    
    def _get_communication_examples(self, communication_style: str) -> List[str]:
        """Get communication examples for the lawyer's style."""
        examples = {
            "direct_and_efficient": [
                "• Key recommendation: File motion for summary judgment",
                "• Next steps: 1) Review documents, 2) Prepare filing, 3) Submit by Friday",
                "• Risk level: Low (25% probability of opposition)"
            ],
            "detailed_and_thorough": [
                "Comprehensive Analysis: The motion for summary judgment presents a strong case based on three key factors: 1) Clear contractual language, 2) Absence of material facts in dispute, and 3) Favorable precedent in similar cases.",
                "Detailed Recommendation: Proceed with filing, but include additional evidence to strengthen the position.",
                "Risk Assessment: While the probability of success is high (75%), potential opposition arguments include..."
            ],
            "collaborative": [
                "Team Discussion Points: Let's review the motion strategy together and consider input from the paralegal team.",
                "Collaborative Options: We could either file immediately or schedule a team review session first.",
                "Stakeholder Considerations: How does this align with the client's preferences and team workload?"
            ],
            "analytical": [
                "Data Analysis: Success rate for similar motions: 78% (based on 45 cases)",
                "Metrics: Estimated time savings: 3-4 months, Cost reduction: €15,000-€20,000",
                "Probability Assessment: 75% chance of success, 15% chance of partial success, 10% chance of denial"
            ]
        }
        
        return examples.get(communication_style, ["Standard communication format"]) 