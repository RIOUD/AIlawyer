#!/usr/bin/env python3
"""
Configuration file for Secure Offline Legal Assistant

Centralizes all configuration settings including filtering options,
metadata extraction rules, and system parameters.
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Core System Configuration
try:
    from security_config import get_config
    config = get_config()
    
    # Use security configuration
    SOURCE_DOCUMENTS_PATH = config.source_documents_path
    VECTOR_STORE_PATH = config.vector_store_path
    EMBEDDING_MODEL_NAME = config.embedding_model
    OLLAMA_MODEL_NAME = config.ollama_model
    OLLAMA_BASE_URL = config.ollama_base_url
    MAX_RETRIEVAL_DOCS = config.get_vector_store_config()['max_retrieval_docs']
    
    # Security Configuration
    SECURITY_ENABLED = config.security_enabled
    SECURITY_DIR = config.security_dir
    ENABLE_AUDIT_LOGGING = config.enable_audit_logging
    
    security_config = config.get_security_config()
    ENCRYPTION_ALGORITHM = security_config['encryption_algorithm']
    KEY_DERIVATION_ROUNDS = security_config['key_derivation_rounds']
    SECURE_DELETE_PASSES = security_config['secure_delete_passes']
    SESSION_TIMEOUT_DEFAULT = security_config['session_timeout']
    SESSION_TIMEOUT_SENSITIVE = security_config['session_timeout'] // 2
    FAILED_LOGIN_LOCKOUT_THRESHOLD = security_config['max_failed_attempts']
    FAILED_LOGIN_LOCKOUT_DURATION = security_config['lockout_duration']
    
except ImportError:
    # Fallback configuration for development
    SOURCE_DOCUMENTS_PATH = os.getenv('SOURCE_DOCUMENTS_PATH', "./source_documents")
    VECTOR_STORE_PATH = os.getenv('VECTOR_STORE_PATH', "./chroma_db")
    EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL', "all-MiniLM-L6-v2")
    OLLAMA_MODEL_NAME = os.getenv('OLLAMA_MODEL', "mixtral")
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', "http://localhost:11434")
    MAX_RETRIEVAL_DOCS = int(os.getenv('MAX_RETRIEVAL_DOCS', "4"))
    
    # Security Configuration
    SECURITY_ENABLED = os.getenv('SECURITY_ENABLED', 'true').lower() == 'true'
    SECURITY_DIR = os.getenv('SECURITY_DIR', "./security")
    ENABLE_AUDIT_LOGGING = os.getenv('ENABLE_AUDIT_LOGGING', 'true').lower() == 'true'
    ENCRYPTION_ALGORITHM = "AES-256-GCM"
    KEY_DERIVATION_ROUNDS = 100000
    SECURE_DELETE_PASSES = 3
    SESSION_TIMEOUT_DEFAULT = int(os.getenv('SESSION_TIMEOUT', "3600"))
    SESSION_TIMEOUT_SENSITIVE = int(os.getenv('SESSION_TIMEOUT', "3600")) // 2
    FAILED_LOGIN_LOCKOUT_THRESHOLD = int(os.getenv('MAX_FAILED_ATTEMPTS', "5"))
    FAILED_LOGIN_LOCKOUT_DURATION = int(os.getenv('LOCKOUT_DURATION', "900"))

# Security-sensitive configuration from environment variables
# CRITICAL: These must be set in environment variables for production
SECRET_KEY = os.getenv('SECRET_KEY')
MASTER_PASSWORD = os.getenv('MASTER_PASSWORD')

# Validate required environment variables
required_env_vars = ['SECRET_KEY', 'MASTER_PASSWORD']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    if os.getenv('ENVIRONMENT') == 'production':
        raise ValueError(f"CRITICAL: Missing required environment variables in production: {missing_vars}")
    else:
        print(f"⚠️  WARNING: Missing required environment variables: {missing_vars}")
        print("⚠️  Using insecure fallback values for development only!")
        print("⚠️  Set these variables in your .env file or environment for production")
        
        # Generate temporary secrets for development only
        import secrets
        SECRET_KEY = secrets.token_hex(32)
        MASTER_PASSWORD = "dev_master_password_change_in_production"
        
        print("⚠️  Generated temporary SECRET_KEY for development")
        print("⚠️  Using default MASTER_PASSWORD for development")
else:
    # Validate secret strength in production
    if os.getenv('ENVIRONMENT') == 'production':
        if len(SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long in production")
        if len(MASTER_PASSWORD) < 12:
            raise ValueError("MASTER_PASSWORD must be at least 12 characters long in production")

# Document Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Metadata Extraction Configuration
METADATA_EXTRACTION_ENABLED = True

# Document Type Detection Patterns (Belgian Legal Context)
DOCUMENT_TYPE_PATTERNS = {
    "wetboeken": [
        "wetboek", "code", "wet", "decreet", "ordonnantie", "besluit",
        "koninklijk besluit", "ministerieel besluit", "reglement"
    ],
    "jurisprudentie": [
        "arrest", "vonnis", "beschikking", "uitspraak", "rechtspraak",
        "hof van cassatie", "hof van beroep", "rechtbank", "arbeidsrechtbank"
    ],
    "contracten": [
        "contract", "overeenkomst", "huurovereenkomst", "arbeidsovereenkomst",
        "dienstverlening", "partnership", "licentie", "geheimhouding", "nda"
    ],
    "advocatenstukken": [
        "conclusie", "verzoekschrift", "dagvaarding", "antwoord", "repliek",
        "dupliek", "memorie", "nota", "advies"
    ],
    "rechtsleer": [
        "doctrine", "commentaar", "annotatie", "artikel", "publicatie",
        "tijdschrift", "handboek", "leerboek"
    ],
    "reglementering": [
        "reglement", "richtlijn", "circulaire", "omzendbrief", "richtsnoer",
        "procedure", "werkwijze"
    ]
}

# Jurisdiction Detection Patterns (Belgian Legal Context)
JURISDICTION_PATTERNS = {
    "federaal": [
        "federaal", "federale", "belgië", "belgische", "koninkrijk",
        "hof van cassatie", "grondwettelijk hof", "raad van state"
    ],
    "vlaams": [
        "vlaanderen", "vlaamse", "vlaams", "decreet", "vlaams parlement",
        "vlaamse regering", "vlaamse overheid"
    ],
    "waals": [
        "wallonië", "waals", "waalse", "decreet wallon", "parlement wallon",
        "waalse regering", "waalse overheid"
    ],
    "brussels": [
        "brussel", "brusselse", "ordonnantie", "brussels parlement",
        "brusselse regering", "brusselse overheid"
    ],
    "gemeentelijk": [
        "gemeente", "gemeentelijk", "gemeentelijke", "gemeenteraad",
        "college van burgemeester en schepenen", "politiezone"
    ],
    "provinciaal": [
        "provincie", "provinciaal", "provinciale", "provincieraad",
        "deputatie", "provinciegouverneur"
    ],
    "eu": [
        "europese unie", "eu", "europees", "europese", "richtlijn",
        "verordening", "europees hof van justitie"
    ]
}

# Date Extraction Patterns
DATE_PATTERNS = [
    r'\b\d{4}\b',  # Year only
    r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
    r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
    r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
]

# Filter Configuration
DEFAULT_FILTERS = {
    "document_type": None,
    "date_range": None,
    "jurisdiction": None,
    "source": None
}

# Search Configuration (Belgian Legal Context)
SEARCH_CONFIG = {
    "enable_filters": True,
    "default_retrieval_count": 4,
    "similarity_threshold": 0.7,
    "enable_metadata_search": True,
    "belgian_context": True,
    "language_support": ["nl", "fr", "en"]  # Dutch, French, English
}

# UI Configuration
UI_CONFIG = {
    "show_filters": True,
    "show_metadata": True,
    "show_source_preview": True,
    "max_source_preview_length": 200
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "log_queries": True,
    "log_filters": True,
    "log_file": "legal_assistant.log"
}

def get_filter_options() -> Dict[str, List[str]]:
    """
    Returns available filter options for the UI (Belgian Legal Context).
    
    Returns:
        Dictionary of filter categories and their options
    """
    return {
        "document_type": list(DOCUMENT_TYPE_PATTERNS.keys()),
        "jurisdiction": list(JURISDICTION_PATTERNS.keys()),
        "source": ["all", "recent", "archived"],  # Can be expanded based on actual sources
        "language": ["nl", "fr", "en", "all"]  # Dutch, French, English, All
    }

def validate_config() -> bool:
    """
    Validates the configuration settings.
    
    Returns:
        True if configuration is valid, False otherwise
    """
    required_paths = [SOURCE_DOCUMENTS_PATH, VECTOR_STORE_PATH]
    
    for path in required_paths:
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception:
                return False
    
    return True 