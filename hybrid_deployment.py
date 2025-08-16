#!/usr/bin/env python3
"""
Hybrid Deployment Architecture for LawyerAgent

This module implements a hybrid deployment model that allows both local and cloud
deployment options while maintaining security advantages for sensitive cases.

Features:
- Local-only deployment (current functionality)
- Hybrid deployment (sensitive data local, non-sensitive cloud)
- Cloud-only deployment (enterprise with enhanced security)
- Secure synchronization between deployment modes
- Tier-based security configurations
"""

import os
import sys
import asyncio
import ssl
import certifi
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
import json
import hashlib
import secrets

# Import existing components
from security_manager import SecurityManager
from quantum_encryption import QuantumResistantEncryption
from database import LegalAssistantDB


class DeploymentMode(Enum):
    """Deployment modes for the hybrid architecture."""
    LOCAL_ONLY = "local_only"
    HYBRID_CLOUD = "hybrid_cloud"
    CLOUD_ONLY = "cloud_only"


@dataclass
class SecurityContext:
    """Security context for different deployment modes."""
    encryption_level: str  # "local_aes256", "hybrid_quantum", "cloud_enterprise"
    data_residency: str    # "local_only", "hybrid_split", "cloud_managed"
    audit_requirements: List[str]
    compliance_frameworks: List[str]
    session_timeout: int
    max_failed_attempts: int
    lockout_duration: int


class ChromaDBManager:
    """Manages local ChromaDB vector store operations."""
    
    def __init__(self, local_path: str = "./chroma_db"):
        self.local_path = local_path
        self.embeddings = None
        self.vector_store = None
    
    def initialize(self, embeddings_model: str = "all-MiniLM-L6-v2"):
        """Initialize ChromaDB with embeddings model."""
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma
            
            self.embeddings = HuggingFaceEmbeddings(
                model_name=embeddings_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            if os.path.exists(self.local_path):
                self.vector_store = Chroma(
                    persist_directory=self.local_path,
                    embedding_function=self.embeddings
                )
            else:
                self.vector_store = Chroma(
                    persist_directory=self.local_path,
                    embedding_function=self.embeddings
                )
            
            return True
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            return False
    
    def search_documents(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search documents in the vector store."""
        if not self.vector_store:
            return []
        
        try:
            results = self.vector_store.similarity_search_with_relevance_scores(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                }
                for doc, score in results
            ]
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []


class OllamaManager:
    """Manages local Ollama LLM operations."""
    
    def __init__(self, model_name: str = "mixtral", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.llm = None
    
    def initialize(self):
        """Initialize Ollama LLM."""
        try:
            from langchain_ollama import Ollama
            
            self.llm = Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.1
            )
            return True
        except Exception as e:
            print(f"Error initializing Ollama: {e}")
            return False
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using the LLM."""
        if not self.llm:
            return "LLM not initialized"
        
        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            return f"Error generating response: {e}"


class LocalAuditLogger:
    """Manages local audit logging."""
    
    def __init__(self, log_file: str = "hybrid_audit.log"):
        self.log_file = log_file
        self.ensure_log_directory()
    
    def ensure_log_directory(self):
        """Ensure log directory exists."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log_event(self, event_type: str, user_id: Optional[str] = None,
                  document_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log an audit event."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "document_id": document_id,
            "details": details or {},
            "deployment_mode": "local"
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"Error logging audit event: {e}")


class CloudAPIGateway:
    """Manages cloud API gateway operations."""
    
    def __init__(self, api_endpoint: Optional[str] = None):
        self.api_endpoint = api_endpoint or os.getenv("CLOUD_API_ENDPOINT")
        self.api_key = os.getenv("CLOUD_API_KEY")
        self.session = None
    
    async def initialize(self):
        """Initialize cloud API gateway."""
        if not self.api_endpoint or not self.api_key:
            print("Cloud API credentials not configured")
            return False
        
        try:
            import aiohttp
            
            # Configure SSL context
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(
                connector=connector,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
            return True
        except Exception as e:
            print(f"Error initializing cloud API gateway: {e}")
            return False
    
    async def health_check(self) -> bool:
        """Check cloud API health."""
        if not self.session:
            return False
        
        try:
            async with self.session.get(f"{self.api_endpoint}/health") as response:
                return response.status == 200
        except Exception:
            return False


class SecureDocumentSync:
    """Manages secure document synchronization."""
    
    def __init__(self, api_gateway: CloudAPIGateway):
        self.api_gateway = api_gateway
    
    async def sync_metadata(self, document_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sync document metadata to cloud."""
        if not self.api_gateway.session:
            return {"error": "API gateway not initialized"}
        
        try:
            payload = {
                "document_id": document_id,
                "metadata": metadata,
                "sync_type": "metadata_only",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            async with self.api_gateway.session.post(
                f"{self.api_gateway.api_endpoint}/sync/metadata",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Sync failed with status {response.status}"}
        except Exception as e:
            return {"error": f"Sync error: {str(e)}"}
    
    async def sync_full_document(self, document_id: str, 
                                encrypted_payload: bytes) -> Dict[str, Any]:
        """Sync full encrypted document to cloud."""
        if not self.api_gateway.session:
            return {"error": "API gateway not initialized"}
        
        try:
            payload = {
                "document_id": document_id,
                "encrypted_content": encrypted_payload.hex(),
                "sync_type": "full_document",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            async with self.api_gateway.session.post(
                f"{self.api_gateway.api_endpoint}/sync/document",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Sync failed with status {response.status}"}
        except Exception as e:
            return {"error": f"Sync error: {str(e)}"}


class CollaborationManager:
    """Manages collaboration features for hybrid deployment."""
    
    def __init__(self, api_gateway: CloudAPIGateway):
        self.api_gateway = api_gateway
    
    async def create_shared_workspace(self, workspace_name: str, 
                                    owner_id: str) -> Dict[str, Any]:
        """Create a shared workspace for collaboration."""
        if not self.api_gateway.session:
            return {"error": "API gateway not initialized"}
        
        try:
            payload = {
                "workspace_name": workspace_name,
                "owner_id": owner_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            async with self.api_gateway.session.post(
                f"{self.api_gateway.api_endpoint}/workspace/create",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Workspace creation failed with status {response.status}"}
        except Exception as e:
            return {"error": f"Workspace creation error: {str(e)}"}


class EncryptedBackupManager:
    """Manages encrypted backup operations."""
    
    def __init__(self, api_gateway: CloudAPIGateway):
        self.api_gateway = api_gateway
    
    async def create_backup(self, backup_data: bytes, 
                           backup_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create encrypted backup in cloud."""
        if not self.api_gateway.session:
            return {"error": "API gateway not initialized"}
        
        try:
            payload = {
                "encrypted_backup": backup_data.hex(),
                "metadata": backup_metadata,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            async with self.api_gateway.session.post(
                f"{self.api_gateway.api_endpoint}/backup/create",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Backup creation failed with status {response.status}"}
        except Exception as e:
            return {"error": f"Backup creation error: {str(e)}"}


class PrivacyPreservingAnalytics:
    """Manages privacy-preserving analytics."""
    
    def __init__(self, api_gateway: CloudAPIGateway):
        self.api_gateway = api_gateway
    
    async def send_analytics(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send privacy-preserving analytics to cloud."""
        if not self.api_gateway.session:
            return {"error": "API gateway not initialized"}
        
        try:
            # Anonymize sensitive data
            anonymized_data = self._anonymize_data(analytics_data)
            
            payload = {
                "analytics": anonymized_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            async with self.api_gateway.session.post(
                f"{self.api_gateway.api_endpoint}/analytics/send",
                json=payload
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Analytics send failed with status {response.status}"}
        except Exception as e:
            return {"error": f"Analytics send error: {str(e)}"}
    
    def _anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize sensitive data for analytics."""
        anonymized = {}
        
        for key, value in data.items():
            if key in ["user_id", "document_id", "client_name"]:
                # Hash sensitive identifiers
                anonymized[key] = hashlib.sha256(str(value).encode()).hexdigest()[:16]
            elif key in ["query_content", "document_content"]:
                # Skip content data entirely
                continue
            else:
                # Keep non-sensitive data
                anonymized[key] = value
        
        return anonymized


class HybridDeploymentManager:
    """
    Manages hybrid deployment with security-first architecture.
    
    Supports:
    - Local-only deployment (current functionality)
    - Hybrid deployment (sensitive data local, non-sensitive cloud)
    - Cloud-only deployment (enterprise with enhanced security)
    """
    
    def __init__(self, deployment_mode: DeploymentMode, 
                 security_context: SecurityContext):
        self.deployment_mode = deployment_mode
        self.security_context = security_context
        self.local_components = {}
        self.cloud_components = {}
        self.sync_manager = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the hybrid deployment manager."""
        try:
            # Initialize local components
            self.local_components = await self._initialize_local_components()
            
            # Initialize cloud components if needed
            if self.deployment_mode != DeploymentMode.LOCAL_ONLY:
                self.cloud_components = await self._initialize_cloud_components()
            
            # Initialize sync manager for hybrid mode
            if self.deployment_mode == DeploymentMode.HYBRID_CLOUD:
                self.sync_manager = await self._initialize_sync_manager()
            
            self.initialized = True
            print(f"✅ Hybrid deployment manager initialized in {self.deployment_mode.value} mode")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing hybrid deployment manager: {e}")
            return False
    
    async def _initialize_local_components(self) -> Dict[str, Any]:
        """Initialize local-only components."""
        components = {}
        
        # Initialize vector store
        components["vector_store"] = ChromaDBManager(local_path="./chroma_db")
        if not components["vector_store"].initialize():
            raise Exception("Failed to initialize vector store")
        
        # Initialize LLM
        components["llm"] = OllamaManager(model_name="mixtral")
        if not components["llm"].initialize():
            raise Exception("Failed to initialize LLM")
        
        # Initialize security components
        components["security"] = SecurityManager()
        components["encryption"] = QuantumResistantEncryption()
        components["audit_log"] = LocalAuditLogger()
        
        return components
    
    async def _initialize_cloud_components(self) -> Dict[str, Any]:
        """Initialize cloud components for hybrid deployment."""
        components = {}
        
        # Initialize API gateway
        components["api_gateway"] = CloudAPIGateway()
        if not await components["api_gateway"].initialize():
            print("⚠️ Cloud API gateway initialization failed - continuing in local mode")
            return {}
        
        # Initialize cloud services
        components["document_sync"] = SecureDocumentSync(components["api_gateway"])
        components["collaboration"] = CollaborationManager(components["api_gateway"])
        components["backup"] = EncryptedBackupManager(components["api_gateway"])
        components["analytics"] = PrivacyPreservingAnalytics(components["api_gateway"])
        
        return components
    
    async def _initialize_sync_manager(self) -> Optional['SecureSyncManager']:
        """Initialize secure synchronization manager for hybrid mode."""
        if self.deployment_mode == DeploymentMode.HYBRID_CLOUD:
            from secure_sync_manager import SecureSyncManager
            return SecureSyncManager(
                local_components=self.local_components,
                cloud_components=self.cloud_components,
                security_context=self.security_context
            )
        return None
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get current deployment information."""
        return {
            "deployment_mode": self.deployment_mode.value,
            "security_context": {
                "encryption_level": self.security_context.encryption_level,
                "data_residency": self.security_context.data_residency,
                "compliance_frameworks": self.security_context.compliance_frameworks
            },
            "components_initialized": {
                "local": bool(self.local_components),
                "cloud": bool(self.cloud_components),
                "sync_manager": bool(self.sync_manager)
            },
            "initialized": self.initialized
        }
    
    async def process_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a legal query using the appropriate deployment mode."""
        if not self.initialized:
            return {"error": "Deployment manager not initialized"}
        
        try:
            # Log query event
            self.local_components["audit_log"].log_event(
                "query_processed", user_id, None, {"query": query[:100]}
            )
            
            # Search documents
            search_results = self.local_components["vector_store"].search_documents(query)
            
            # Generate response
            if search_results:
                context = "\n\n".join([result["content"] for result in search_results])
                prompt = f"Based on the following legal documents, answer this question: {query}\n\nDocuments:\n{context}"
                response = self.local_components["llm"].generate_response(prompt)
            else:
                response = "I couldn't find relevant documents to answer your question."
            
            # Sync to cloud if in hybrid mode
            if self.sync_manager and self.cloud_components:
                await self.sync_manager.sync_query_metadata(query, response, user_id)
            
            return {
                "response": response,
                "sources": search_results,
                "deployment_mode": self.deployment_mode.value
            }
            
        except Exception as e:
            self.local_components["audit_log"].log_event(
                "query_error", user_id, None, {"error": str(e)}
            )
            return {"error": f"Query processing error: {str(e)}"}


# Example usage and testing
async def test_hybrid_deployment():
    """Test the hybrid deployment manager."""
    print("🧪 Testing Hybrid Deployment Manager")
    
    # Test local-only deployment
    print("\n1. Testing Local-Only Deployment")
    local_security = SecurityContext(
        encryption_level="local_aes256",
        data_residency="local_only",
        audit_requirements=["basic_logging"],
        compliance_frameworks=["gdpr"],
        session_timeout=1800,
        max_failed_attempts=5,
        lockout_duration=1800
    )
    
    local_manager = HybridDeploymentManager(DeploymentMode.LOCAL_ONLY, local_security)
    await local_manager.initialize()
    
    print("Local deployment info:", local_manager.get_deployment_info())
    
    # Test query processing
    result = await local_manager.process_query("What are the requirements for employment contracts?")
    print("Query result:", result.get("response", "No response")[:200] + "...")
    
    print("\n✅ Hybrid deployment test completed")


if __name__ == "__main__":
    asyncio.run(test_hybrid_deployment()) 