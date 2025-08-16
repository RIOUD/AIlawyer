#!/usr/bin/env python3
"""
AI-Powered Legal Contract Negotiation Assistant

This module implements an AI system that can analyze contracts, generate
optimized counter-proposals, and provide real-time negotiation guidance.

Features:
- Contract term analysis and fairness assessment
- AI-generated counter-proposals optimized for client interests
- Real-time negotiation assistance and strategy recommendations
- Risk assessment and mitigation strategies
- Alternative clause suggestions
"""

import json
import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
import hashlib


@dataclass
class ContractTerm:
    """Represents a contract term with analysis data."""
    term_type: str
    content: str
    fairness_score: float
    risk_level: str
    negotiation_priority: float
    alternative_suggestions: List[str]
    legal_compliance: bool


@dataclass
class NegotiationStrategy:
    """Represents a negotiation strategy with recommendations."""
    strategy_type: str
    priority_terms: List[str]
    concession_terms: List[str]
    bargaining_power: float
    risk_tolerance: str
    timeline: str
    expected_outcome: str


class LegalNegotiationAI:
    """
    AI-powered contract negotiation assistant.
    
    Provides comprehensive contract analysis, generates optimized
    counter-proposals, and offers real-time negotiation guidance.
    """
    
    def __init__(self):
        """Initialize the legal negotiation AI system."""
        self.negotiation_model = "gpt-4-legal-negotiation"
        self.strategy_database = self._load_negotiation_strategies()
        self.term_patterns = self._load_term_patterns()
        self.risk_assessment_rules = self._load_risk_assessment_rules()
        
    def _load_negotiation_strategies(self) -> Dict[str, Any]:
        """Load negotiation strategies and tactics database."""
        return {
            "collaborative": {
                "description": "Win-win approach focusing on mutual benefits",
                "tactics": ["interest-based bargaining", "creative problem solving", "relationship building"],
                "best_for": ["long-term partnerships", "complex deals", "relationship preservation"]
            },
            "competitive": {
                "description": "Aggressive approach maximizing client gains",
                "tactics": ["anchoring", "deadlines", "walk-away threats"],
                "best_for": ["one-time transactions", "power imbalances", "time pressure"]
            },
            "accommodating": {
                "description": "Concession-focused approach to close deals",
                "tactics": ["early concessions", "relationship preservation", "future consideration"],
                "best_for": ["relationship preservation", "market entry", "learning opportunities"]
            }
        }
    
    def _load_term_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for identifying contract terms."""
        return {
            "payment_terms": [
                r"payment.*within.*days",
                r"net.*\d+",
                r"due.*date",
                r"late.*fee",
                r"interest.*rate"
            ],
            "liability_terms": [
                r"limitation.*liability",
                r"indemnification",
                r"damages.*cap",
                r"exclusion.*liability",
                r"force.*majeure"
            ],
            "termination_terms": [
                r"termination.*notice",
                r"breach.*remedy",
                r"cure.*period",
                r"immediate.*termination",
                r"survival.*clause"
            ],
            "intellectual_property": [
                r"intellectual.*property",
                r"ownership.*rights",
                r"licensing.*terms",
                r"confidentiality",
                r"non-disclosure"
            ],
            "service_levels": [
                r"service.*level",
                r"uptime.*guarantee",
                r"response.*time",
                r"performance.*metrics",
                r"sla"
            ]
        }
    
    def _load_risk_assessment_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load risk assessment rules for different term types."""
        return {
            "payment_terms": {
                "high_risk": ["payment within 7 days", "late fees > 5%", "no grace period"],
                "medium_risk": ["payment within 30 days", "late fees 2-5%", "grace period < 5 days"],
                "low_risk": ["payment within 60+ days", "late fees < 2%", "grace period > 10 days"]
            },
            "liability_terms": {
                "high_risk": ["unlimited liability", "no indemnification", "no force majeure"],
                "medium_risk": ["limited liability", "mutual indemnification", "standard force majeure"],
                "low_risk": ["capped liability", "comprehensive indemnification", "broad force majeure"]
            }
        }
    
    def analyze_contract_terms(self, contract_text: str, 
                             client_priorities: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze contract terms and identify negotiation opportunities.
        
        Args:
            contract_text: Contract to analyze
            client_priorities: Client's priority weights for different terms
            
        Returns:
            Negotiation analysis with recommendations
        """
        # Extract key terms
        key_terms = self._extract_contract_terms(contract_text)
        
        # Analyze term fairness
        term_analysis = self._analyze_term_fairness(key_terms)
        
        # Generate negotiation strategy
        negotiation_strategy = self._generate_negotiation_strategy(
            key_terms, client_priorities, term_analysis
        )
        
        # Calculate bargaining power
        bargaining_power = self._calculate_bargaining_power(client_priorities, term_analysis)
        
        return {
            "term_analysis": term_analysis,
            "negotiation_strategy": negotiation_strategy,
            "risk_assessment": self._assess_negotiation_risks(key_terms),
            "alternative_clauses": self._suggest_alternative_clauses(key_terms),
            "bargaining_power": bargaining_power,
            "priority_terms": self._identify_priority_terms(key_terms, client_priorities),
            "concession_terms": self._identify_concession_terms(key_terms, client_priorities)
        }
    
    def _extract_contract_terms(self, contract_text: str) -> List[ContractTerm]:
        """Extract and categorize contract terms."""
        terms = []
        
        for term_type, patterns in self.term_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, contract_text, re.IGNORECASE)
                for match in matches:
                    term_content = match.group(0)
                    fairness_score = self._calculate_fairness_score(term_content, term_type)
                    risk_level = self._assess_term_risk(term_content, term_type)
                    
                    term = ContractTerm(
                        term_type=term_type,
                        content=term_content,
                        fairness_score=fairness_score,
                        risk_level=risk_level,
                        negotiation_priority=0.0,  # Will be calculated later
                        alternative_suggestions=[],
                        legal_compliance=True
                    )
                    terms.append(term)
        
        return terms
    
    def _calculate_fairness_score(self, term_content: str, term_type: str) -> float:
        """Calculate fairness score for a contract term."""
        # Simplified fairness calculation
        # In production, this would use more sophisticated NLP analysis
        
        fairness_indicators = {
            "mutual": 0.8,
            "both parties": 0.8,
            "reasonable": 0.7,
            "standard": 0.6,
            "industry": 0.6,
            "unilateral": 0.3,
            "exclusive": 0.3,
            "sole": 0.3
        }
        
        score = 0.5  # Default neutral score
        
        for indicator, value in fairness_indicators.items():
            if indicator in term_content.lower():
                score = value
                break
        
        return score
    
    def _assess_term_risk(self, term_content: str, term_type: str) -> str:
        """Assess risk level for a contract term."""
        if term_type in self.risk_assessment_rules:
            rules = self.risk_assessment_rules[term_type]
            
            for risk_level, risk_indicators in rules.items():
                for indicator in risk_indicators:
                    if indicator.lower() in term_content.lower():
                        return risk_level
        
        return "medium"  # Default risk level
    
    def _analyze_term_fairness(self, terms: List[ContractTerm]) -> Dict[str, Any]:
        """Analyze overall fairness of contract terms."""
        if not terms:
            return {"overall_fairness": 0.5, "risk_distribution": {}, "recommendations": []}
        
        fairness_scores = [term.fairness_score for term in terms]
        overall_fairness = sum(fairness_scores) / len(fairness_scores)
        
        risk_distribution = {}
        for term in terms:
            risk_distribution[term.risk_level] = risk_distribution.get(term.risk_level, 0) + 1
        
        recommendations = []
        if overall_fairness < 0.4:
            recommendations.append("Contract appears heavily one-sided. Consider aggressive renegotiation.")
        elif overall_fairness < 0.6:
            recommendations.append("Contract has some unfair terms. Focus on key areas for improvement.")
        else:
            recommendations.append("Contract appears reasonably balanced. Focus on optimization.")
        
        return {
            "overall_fairness": overall_fairness,
            "risk_distribution": risk_distribution,
            "recommendations": recommendations,
            "term_count": len(terms)
        }
    
    def _generate_negotiation_strategy(self, terms: List[ContractTerm],
                                     client_priorities: Dict[str, float],
                                     term_analysis: Dict[str, Any]) -> NegotiationStrategy:
        """Generate negotiation strategy based on analysis."""
        # Determine strategy type based on fairness and priorities
        overall_fairness = term_analysis["overall_fairness"]
        
        if overall_fairness < 0.4:
            strategy_type = "competitive"
        elif overall_fairness < 0.6:
            strategy_type = "collaborative"
        else:
            strategy_type = "accommodating"
        
        # Identify priority terms for negotiation
        priority_terms = self._identify_priority_terms(terms, client_priorities)
        concession_terms = self._identify_concession_terms(terms, client_priorities)
        
        # Calculate bargaining power
        bargaining_power = self._calculate_bargaining_power(client_priorities, term_analysis)
        
        return NegotiationStrategy(
            strategy_type=strategy_type,
            priority_terms=priority_terms,
            concession_terms=concession_terms,
            bargaining_power=bargaining_power,
            risk_tolerance="medium",
            timeline="standard",
            expected_outcome="improved_terms"
        )
    
    def _identify_priority_terms(self, terms: List[ContractTerm],
                               client_priorities: Dict[str, float]) -> List[str]:
        """Identify terms that should be prioritized in negotiation."""
        priority_terms = []
        
        for term in terms:
            priority_score = term.fairness_score * client_priorities.get(term.term_type, 0.5)
            if priority_score < 0.4:  # Low fairness, high priority
                priority_terms.append(term.content)
        
        return priority_terms[:5]  # Top 5 priority terms
    
    def _identify_concession_terms(self, terms: List[ContractTerm],
                                 client_priorities: Dict[str, float]) -> List[str]:
        """Identify terms that can be conceded in negotiation."""
        concession_terms = []
        
        for term in terms:
            priority_score = term.fairness_score * client_priorities.get(term.term_type, 0.5)
            if priority_score > 0.7:  # High fairness, can be conceded
                concession_terms.append(term.content)
        
        return concession_terms[:3]  # Top 3 concession terms
    
    def _calculate_bargaining_power(self, client_priorities: Dict[str, float],
                                  term_analysis: Dict[str, Any]) -> float:
        """Calculate client's bargaining power."""
        # Simplified bargaining power calculation
        # In production, this would consider market conditions, alternatives, etc.
        
        overall_fairness = term_analysis["overall_fairness"]
        priority_strength = sum(client_priorities.values()) / len(client_priorities)
        
        # Lower fairness = higher bargaining power (more room for improvement)
        bargaining_power = (1 - overall_fairness) * priority_strength
        
        return min(bargaining_power, 1.0)
    
    def _assess_negotiation_risks(self, terms: List[ContractTerm]) -> Dict[str, Any]:
        """Assess risks associated with negotiation."""
        risk_counts = {"high": 0, "medium": 0, "low": 0}
        
        for term in terms:
            risk_counts[term.risk_level] += 1
        
        total_terms = len(terms)
        risk_percentages = {
            risk: count / total_terms if total_terms > 0 else 0
            for risk, count in risk_counts.items()
        }
        
        return {
            "risk_distribution": risk_counts,
            "risk_percentages": risk_percentages,
            "overall_risk_level": max(risk_percentages, key=risk_percentages.get),
            "high_risk_terms": [term.content for term in terms if term.risk_level == "high"]
        }
    
    def _suggest_alternative_clauses(self, terms: List[ContractTerm]) -> Dict[str, List[str]]:
        """Suggest alternative clauses for problematic terms."""
        alternatives = {}
        
        for term in terms:
            if term.fairness_score < 0.5:
                alternatives[term.content] = self._generate_alternatives(term)
        
        return alternatives
    
    def _generate_alternatives(self, term: ContractTerm) -> List[str]:
        """Generate alternative clauses for a specific term."""
        alternatives = {
            "payment_terms": [
                "Payment due within 30 days of invoice date",
                "Net 45 payment terms with early payment discount",
                "Payment schedule: 50% upfront, 50% upon completion"
            ],
            "liability_terms": [
                "Mutual limitation of liability to contract value",
                "Indemnification for gross negligence only",
                "Force majeure clause with reasonable notice requirements"
            ],
            "termination_terms": [
                "30-day written notice for termination without cause",
                "Cure period of 15 days for material breaches",
                "Survival of key terms for 2 years post-termination"
            ]
        }
        
        return alternatives.get(term.term_type, ["Standard industry terms recommended"])
    
    def generate_counter_proposal(self, original_contract: str,
                                client_priorities: Dict[str, float],
                                negotiation_history: List[Dict]) -> Dict[str, Any]:
        """
        Generate AI-optimized counter-proposal.
        
        Args:
            original_contract: Original contract text
            client_priorities: Client's priorities
            negotiation_history: Previous negotiation rounds
            
        Returns:
            Optimized counter-proposal
        """
        # Analyze original contract
        analysis = self.analyze_contract_terms(original_contract, client_priorities)
        
        # Analyze negotiation history
        history_analysis = self._analyze_negotiation_history(negotiation_history)
        
        # Generate optimized counter-proposal
        counter_proposal = self._generate_optimized_proposal(
            original_contract, analysis, history_analysis
        )
        
        # Validate legal compliance
        compliance_check = self._validate_proposal_compliance(counter_proposal)
        
        return {
            "counter_proposal": counter_proposal,
            "changes_summary": self._summarize_changes(original_contract, counter_proposal),
            "justification": self._justify_changes(counter_proposal, client_priorities),
            "compliance_status": compliance_check,
            "next_steps": self._recommend_next_steps(history_analysis),
            "risk_assessment": analysis["risk_assessment"]
        }
    
    def _analyze_negotiation_history(self, negotiation_history: List[Dict]) -> Dict[str, Any]:
        """Analyze negotiation history for patterns and insights."""
        if not negotiation_history:
            return {"rounds": 0, "progress": "initial", "opponent_style": "unknown"}
        
        rounds = len(negotiation_history)
        concessions_made = sum(1 for round_data in negotiation_history 
                             if round_data.get("concessions_made", False))
        
        progress = "stalled" if rounds > 3 and concessions_made == 0 else "progressing"
        
        return {
            "rounds": rounds,
            "progress": progress,
            "concessions_made": concessions_made,
            "opponent_style": self._identify_opponent_style(negotiation_history)
        }
    
    def _identify_opponent_style(self, negotiation_history: List[Dict]) -> str:
        """Identify opponent's negotiation style."""
        if not negotiation_history:
            return "unknown"
        
        # Analyze patterns in negotiation history
        aggressive_moves = sum(1 for round_data in negotiation_history 
                             if round_data.get("aggressive", False))
        collaborative_moves = sum(1 for round_data in negotiation_history 
                                if round_data.get("collaborative", False))
        
        if aggressive_moves > collaborative_moves:
            return "competitive"
        elif collaborative_moves > aggressive_moves:
            return "collaborative"
        else:
            return "mixed"
    
    def _generate_optimized_proposal(self, original_contract: str,
                                   analysis: Dict[str, Any],
                                   history_analysis: Dict[str, Any]) -> str:
        """Generate optimized counter-proposal based on analysis."""
        # This is a simplified implementation
        # In production, this would use advanced NLP to modify the contract
        
        counter_proposal = original_contract
        
        # Apply improvements based on analysis
        for term in analysis.get("term_analysis", {}).get("recommendations", []):
            if "payment" in term.lower():
                counter_proposal = counter_proposal.replace(
                    "payment within 7 days",
                    "payment within 30 days"
                )
        
        return counter_proposal
    
    def _validate_proposal_compliance(self, proposal: str) -> Dict[str, Any]:
        """Validate legal compliance of the proposal."""
        # Simplified compliance check
        # In production, this would check against legal databases and regulations
        
        compliance_issues = []
        
        # Check for basic legal requirements
        if "governing law" not in proposal.lower():
            compliance_issues.append("Missing governing law clause")
        
        if "dispute resolution" not in proposal.lower():
            compliance_issues.append("Missing dispute resolution clause")
        
        return {
            "compliant": len(compliance_issues) == 0,
            "issues": compliance_issues,
            "recommendations": ["Add governing law clause", "Include dispute resolution mechanism"]
        }
    
    def _summarize_changes(self, original: str, proposal: str) -> List[str]:
        """Summarize changes between original and proposal."""
        # Simplified change detection
        # In production, this would use diff algorithms
        
        changes = []
        
        if "payment within 30 days" in proposal and "payment within 7 days" in original:
            changes.append("Extended payment terms from 7 to 30 days")
        
        if "mutual limitation of liability" in proposal:
            changes.append("Added mutual limitation of liability")
        
        return changes
    
    def _justify_changes(self, proposal: str, client_priorities: Dict[str, float]) -> List[str]:
        """Justify proposed changes based on client priorities."""
        justifications = []
        
        if client_priorities.get("payment_terms", 0) > 0.7:
            justifications.append("Extended payment terms align with client's cash flow priorities")
        
        if client_priorities.get("liability_terms", 0) > 0.7:
            justifications.append("Liability limitations protect client's business interests")
        
        return justifications
    
    def _recommend_next_steps(self, history_analysis: Dict[str, Any]) -> List[str]:
        """Recommend next steps in negotiation."""
        steps = []
        
        if history_analysis["rounds"] == 0:
            steps.append("Present counter-proposal with key improvements")
        elif history_analysis["progress"] == "stalled":
            steps.append("Consider alternative negotiation approaches")
        else:
            steps.append("Continue with current strategy")
        
        return steps
    
    def real_time_negotiation_assistant(self, negotiation_session: Dict) -> Dict[str, Any]:
        """
        Provide real-time negotiation assistance during live negotiations.
        
        Args:
            negotiation_session: Live negotiation session data
            
        Returns:
            Real-time negotiation guidance
        """
        # Analyze current negotiation state
        current_state = self._analyze_current_state(negotiation_session)
        
        # Generate real-time recommendations
        recommendations = self._generate_realtime_recommendations(current_state)
        
        # Predict opponent's next move
        opponent_prediction = self._predict_opponent_move(negotiation_session)
        
        return {
            "current_position": current_state,
            "recommendations": recommendations,
            "opponent_prediction": opponent_prediction,
            "risk_alerts": self._identify_risk_alerts(current_state),
            "opportunity_alerts": self._identify_opportunities(current_state)
        }
    
    def _analyze_current_state(self, session: Dict) -> Dict[str, Any]:
        """Analyze current state of negotiation session."""
        return {
            "round": session.get("round", 1),
            "concessions_made": session.get("concessions_made", 0),
            "concessions_received": session.get("concessions_received", 0),
            "current_terms": session.get("current_terms", {}),
            "deadline": session.get("deadline"),
            "pressure_level": session.get("pressure_level", "medium")
        }
    
    def _generate_realtime_recommendations(self, current_state: Dict[str, Any]) -> List[str]:
        """Generate real-time negotiation recommendations."""
        recommendations = []
        
        if current_state["concessions_made"] > current_state["concessions_received"]:
            recommendations.append("Request concessions from opponent to balance negotiation")
        
        if current_state["pressure_level"] == "high":
            recommendations.append("Consider time-sensitive concessions to close deal")
        
        return recommendations
    
    def _predict_opponent_move(self, session: Dict) -> Dict[str, Any]:
        """Predict opponent's next move based on session data."""
        # Simplified prediction logic
        # In production, this would use ML models trained on negotiation data
        
        return {
            "predicted_move": "concession",
            "confidence": 0.7,
            "reasoning": "Based on negotiation pattern analysis"
        }
    
    def _identify_risk_alerts(self, current_state: Dict[str, Any]) -> List[str]:
        """Identify potential risks in current negotiation state."""
        alerts = []
        
        if current_state["concessions_made"] > 3:
            alerts.append("High number of concessions made - risk of weak position")
        
        return alerts
    
    def _identify_opportunities(self, current_state: Dict[str, Any]) -> List[str]:
        """Identify opportunities in current negotiation state."""
        opportunities = []
        
        if current_state["concessions_received"] > current_state["concessions_made"]:
            opportunities.append("Strong position - can push for additional concessions")
        
        return opportunities


# Example usage and testing
if __name__ == "__main__":
    # Initialize negotiation AI
    negotiation_ai = LegalNegotiationAI()
    
    # Test contract analysis
    test_contract = """
    Payment terms: Payment due within 7 days of invoice date.
    Late fees: 10% per month on overdue amounts.
    Liability: Unlimited liability for all damages.
    Termination: Immediate termination for any breach.
    """
    
    client_priorities = {
        "payment_terms": 0.9,
        "liability_terms": 0.8,
        "termination_terms": 0.7
    }
    
    # Analyze contract
    analysis = negotiation_ai.analyze_contract_terms(test_contract, client_priorities)
    print("✅ Contract analysis completed")
    print(f"Overall fairness: {analysis['term_analysis']['overall_fairness']:.2f}")
    print(f"Bargaining power: {analysis['bargaining_power']:.2f}")
    
    # Generate counter-proposal
    counter_proposal = negotiation_ai.generate_counter_proposal(
        test_contract, client_priorities, []
    )
    print("✅ Counter-proposal generated")
    print(f"Changes: {counter_proposal['changes_summary']}") 