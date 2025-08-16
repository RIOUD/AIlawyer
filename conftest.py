#!/usr/bin/env python3
"""
Shared test configuration and fixtures for Legal Assistant AI Platform

This file provides common fixtures and configuration for all test modules.
"""

import pytest
import tempfile
import os
import shutil
import json
from pathlib import Path
from typing import Dict, Any, List


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="session")
def sample_documents(test_data_dir):
    """Create sample documents for testing."""
    documents = {
        "contract.txt": "Sample employment contract content",
        "law.txt": "Sample legal document content",
        "case.txt": "Sample case law content",
        "employment_agreement.pdf": "Employment agreement PDF content",
        "legal_opinion.docx": "Legal opinion document content"
    }
    
    for filename, content in documents.items():
        filepath = os.path.join(test_data_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
    
    yield documents


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "vector_store_path": "./test_chroma_db",
        "embedding_model": "all-MiniLM-L6-v2",
        "ollama_model": "mixtral",
        "ollama_base_url": "http://localhost:11434",
        "max_retrieval_docs": 4,
        "security_enabled": True,
        "security_dir": "./test_security",
        "enable_audit_logging": True
    }


@pytest.fixture(scope="session")
def test_filters():
    """Provide test filter configurations."""
    return {
        "document_type": "contracten",
        "jurisdiction": "vlaams",
        "language": "dutch",
        "date_from": "2024-01-01",
        "date_to": "2024-12-31"
    }


@pytest.fixture(scope="session")
def test_session_data():
    """Provide test session data."""
    return {
        "session_id": "test_session_123",
        "filters": {
            "document_type": "contracten",
            "jurisdiction": "vlaams"
        },
        "queries": [
            {
                "question": "What are the key terms of an employment contract?",
                "answer": "Employment contracts typically include...",
                "sources": [
                    {"title": "Employment Law Guide", "page": 15},
                    {"title": "Contract Templates", "page": 8}
                ],
                "processing_time": 2.5
            },
            {
                "question": "How to terminate an employment contract?",
                "answer": "Termination procedures vary by jurisdiction...",
                "sources": [
                    {"title": "Termination Procedures", "page": 22}
                ],
                "processing_time": 1.8
            }
        ]
    }


@pytest.fixture(scope="session")
def test_templates():
    """Provide test template data."""
    return {
        "employment_contract": {
            "name": "Employment Contract Template",
            "description": "Standard employment contract template",
            "content": "This employment contract is made between...",
            "variables": ["employee_name", "employer_name", "start_date", "salary"]
        },
        "legal_opinion": {
            "name": "Legal Opinion Template",
            "description": "Template for legal opinions",
            "content": "Based on the facts presented...",
            "variables": ["client_name", "case_number", "opinion_date"]
        }
    }


@pytest.fixture(scope="session")
def test_security_config():
    """Provide test security configuration."""
    return {
        "master_password": "test_master_password_123",
        "encryption_algorithm": "AES-256-GCM",
        "key_derivation_rounds": 100000,
        "secure_delete_passes": 3,
        "session_timeout": 3600,
        "max_failed_attempts": 5,
        "lockout_duration": 900
    }


@pytest.fixture(scope="function")
def temp_workspace():
    """Create a temporary workspace for individual tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create subdirectories
        os.makedirs(os.path.join(temp_dir, "documents"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "security"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "chroma_db"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "exports"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "logs"), exist_ok=True)
        
        yield temp_dir


@pytest.fixture(scope="function")
def temp_database():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture(scope="function")
def mock_embeddings():
    """Create a mock embeddings model."""
    class MockEmbeddings:
        def __init__(self):
            self.model_name = "test-embeddings"
        
        def embed_documents(self, texts):
            return [[0.1, 0.2, 0.3] for _ in texts]
        
        def embed_query(self, text):
            return [0.1, 0.2, 0.3]
    
    return MockEmbeddings()


@pytest.fixture(scope="function")
def mock_vector_store():
    """Create a mock vector store."""
    class MockVectorStore:
        def __init__(self):
            self.documents = []
        
        def add_documents(self, documents):
            self.documents.extend(documents)
            return ["doc_id_1", "doc_id_2"]
        
        def similarity_search(self, query, k=4):
            return [
                type('Document', (), {
                    'page_content': f'Document content for query: {query}',
                    'metadata': {'source': 'test_source.pdf', 'page': 1}
                })()
            ]
        
        def similarity_search_with_relevance_scores(self, query, k=4):
            docs = self.similarity_search(query, k)
            return [(doc, 0.95) for doc in docs]
        
        def as_retriever(self, search_kwargs=None):
            class MockRetriever:
                def __init__(self, store):
                    self.store = store
                
                def get_relevant_documents(self, query):
                    return self.store.similarity_search(query)
            
            return MockRetriever(self)
    
    return MockVectorStore()


@pytest.fixture(scope="function")
def mock_llm():
    """Create a mock LLM."""
    class MockLLM:
        def __init__(self):
            self.model_name = "test-llm"
        
        def invoke(self, prompt):
            return f"Mock response to: {prompt}"
        
        def generate(self, prompts):
            return [f"Mock response to: {prompt}" for prompt in prompts]
    
    return MockLLM()


@pytest.fixture(scope="function")
def sample_legal_documents():
    """Create sample legal documents for testing."""
    return [
        {
            "title": "Employment Contract Template",
            "content": "This employment contract is made between [EMPLOYEE_NAME] and [EMPLOYER_NAME]...",
            "type": "contracten",
            "jurisdiction": "vlaams",
            "language": "dutch",
            "date": "2024-01-15"
        },
        {
            "title": "Vlaams Decreet Arbeid",
            "content": "Het Vlaams Decreet betreffende de arbeidsreglementering...",
            "type": "wetboeken",
            "jurisdiction": "vlaams",
            "language": "dutch",
            "date": "2024-03-20"
        },
        {
            "title": "EU Privacy Directive",
            "content": "The European Union General Data Protection Regulation...",
            "type": "reglementering",
            "jurisdiction": "eu",
            "language": "english",
            "date": "2021-06-15"
        }
    ]


@pytest.fixture(scope="function")
def test_user_inputs():
    """Provide test user inputs for validation testing."""
    return {
        "valid_queries": [
            "What are the requirements for an employment contract?",
            "How to terminate a contract in Belgium?",
            "What are the privacy regulations in the EU?",
            "Explain the difference between wetboeken and jurisprudentie"
        ],
        "invalid_queries": [
            "",  # Empty query
            "A" * 15000,  # Too long
            "<script>alert('xss')</script>",  # XSS attempt
            "javascript:alert('xss')",  # JavaScript protocol
            "data:text/html,<script>alert('xss')</script>"  # Data URL
        ],
        "edge_cases": [
            "Query with 'quotes' and \"double quotes\"",
            "Query with < and > symbols",
            "Query with vs. and et al. abbreviations",
            "Query with multiple    spaces"
        ]
    }


@pytest.fixture(scope="function")
def test_error_scenarios():
    """Provide test error scenarios."""
    return {
        "database_errors": [
            "Database connection failed",
            "Table not found",
            "Constraint violation",
            "Transaction rollback"
        ],
        "security_errors": [
            "Authentication failed",
            "Authorization denied",
            "Encryption failed",
            "Invalid password"
        ],
        "network_errors": [
            "Connection timeout",
            "DNS resolution failed",
            "SSL certificate error",
            "Server not responding"
        ],
        "validation_errors": [
            "Invalid input format",
            "Missing required field",
            "Value out of range",
            "Invalid file type"
        ]
    }


@pytest.fixture(scope="session")
def performance_test_data():
    """Provide data for performance testing."""
    return {
        "file_sizes": [1024, 10240, 102400, 1024000],  # 1KB, 10KB, 100KB, 1MB
        "concurrent_requests": [1, 5, 10, 20],
        "query_complexity": ["simple", "medium", "complex"],
        "document_counts": [10, 100, 1000]
    }


# Test markers
def pytest_configure(config):
    """Configure custom test markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Test utilities
class TestUtils:
    """Utility functions for tests."""
    
    @staticmethod
    def create_test_file(content: str, filepath: str) -> str:
        """Create a test file with given content."""
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    @staticmethod
    def create_test_directory(dirpath: str) -> str:
        """Create a test directory."""
        os.makedirs(dirpath, exist_ok=True)
        return dirpath
    
    @staticmethod
    def cleanup_test_files(filepaths: List[str]):
        """Clean up test files."""
        for filepath in filepaths:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    @staticmethod
    def cleanup_test_directories(dirpaths: List[str]):
        """Clean up test directories."""
        for dirpath in dirpaths:
            if os.path.exists(dirpath):
                shutil.rmtree(dirpath)
    
    @staticmethod
    def assert_file_exists(filepath: str):
        """Assert that a file exists."""
        assert os.path.exists(filepath), f"File does not exist: {filepath}"
    
    @staticmethod
    def assert_file_content(filepath: str, expected_content: str):
        """Assert file content matches expected content."""
        with open(filepath, 'r') as f:
            content = f.read()
        assert content == expected_content, f"File content mismatch: {content} != {expected_content}"
    
    @staticmethod
    def assert_json_structure(data: Dict[str, Any], required_keys: List[str]):
        """Assert JSON structure has required keys."""
        for key in required_keys:
            assert key in data, f"Missing required key: {key}"
    
    @staticmethod
    def assert_error_response(response: Dict[str, Any], error_type: str = None):
        """Assert response indicates an error."""
        assert "success" in response, "Response missing 'success' field"
        assert response["success"] is False, "Response should indicate failure"
        assert "error" in response, "Response missing 'error' field"
        if error_type:
            assert error_type in response["error"], f"Error should contain '{error_type}'"


# Make TestUtils available to all tests
@pytest.fixture(scope="session")
def test_utils():
    """Provide test utilities."""
    return TestUtils 