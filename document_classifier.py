#!/usr/bin/env python3
"""
Document Classification System for Hybrid Deployment

This module implements intelligent document classification that determines
the appropriate deployment strategy for each document based on sensitivity
analysis, client preferences, and regulatory requirements.

Features:
- Sensitivity scoring based on content analysis
- Client preference integration
- Regulatory requirement checking
- Deployment strategy recommendations
- Secure classification storage
"""

import re
import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import sqlite3
import os


class SensitivityLevel(Enum):
    """Document sensitivity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeploymentStrategy(Enum):
    """Deployment strategies for documents."""
    LOCAL_ONLY = "local_only"
    HYBRID = "hybrid"
    CLOUD_ELIGIBLE = "cloud_eligible"


@dataclass
class ClassificationResult:
    """Result of document classification."""
    document_id: str
    sensitivity_score: float
    sensitivity_level: SensitivityLevel
    deployment_strategy: DeploymentStrategy
    encryption_requirements: List[str]
    audit_requirements: List[str]
    sync_strategy: str
    classification_reason: str
    timestamp: datetime
    confidence_score: float


class DocumentClassifier:
    """
    Classifies documents for appropriate deployment handling.
    
    Determines whether documents should be:
    - Local-only (highly sensitive)
    - Hybrid (moderate sensitivity)
    - Cloud-eligible (low sensitivity)
    """
    
    def __init__(self, db_path: str = "classification.db"):
        self.db_path = db_path
        self.sensitivity_patterns = self._load_sensitivity_patterns()
        self.client_preferences = self._load_client_preferences()
        self.regulatory_requirements = self._load_regulatory_requirements()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize classification database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS document_classifications (
                        document_id TEXT PRIMARY KEY,
                        document_hash TEXT NOT NULL,
                        sensitivity_score REAL NOT NULL,
                        sensitivity_level TEXT NOT NULL,
                        deployment_strategy TEXT NOT NULL,
                        encryption_requirements TEXT NOT NULL,
                        audit_requirements TEXT NOT NULL,
                        sync_strategy TEXT NOT NULL,
                        classification_reason TEXT NOT NULL,
                        confidence_score REAL NOT NULL,
                        classified_at TEXT NOT NULL,
                        client_id TEXT,
                        practice_area TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sensitivity_level 
                    ON document_classifications(sensitivity_level)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_deployment_strategy 
                    ON document_classifications(deployment_strategy)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_client_id 
                    ON document_classifications(client_id)
                """)
        except Exception as e:
            print(f"Error initializing classification database: {e}")
    
    def _load_sensitivity_patterns(self) -> Dict[str, List[str]]:
        """Load sensitivity patterns for different document types."""
        return {
            "high_sensitivity_keywords": [
                "confidential", "privileged", "attorney-client", "trade secret",
                "personal data", "financial information", "medical records",
                "confidentiel", "privilégié", "secret commercial", "données personnelles",
                "informations financières", "dossiers médicaux", "geheimhouding",
                "vertrouwelijk", "persoonlijke gegevens", "financiële informatie"
            ],
            "medium_sensitivity_keywords": [
                "internal", "proprietary", "business plan", "strategy",
                "interne", "propriétaire", "plan d'affaires", "stratégie",
                "intern", "eigendom", "businessplan", "strategie"
            ],
            "client_identifiers": [
                r'\b[A-Z]{2,3}\d{6,8}\b',  # Client codes
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN patterns
                r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',  # Email addresses
                r'\b\d{10,11}\b',  # Phone numbers
                r'\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b'  # IBAN patterns
            ],
            "legal_sensitive_terms": [
                "litigation", "lawsuit", "settlement", "mediation",
                "litige", "procès", "règlement", "médiation",
                "rechtszaak", "proces", "schikking", "bemiddeling"
            ]
        }
    
    def _load_client_preferences(self) -> Dict[str, Dict[str, Any]]:
        """Load client preferences for data handling."""
        # In production, this would be loaded from a secure database
        return {
            "default": {
                "local_only": False,
                "hybrid_allowed": True,
                "cloud_allowed": True,
                "encryption_required": True,
                "audit_required": True
            },
            "high_security_clients": {
                "local_only": True,
                "hybrid_allowed": False,
                "cloud_allowed": False,
                "encryption_required": True,
                "audit_required": True
            },
            "financial_clients": {
                "local_only": False,
                "hybrid_allowed": True,
                "cloud_allowed": False,
                "encryption_required": True,
                "audit_required": True
            }
        }
    
    def _load_regulatory_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load regulatory requirements for different jurisdictions."""
        return {
            "gdpr": {
                "personal_data_local_only": True,
                "encryption_required": True,
                "audit_trail_required": True,
                "data_residency": "eu_only"
            },
            "sox": {
                "financial_data_local_only": False,
                "encryption_required": True,
                "audit_trail_required": True,
                "retention_period": 7  # years
            },
            "hipaa": {
                "health_data_local_only": True,
                "encryption_required": True,
                "audit_trail_required": True,
                "access_controls": True
            },
            "belgian_privacy": {
                "personal_data_local_only": True,
                "encryption_required": True,
                "audit_trail_required": True,
                "data_residency": "belgium_only"
            }
        }
    
    def classify_document(self, document_content: str, 
                         metadata: Dict[str, Any]) -> ClassificationResult:
        """
        Classify document for deployment strategy.
        
        Args:
            document_content: Document text content
            metadata: Document metadata including client_id, practice_area, etc.
            
        Returns:
            Classification result with deployment recommendations
        """
        # Generate document ID and hash
        document_hash = hashlib.sha256(document_content.encode()).hexdigest()
        document_id = metadata.get("document_id") or f"doc_{document_hash[:16]}"
        
        # Analyze document content for sensitivity indicators
        sensitivity_score = self._calculate_sensitivity_score(document_content)
        sensitivity_level = self._determine_sensitivity_level(sensitivity_score)
        
        # Check client preferences
        client_requirements = self._check_client_requirements(metadata.get("client_id"))
        
        # Check regulatory requirements
        regulatory_requirements = self._check_regulatory_requirements(metadata)
        
        # Determine deployment strategy
        deployment_strategy = self._determine_deployment_strategy(
            sensitivity_score, client_requirements, regulatory_requirements
        )
        
        # Get requirements based on strategy
        encryption_requirements = self._get_encryption_requirements(deployment_strategy)
        audit_requirements = self._get_audit_requirements(deployment_strategy)
        sync_strategy = self._get_sync_strategy(deployment_strategy)
        
        # Generate classification reason
        classification_reason = self._generate_classification_reason(
            sensitivity_score, client_requirements, regulatory_requirements
        )
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            sensitivity_score, client_requirements, regulatory_requirements
        )
        
        # Create classification result
        result = ClassificationResult(
            document_id=document_id,
            sensitivity_score=sensitivity_score,
            sensitivity_level=sensitivity_level,
            deployment_strategy=deployment_strategy,
            encryption_requirements=encryption_requirements,
            audit_requirements=audit_requirements,
            sync_strategy=sync_strategy,
            classification_reason=classification_reason,
            timestamp=datetime.now(timezone.utc),
            confidence_score=confidence_score
        )
        
        # Store classification result
        self._store_classification_result(result, metadata)
        
        return result
    
    def _calculate_sensitivity_score(self, content: str) -> float:
        """Calculate document sensitivity score (0.0 to 1.0)."""
        score = 0.0
        content_lower = content.lower()
        
        # Check for high-sensitivity keywords
        high_sensitivity_keywords = self.sensitivity_patterns["high_sensitivity_keywords"]
        for keyword in high_sensitivity_keywords:
            if keyword.lower() in content_lower:
                score += 0.15
        
        # Check for medium-sensitivity keywords
        medium_sensitivity_keywords = self.sensitivity_patterns["medium_sensitivity_keywords"]
        for keyword in medium_sensitivity_keywords:
            if keyword.lower() in content_lower:
                score += 0.08
        
        # Check for client identifiers
        client_patterns = self.sensitivity_patterns["client_identifiers"]
        for pattern in client_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                score += 0.1 * len(matches)
        
        # Check for legal sensitive terms
        legal_terms = self.sensitivity_patterns["legal_sensitive_terms"]
        for term in legal_terms:
            if term.lower() in content_lower:
                score += 0.05
        
        # Check document length (longer documents may contain more sensitive info)
        if len(content) > 10000:
            score += 0.05
        
        # Check for specific document types
        if any(doc_type in content_lower for doc_type in ["contract", "agreement", "contract", "accord"]):
            score += 0.1
        
        return min(score, 1.0)
    
    def _determine_sensitivity_level(self, sensitivity_score: float) -> SensitivityLevel:
        """Determine sensitivity level based on score."""
        if sensitivity_score >= 0.8:
            return SensitivityLevel.CRITICAL
        elif sensitivity_score >= 0.6:
            return SensitivityLevel.HIGH
        elif sensitivity_score >= 0.3:
            return SensitivityLevel.MEDIUM
        else:
            return SensitivityLevel.LOW
    
    def _check_client_requirements(self, client_id: Optional[str]) -> Dict[str, Any]:
        """Check client-specific requirements."""
        if not client_id:
            return self.client_preferences["default"]
        
        # In production, this would query a client database
        if client_id in self.client_preferences:
            return self.client_preferences[client_id]
        
        return self.client_preferences["default"]
    
    def _check_regulatory_requirements(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Check regulatory requirements based on metadata."""
        requirements = {}
        
        # Check jurisdiction
        jurisdiction = metadata.get("jurisdiction", "").lower()
        if "eu" in jurisdiction or "belgian" in jurisdiction:
            requirements.update(self.regulatory_requirements["gdpr"])
            requirements.update(self.regulatory_requirements["belgian_privacy"])
        
        # Check practice area
        practice_area = metadata.get("practice_area", "").lower()
        if "financial" in practice_area or "banking" in practice_area:
            requirements.update(self.regulatory_requirements["sox"])
        
        if "healthcare" in practice_area or "medical" in practice_area:
            requirements.update(self.regulatory_requirements["hipaa"])
        
        return requirements
    
    def _determine_deployment_strategy(self, sensitivity_score: float,
                                     client_requirements: Dict[str, Any],
                                     regulatory_requirements: Dict[str, Any]) -> DeploymentStrategy:
        """Determine deployment strategy based on analysis."""
        # Client preferences override
        if client_requirements.get("local_only", False):
            return DeploymentStrategy.LOCAL_ONLY
        
        # Regulatory requirements
        if regulatory_requirements.get("personal_data_local_only", False):
            return DeploymentStrategy.LOCAL_ONLY
        
        # Sensitivity-based decision
        if sensitivity_score > 0.7:
            return DeploymentStrategy.LOCAL_ONLY
        elif sensitivity_score > 0.4:
            return DeploymentStrategy.HYBRID
        else:
            return DeploymentStrategy.CLOUD_ELIGIBLE
    
    def _get_encryption_requirements(self, deployment_strategy: DeploymentStrategy) -> List[str]:
        """Get encryption requirements for deployment strategy."""
        if deployment_strategy == DeploymentStrategy.LOCAL_ONLY:
            return ["AES-256-GCM", "quantum_resistant"]
        elif deployment_strategy == DeploymentStrategy.HYBRID:
            return ["AES-256-GCM", "quantum_resistant", "hybrid_key_management"]
        else:
            return ["AES-256-GCM", "enterprise_encryption"]
    
    def _get_audit_requirements(self, deployment_strategy: DeploymentStrategy) -> List[str]:
        """Get audit requirements for deployment strategy."""
        if deployment_strategy == DeploymentStrategy.LOCAL_ONLY:
            return ["local_audit_logging", "secure_deletion"]
        elif deployment_strategy == DeploymentStrategy.HYBRID:
            return ["local_audit_logging", "cloud_audit_logging", "sync_audit_trail"]
        else:
            return ["enterprise_audit_logging", "compliance_reporting"]
    
    def _get_sync_strategy(self, deployment_strategy: DeploymentStrategy) -> str:
        """Get synchronization strategy for deployment strategy."""
        if deployment_strategy == DeploymentStrategy.LOCAL_ONLY:
            return "no_sync"
        elif deployment_strategy == DeploymentStrategy.HYBRID:
            return "metadata_sync"
        else:
            return "full_sync"
    
    def _generate_classification_reason(self, sensitivity_score: float,
                                      client_requirements: Dict[str, Any],
                                      regulatory_requirements: Dict[str, Any]) -> str:
        """Generate human-readable classification reason."""
        reasons = []
        
        if sensitivity_score > 0.7:
            reasons.append(f"High sensitivity score ({sensitivity_score:.2f})")
        
        if client_requirements.get("local_only", False):
            reasons.append("Client requires local-only storage")
        
        if regulatory_requirements.get("personal_data_local_only", False):
            reasons.append("Regulatory requirement for local storage")
        
        if not reasons:
            reasons.append("Standard classification based on sensitivity analysis")
        
        return "; ".join(reasons)
    
    def _calculate_confidence_score(self, sensitivity_score: float,
                                  client_requirements: Dict[str, Any],
                                  regulatory_requirements: Dict[str, Any]) -> float:
        """Calculate confidence score for classification."""
        confidence = 0.8  # Base confidence
        
        # Higher confidence for clear client requirements
        if client_requirements.get("local_only", False):
            confidence += 0.15
        
        # Higher confidence for clear regulatory requirements
        if regulatory_requirements:
            confidence += 0.1
        
        # Higher confidence for extreme sensitivity scores
        if sensitivity_score > 0.8 or sensitivity_score < 0.2:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _store_classification_result(self, result: ClassificationResult, 
                                   metadata: Dict[str, Any]):
        """Store classification result in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO document_classifications 
                    (document_id, document_hash, sensitivity_score, sensitivity_level,
                     deployment_strategy, encryption_requirements, audit_requirements,
                     sync_strategy, classification_reason, confidence_score,
                     classified_at, client_id, practice_area)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.document_id,
                    hashlib.sha256(str(result).encode()).hexdigest(),
                    result.sensitivity_score,
                    result.sensitivity_level.value,
                    result.deployment_strategy.value,
                    json.dumps(result.encryption_requirements),
                    json.dumps(result.audit_requirements),
                    result.sync_strategy,
                    result.classification_reason,
                    result.confidence_score,
                    result.timestamp.isoformat(),
                    metadata.get("client_id"),
                    metadata.get("practice_area")
                ))
        except Exception as e:
            print(f"Error storing classification result: {e}")
    
    def get_classification_history(self, document_id: str) -> Optional[ClassificationResult]:
        """Get classification history for a document."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM document_classifications 
                    WHERE document_id = ?
                """, (document_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_classification_result(row)
                return None
        except Exception as e:
            print(f"Error retrieving classification history: {e}")
            return None
    
    def _row_to_classification_result(self, row: Tuple) -> ClassificationResult:
        """Convert database row to ClassificationResult."""
        return ClassificationResult(
            document_id=row[0],
            sensitivity_score=row[2],
            sensitivity_level=SensitivityLevel(row[3]),
            deployment_strategy=DeploymentStrategy(row[4]),
            encryption_requirements=json.loads(row[5]),
            audit_requirements=json.loads(row[6]),
            sync_strategy=row[7],
            classification_reason=row[8],
            confidence_score=row[9],
            timestamp=datetime.fromisoformat(row[10])
        )
    
    def get_classification_statistics(self) -> Dict[str, Any]:
        """Get classification statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Count by sensitivity level
                sensitivity_counts = {}
                for level in SensitivityLevel:
                    cursor = conn.execute("""
                        SELECT COUNT(*) FROM document_classifications 
                        WHERE sensitivity_level = ?
                    """, (level.value,))
                    sensitivity_counts[level.value] = cursor.fetchone()[0]
                
                # Count by deployment strategy
                strategy_counts = {}
                for strategy in DeploymentStrategy:
                    cursor = conn.execute("""
                        SELECT COUNT(*) FROM document_classifications 
                        WHERE deployment_strategy = ?
                    """, (strategy.value,))
                    strategy_counts[strategy.value] = cursor.fetchone()[0]
                
                # Average confidence score
                cursor = conn.execute("""
                    SELECT AVG(confidence_score) FROM document_classifications
                """)
                avg_confidence = cursor.fetchone()[0] or 0.0
                
                return {
                    "total_documents": sum(sensitivity_counts.values()),
                    "sensitivity_distribution": sensitivity_counts,
                    "deployment_strategy_distribution": strategy_counts,
                    "average_confidence_score": avg_confidence
                }
        except Exception as e:
            print(f"Error retrieving classification statistics: {e}")
            return {}


# Example usage and testing
def test_document_classifier():
    """Test the document classifier."""
    print("🧪 Testing Document Classifier")
    
    classifier = DocumentClassifier()
    
    # Test high-sensitivity document
    high_sensitivity_content = """
    CONFIDENTIAL ATTORNEY-CLIENT COMMUNICATION
    
    This document contains privileged information regarding client ABC123456.
    The client's personal data includes: john.doe@example.com and SSN: 123-45-6789.
    
    This is a confidential settlement agreement that must remain secure.
    """
    
    high_sensitivity_metadata = {
        "client_id": "high_security_clients",
        "practice_area": "litigation",
        "jurisdiction": "belgian"
    }
    
    result = classifier.classify_document(high_sensitivity_content, high_sensitivity_metadata)
    print(f"\nHigh sensitivity document:")
    print(f"Sensitivity Score: {result.sensitivity_score:.2f}")
    print(f"Sensitivity Level: {result.sensitivity_level.value}")
    print(f"Deployment Strategy: {result.deployment_strategy.value}")
    print(f"Classification Reason: {result.classification_reason}")
    
    # Test low-sensitivity document
    low_sensitivity_content = """
    General legal research document about employment law.
    This document contains public information about Belgian employment regulations.
    No confidential or personal information is included.
    """
    
    low_sensitivity_metadata = {
        "client_id": "default",
        "practice_area": "employment_law",
        "jurisdiction": "belgian"
    }
    
    result = classifier.classify_document(low_sensitivity_content, low_sensitivity_metadata)
    print(f"\nLow sensitivity document:")
    print(f"Sensitivity Score: {result.sensitivity_score:.2f}")
    print(f"Sensitivity Level: {result.sensitivity_level.value}")
    print(f"Deployment Strategy: {result.deployment_strategy.value}")
    print(f"Classification Reason: {result.classification_reason}")
    
    # Get statistics
    stats = classifier.get_classification_statistics()
    print(f"\nClassification Statistics:")
    print(f"Total Documents: {stats.get('total_documents', 0)}")
    print(f"Sensitivity Distribution: {stats.get('sensitivity_distribution', {})}")
    print(f"Deployment Strategy Distribution: {stats.get('deployment_strategy_distribution', {})}")
    
    print("\n✅ Document classifier test completed")


if __name__ == "__main__":
    test_document_classifier() 