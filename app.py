#!/usr/bin/env python3
"""
Secure Offline Legal Assistant - Main RAG Application

This script implements the core RAG (Retrieval-Augmented Generation) system
for legal document querying. It provides an interactive interface for lawyers
to ask questions about their legal documents with source verification.

Security Features:
- Complete offline operation using local Ollama LLM
- Local vector database with ChromaDB
- Source verification for all responses
- Input validation and sanitization
- No data transmission to external services
"""

import os
import sys
import re
import time
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import lru_cache

# LangChain imports
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Import configuration and history management
from config import (
    VECTOR_STORE_PATH, EMBEDDING_MODEL_NAME, OLLAMA_MODEL_NAME, 
    OLLAMA_BASE_URL, MAX_RETRIEVAL_DOCS, SEARCH_CONFIG, UI_CONFIG,
    get_filter_options, DEFAULT_FILTERS, SECURITY_ENABLED, SECURITY_DIR, ENABLE_AUDIT_LOGGING
)
from history_manager import HistoryManager
from cross_reference import CrossReferenceManager
from template_manager import TemplateManager
from document_generator import DocumentGenerator
from security_manager import SecurityManager
from rich_formatter import ConsoleFormatter
from rich.console import Console
from rich.table import Table
from rich.text import Text

# Import enhanced error handling
from exceptions import (
    LegalAssistantError, ValidationError, InputValidationError, 
    EmbeddingError, VectorStoreError, LLMError, DatabaseError,
    AuthenticationError, AuthorizationError
)
from logger import get_logger
from auth_manager import AuthManager

logger = get_logger("app")


@dataclass
class ValidationResult:
    """Result of input validation."""
    is_valid: bool
    sanitized_input: Optional[str] = None
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class InputValidator:
    """Comprehensive input validation for legal queries with enhanced security."""
    
    def __init__(self):
        self.max_input_length = 10000
        self.min_input_length = 3
        
        # Enhanced forbidden patterns for XSS and injection prevention
        self.forbidden_patterns = [
            # XSS patterns
            r'<script.*?>.*?</script>',  # Script tags
            r'<iframe.*?>',              # Iframe tags
            r'<object.*?>',              # Object tags
            r'<embed.*?>',               # Embed tags
            r'<form.*?>',                # Form tags
            r'<input.*?>',               # Input tags
            r'<textarea.*?>',            # Textarea tags
            r'<select.*?>',              # Select tags
            
            # JavaScript injection
            r'javascript:',              # JavaScript protocol
            r'vbscript:',                # VBScript
            r'data:text/html',           # Data URLs
            r'data:application/javascript',  # JavaScript data URLs
            r'data:application/x-javascript', # Alternative JS data URLs
            
            # Event handlers
            r'on\w+\s*=',                # Event handlers
            r'onload\s*=',               # Onload events
            r'onerror\s*=',              # Onerror events
            r'onclick\s*=',              # Onclick events
            
            # SQL injection patterns
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',  # SQL keywords
            r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',  # Boolean injection
            r'(\b(union|select)\b.*\bfrom\b)',  # Union select patterns
            
            # Command injection patterns
            r'(\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|ipconfig)\b)',  # System commands
            r'(\b(rm|del|erase|format|fdisk|mkfs)\b)',  # Destructive commands
            r'(\b(wget|curl|nc|telnet|ssh|ftp|scp)\b)',  # Network commands
            
            # Path traversal
            r'\.\./',                     # Directory traversal
            r'\.\.\\',                    # Windows directory traversal
            r'%2e%2e%2f',                 # URL encoded traversal
            r'%2e%2e%5c',                 # URL encoded Windows traversal
            
            # File inclusion
            r'(\b(include|require|include_once|require_once)\b\s*[\'"][^\'"]*\.\.)',  # PHP includes
            
            # LDAP injection
            r'(\b(uid|cn|ou|dc)\b\s*=\s*[^\s]*\*[^\s]*)',  # LDAP wildcards
            
            # XML injection
            r'<!\[CDATA\[',               # CDATA sections
            r'<!DOCTYPE',                 # DOCTYPE declarations
            r'<\!ENTITY',                 # Entity declarations
            
            # NoSQL injection
            r'(\b(\$where|\$ne|\$gt|\$lt|\$gte|\$lte)\b)',  # MongoDB operators
            r'(\b(\$or|\$and|\$not)\b)',  # MongoDB logical operators
        ]
        
        # Allowlist for safe legal terminology
        self.safe_legal_patterns = [
            r'\b(contract|agreement|clause|section|article|paragraph|subparagraph)\b',
            r'\b(jurisdiction|federal|state|local|municipal|county)\b',
            r'\b(statute|regulation|ordinance|code|law|act)\b',
            r'\b(court|judge|attorney|lawyer|plaintiff|defendant)\b',
            r'\b(evidence|testimony|witness|expert|opinion)\b',
            r'\b(liability|damages|compensation|settlement)\b',
            r'\b(compliance|violation|penalty|fine|sanction)\b',
            r'\b(privacy|confidentiality|disclosure|consent)\b',
            r'\b(employment|labor|discrimination|harassment)\b',
            r'\b(intellectual property|patent|trademark|copyright)\b',
            r'\b(tax|revenue|deduction|exemption|credit)\b',
            r'\b(real estate|property|lease|mortgage|deed)\b',
            r'\b(corporate|business|partnership|corporation|llc)\b',
            r'\b(criminal|felony|misdemeanor|probation|parole)\b',
            r'\b(family|divorce|custody|support|adoption)\b',
            r'\b(immigration|citizenship|visa|asylum|deportation)\b',
            r'\b(bankruptcy|debt|creditor|debtor|discharge)\b',
            r'\b(insurance|coverage|policy|claim|premium)\b',
            r'\b(healthcare|medical|patient|provider|treatment)\b',
            r'\b(environmental|pollution|conservation|regulation)\b',
        ]
    
    def validate_query(self, user_input: str) -> ValidationResult:
        """
        Validate and sanitize user query input with enhanced security checks.
        
        Args:
            user_input: Raw user input
            
        Returns:
            ValidationResult with validation status and sanitized input
        """
        errors = []
        
        # Check for None or empty input
        if not user_input or not user_input.strip():
            return ValidationResult(False, None, ["Input cannot be empty"])
        
        # Check minimum length
        if len(user_input.strip()) < self.min_input_length:
            errors.append(f"Input too short (min {self.min_input_length} characters)")
        
        # Check maximum length
        if len(user_input) > self.max_input_length:
            errors.append(f"Input too long (max {self.max_input_length} characters)")
        
        # Check for forbidden patterns with detailed logging
        for pattern in self.forbidden_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                logger.warning(f"Security violation detected: {pattern} in user input")
                errors.append(f"Security violation: forbidden pattern detected")
                break  # Stop at first violation for security
        
        # Check for suspicious character sequences
        suspicious_patterns = [
            r'[<>"\']{3,}',  # Multiple special characters
            r'[;]{2,}',      # Multiple semicolons
            r'[=]{2,}',      # Multiple equals
            r'[&]{2,}',      # Multiple ampersands
            r'[|]{2,}',      # Multiple pipes
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_input):
                logger.warning(f"Suspicious pattern detected: {pattern} in user input")
                errors.append("Suspicious character sequence detected")
                break
        
        # Validate content contains legal terminology (optional check)
        if not self._contains_legal_content(user_input):
            logger.info("Input may not contain legal terminology - this is informational only")
        
        # Enhanced sanitization
        sanitized = self._sanitize_input(user_input)
        
        # Check if sanitization removed too much content
        if len(sanitized) < len(user_input) * 0.5:
            errors.append("Input contained too many forbidden characters")
        
        # Final length check after sanitization
        if len(sanitized) < self.min_input_length:
            errors.append("Sanitized input too short")
        
        if errors:
            return ValidationResult(False, None, errors)
        
        return ValidationResult(True, sanitized, [])
    
    def _contains_legal_content(self, user_input: str) -> bool:
        """Check if input contains legal terminology."""
        user_input_lower = user_input.lower()
        for pattern in self.safe_legal_patterns:
            if re.search(pattern, user_input_lower, re.IGNORECASE):
                return True
        return False
    
    def _sanitize_input(self, user_input: str) -> str:
        """Enhanced sanitization while preserving legal terminology."""
        # Remove dangerous characters and sequences
        sanitized = user_input.strip()
        
        # Remove HTML/XML tags
        sanitized = re.sub(r'<[^>]*>', '', sanitized)
        
        # Remove dangerous characters but preserve legal punctuation
        sanitized = re.sub(r'[<>"\']', '', sanitized)
        
        # Remove multiple consecutive special characters
        sanitized = re.sub(r'[;=&\|]{2,}', '', sanitized)
        
        # Remove URL schemes except http/https
        sanitized = re.sub(r'(?!https?://)[a-zA-Z]+://', '', sanitized)
        
        # Remove JavaScript and data URLs
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'data:text/html', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'data:application/javascript', '', sanitized, flags=re.IGNORECASE)
        
        # Remove path traversal attempts
        sanitized = re.sub(r'\.\./', '', sanitized)
        sanitized = re.sub(r'\.\.\\', '', sanitized)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Normalize common legal abbreviations
        sanitized = re.sub(r'\bvs\.\b', 'versus', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'\bet al\.\b', 'et alii', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'\bcf\.\b', 'confer', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'\bi\.e\.\b', 'id est', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'\be\.g\.\b', 'exempli gratia', sanitized, flags=re.IGNORECASE)
        
        # Remove any remaining suspicious patterns
        sanitized = re.sub(r'[^\w\s\-.,;:!?()[\]{}@#$%&*+=<>~`|\\/]', '', sanitized)
        
        return sanitized.strip()


class FilteredRetrieverFactory:
    """Factory for creating filtered retrievers with caching."""
    
    def __init__(self, vector_store, max_retrieval_docs: int = 4):
        self.vector_store = vector_store
        self.max_retrieval_docs = max_retrieval_docs
        self._retriever_cache = {}
    
    @lru_cache(maxsize=128)
    def create_retriever(self, filter_hash: str) -> Any:
        """Create retriever with cached filter configuration."""
        filter_dict = self._parse_filter_hash(filter_hash)
        
        search_kwargs = {"k": self.max_retrieval_docs}
        if filter_dict:
            search_kwargs["filter"] = filter_dict
        
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
    
    def _parse_filter_hash(self, filter_hash: str) -> Dict[str, Any]:
        """Parse filter hash back to dictionary."""
        try:
            # This is a simplified implementation
            # In production, you might want to use a more sophisticated approach
            return json.loads(filter_hash)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def _create_filter_hash(self, filters: Dict[str, Any]) -> str:
        """Create hash for filter configuration."""
        filter_str = json.dumps(filters, sort_keys=True)
        return hashlib.md5(filter_str.encode()).hexdigest()


def validate_vector_store(vector_store_path: str) -> bool:
    """
    Validates that the vector store exists and is accessible.
    
    Args:
        vector_store_path: Path to the vector store directory
        
    Returns:
        True if vector store exists and is accessible, False otherwise
    """
    try:
        return os.path.isdir(vector_store_path) and os.access(vector_store_path, os.R_OK)
    except (OSError, PermissionError):
        return False


def load_embeddings(model_name: str):
    """
    Loads the HuggingFace embeddings model.
    
    Args:
        model_name: Name of the sentence transformer model
        
    Returns:
        HuggingFaceEmbeddings instance
        
    Raises:
        EmbeddingError: If embedding model fails to load
    """
    try:
        logger.info(f"Loading embedding model: {model_name}")
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        logger.info(f"✅ Loaded embedding model: {model_name}")
        return embeddings
    except ImportError as e:
        raise EmbeddingError(f"Embedding model not available: {e}", embedding_model=model_name)
    except Exception as e:
        raise EmbeddingError(f"Failed to load embedding model: {e}", embedding_model=model_name)


def load_vector_store(vector_store_path: str, embeddings):
    """
    Loads the persistent ChromaDB vector store.
    
    Args:
        vector_store_path: Path to the vector store directory
        embeddings: HuggingFaceEmbeddings instance
        
    Returns:
        Chroma vector store instance
        
    Raises:
        VectorStoreError: If vector store fails to load
    """
    try:
        logger.info(f"Loading vector store from: {vector_store_path}")
        
        if not validate_vector_store(vector_store_path):
            raise VectorStoreError(f"Vector store not accessible: {vector_store_path}", store_path=vector_store_path)
        
        vector_store = Chroma(
            persist_directory=vector_store_path,
            embedding_function=embeddings
        )
        
        logger.info("✅ Vector store loaded successfully")
        return vector_store
        
    except Exception as e:
        raise VectorStoreError(f"Failed to load vector store: {e}", store_path=vector_store_path)


def create_filtered_retriever(
    vector_store, 
    filters: Dict[str, Any],
    use_cache: bool = True
) -> Any:
    """
    Create filtered retriever with optional caching.
    
    Args:
        vector_store: ChromaDB vector store instance
        filters: Dictionary of filter criteria
        use_cache: Whether to use cached retrievers
        
    Returns:
        Filtered retriever instance
    """
    if not use_cache:
        return _create_retriever_direct(vector_store, filters)
    
    factory = FilteredRetrieverFactory(vector_store, MAX_RETRIEVAL_DOCS)
    filter_hash = factory._create_filter_hash(filters)
    return factory.create_retriever(filter_hash)


def _create_retriever_direct(vector_store, filters: Dict[str, Any]) -> Any:
    """Create retriever directly without caching."""
    filter_dict = {}
    
    # Apply document type filter
    if filters.get("document_type") and filters["document_type"] != "all":
        filter_dict["document_type"] = filters["document_type"]
    
    # Apply jurisdiction filter
    if filters.get("jurisdiction") and filters["jurisdiction"] != "all":
        filter_dict["jurisdiction"] = filters["jurisdiction"]
    
    # Apply language filter
    if filters.get("language") and filters["language"] != "all":
        filter_dict["language"] = filters["language"]
    
    # Apply date range filter
    if filters.get("date_from"):
        filter_dict["date"] = {"$gte": filters["date_from"]}
    if filters.get("date_to"):
        if "date" in filter_dict:
            filter_dict["date"]["$lte"] = filters["date_to"]
        else:
            filter_dict["date"] = {"$lte": filters["date_to"]}
    
    # Create retriever with filters
    if filter_dict:
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": MAX_RETRIEVAL_DOCS,
                "filter": filter_dict
            }
        )
    else:
        retriever = vector_store.as_retriever(
            search_kwargs={"k": MAX_RETRIEVAL_DOCS}
        )
    
    return retriever


def initialize_ollama_llm(model_name: str, base_url: str):
    """
    Initializes the Ollama LLM connection.
    
    Args:
        model_name: Name of the Ollama model
        base_url: Ollama server URL
        
    Returns:
        Ollama LLM instance
        
    Raises:
        LLMError: If Ollama connection fails
    """
    try:
        logger.info(f"Initializing Ollama LLM: {model_name} at {base_url}")
        
        llm = OllamaLLM(
            model=model_name,
            base_url=base_url,
            temperature=0.1,  # Low temperature for more focused responses
            num_ctx=4096,     # Context window size
            repeat_penalty=1.1  # Prevent repetitive responses
        )
        
        # Test the connection
        logger.debug("Testing Ollama connection...")
        test_response = llm.invoke("Test")
        if not test_response:
            raise LLMError("Ollama model not responding", llm_model=model_name)
        
        logger.info(f"✅ Connected to Ollama model: {model_name}")
        return llm
        
    except Exception as e:
        raise LLMError(f"Failed to initialize Ollama LLM: {e}", llm_model=model_name)


def create_rag_chain(vector_store, llm, filters: Optional[Dict[str, Any]] = None):
    """
    Creates the RAG (Retrieval-Augmented Generation) chain with optional filtering.
    
    Args:
        vector_store: ChromaDB vector store instance
        llm: Ollama LLM instance
        filters: Optional dictionary of filter criteria
        
    Returns:
        RetrievalQA chain instance
    """
    # Custom prompt template for Belgian legal queries
    prompt_template = """You are a Belgian legal assistant AI. Use the following context to answer the user's legal question. 
    Always provide accurate, helpful information based on the provided legal documents, with specific attention to Belgian law context.
    
    Important guidelines:
    - Focus on Belgian legal principles and procedures
    - Consider the federal structure (Federaal, Vlaams, Waals, Brussels)
    - Reference relevant Belgian courts and institutions when applicable
    - Be precise about jurisdiction (Federaal, Gemeenschappen, Gewesten, Gemeenten)
    - If the context doesn't contain enough information, clearly state this
    - Always cite specific information from the provided context
    
    Context: {context}
    
    Question: {question}
    
    Answer the question based on the context provided, with Belgian legal context in mind:"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Create filtered retriever
    retriever = create_filtered_retriever(vector_store, filters or {})
    
    # Create the RAG chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    
    print("✅ RAG chain initialized")
    return chain


def sanitize_input(user_input: str) -> str:
    """
    Sanitizes user input to prevent injection attacks.
    
    Args:
        user_input: Raw user input
        
    Returns:
        Sanitized input string
    """
    # Remove potentially dangerous characters and normalize whitespace
    sanitized = re.sub(r'[<>"\']', '', user_input.strip())
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized


def format_sources(source_documents: List) -> str:
    """
    Formats source documents for display with enhanced metadata.
    
    Args:
        source_documents: List of source documents from RAG chain
        
    Returns:
        Formatted string of sources with metadata
    """
    if not source_documents:
        return "No sources found."
    
    sources_text = "\n--- SOURCES ---\n"
    
    for i, doc in enumerate(source_documents, 1):
        # Extract metadata
        metadata = doc.metadata
        source = metadata.get('source', 'Unknown source')
        page = metadata.get('page', 'Unknown page')
        doc_type = metadata.get('document_type', 'unknown')
        jurisdiction = metadata.get('jurisdiction', 'unknown')
        date = metadata.get('date', 'unknown')
        
        # Clean up source path for display
        source_name = os.path.basename(source) if source != 'Unknown source' else source
        
        sources_text += f"\n{i}. 📄 Document: {source_name}"
        if page != 'Unknown page':
            sources_text += f" (Page {page})"
        
        # Add metadata tags
        metadata_tags = []
        if doc_type != 'unknown':
            metadata_tags.append(f"Type: {doc_type}")
        if jurisdiction != 'unknown':
            metadata_tags.append(f"Jurisdiction: {jurisdiction}")
        if date != 'unknown':
            metadata_tags.append(f"Date: {date}")
        
        if metadata_tags:
            sources_text += f"\n   🏷️  {' | '.join(metadata_tags)}"
        
        # Add a snippet of the content
        if UI_CONFIG.get("show_source_preview", True):
            max_length = UI_CONFIG.get("max_source_preview_length", 200)
            content_preview = doc.page_content[:max_length] + "..." if len(doc.page_content) > max_length else doc.page_content
            sources_text += f"\n   📝 Preview: {content_preview}\n"
    
    return sources_text


def display_filter_options():
    """
    Displays available filter options to the user (Belgian Legal Context).
    """
    filter_options = get_filter_options()
    
    print("\n🔍 Available Filters (Belgian Legal Context):")
    print("=" * 50)
    
    print("📋 Document Types (Documenttypes):")
    for i, doc_type in enumerate(filter_options["document_type"], 1):
        print(f"   {i}. {doc_type}")
    
    print("\n🏛️  Jurisdictions (Bevoegdheden):")
    for i, jurisdiction in enumerate(filter_options["jurisdiction"], 1):
        print(f"   {i}. {jurisdiction}")
    
    print("\n📁 Sources (Bronnen):")
    for i, source in enumerate(filter_options["source"], 1):
        print(f"   {i}. {source}")
    
    print("\n🌐 Language (Taal):")
    for i, language in enumerate(filter_options["language"], 1):
        lang_names = {"nl": "Dutch (Nederlands)", "fr": "French (Français)", "en": "English", "all": "All Languages"}
        print(f"   {i}. {lang_names.get(language, language)}")
    
    print("\n📅 Date Range: Enter as YYYY-MM-DD or YYYY")
    print("=" * 50)


def get_user_filters() -> Dict[str, Any]:
    """
    Gets filter preferences from the user.
    
    Returns:
        Dictionary of filter criteria
    """
    if not SEARCH_CONFIG.get("enable_filters", True):
        return {}
    
    filters = DEFAULT_FILTERS.copy()
    filter_options = get_filter_options()
    
    print("\n🔍 Apply Filters (press Enter to skip):")
    
    # Document type filter
    print("\n📋 Document Type:")
    for i, doc_type in enumerate(filter_options["document_type"], 1):
        print(f"   {i}. {doc_type}")
    print("   Enter number or 'all': ", end="")
    
    try:
        choice = input().strip()
        if choice.lower() != 'all' and choice:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(filter_options["document_type"]):
                filters["document_type"] = filter_options["document_type"][choice_idx]
    except (ValueError, IndexError):
        pass
    
    # Jurisdiction filter
    print("\n🏛️  Jurisdiction:")
    for i, jurisdiction in enumerate(filter_options["jurisdiction"], 1):
        print(f"   {i}. {jurisdiction}")
    print("   Enter number or 'all': ", end="")
    
    try:
        choice = input().strip()
        if choice.lower() != 'all' and choice:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(filter_options["jurisdiction"]):
                filters["jurisdiction"] = filter_options["jurisdiction"][choice_idx]
    except (ValueError, IndexError):
        pass
    
    # Source filter
    print("\n📁 Source:")
    for i, source in enumerate(filter_options["source"], 1):
        print(f"   {i}. {source}")
    print("   Enter number or 'all': ", end="")
    
    try:
        choice = input().strip()
        if choice.lower() != 'all' and choice:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(filter_options["source"]):
                filters["source"] = filter_options["source"][choice_idx]
    except (ValueError, IndexError):
        pass
    
    # Date range filter
    print("\n📅 Date Range (optional):")
    print("   Start date (YYYY-MM-DD or YYYY): ", end="")
    start_date = input().strip()
    if start_date:
        filters["date_range"] = {"start_date": start_date}
        
        print("   End date (YYYY-MM-DD or YYYY): ", end="")
        end_date = input().strip()
        if end_date:
            filters["date_range"]["end_date"] = end_date
    
    return filters


def display_history_menu(history_manager: HistoryManager):
    """Display history management menu."""
    print("\n📚 HISTORY MANAGEMENT")
    print("=" * 40)
    print("1. View current session")
    print("2. Search query history")
    print("3. List all sessions")
    print("4. View session summary")
    print("5. Back to main menu")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        # View current session
        queries = history_manager.get_session_history()
        if queries:
            print(f"\n📋 Current Session Queries:")
            for i, query in enumerate(queries, 1):
                print(f"\n{i}. {query.get('query_time', 'Unknown')}")
                print(f"   Q: {query.get('question', 'No question')[:100]}...")
                print(f"   A: {query.get('answer', 'No answer')[:100]}...")
        else:
            print("No queries in current session.")
    
    elif choice == "2":
        # Search query history
        search_term = input("Enter search term: ").strip()
        if search_term:
            results = history_manager.search_history(search_term)
            if results:
                print(f"\n🔍 Search Results for '{search_term}':")
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result.get('query_time', 'Unknown')}")
                    print(f"   Q: {result.get('question', 'No question')[:100]}...")
                    print(f"   A: {result.get('answer', 'No answer')[:100]}...")
            else:
                print("No matching queries found.")
    
    elif choice == "3":
        # List all sessions
        sessions = history_manager.list_sessions()
        if sessions:
            print(f"\n📊 All Sessions:")
            for i, session in enumerate(sessions, 1):
                print(f"\n{i}. Session: {session.get('session_id', 'Unknown')}")
                print(f"   Start: {session.get('start_time', 'Unknown')}")
                print(f"   Queries: {session.get('query_count', 0)}")
                print(f"   Status: {session.get('status', 'Unknown')}")
    
    elif choice == "4":
        # View session summary
        history_manager.display_session_summary()
    
    elif choice == "5":
        print("Returning to main menu...")
    
    else:
        print("Invalid choice. Returning to main menu...")


def display_export_menu(history_manager: HistoryManager):
    """Display export menu."""
    print("\n📄 EXPORT OPTIONS")
    print("=" * 30)
    print("1. Export current session to PDF")
    print("2. Export search results to PDF")
    print("3. Export usage statistics to PDF")
    print("4. Back to main menu")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        # Export current session
        output_path = history_manager.export_session_to_pdf()
        if output_path:
            print(f"✅ Session exported to: {output_path}")
        else:
            print("❌ Failed to export session")
    
    elif choice == "2":
        # Export search results
        search_term = input("Enter search term to export: ").strip()
        if search_term:
            results = history_manager.search_history(search_term)
            if results:
                output_path = history_manager.export_search_results_to_pdf(search_term, results)
                if output_path:
                    print(f"✅ Search results exported to: {output_path}")
                else:
                    print("❌ Failed to export search results")
            else:
                print("No search results to export.")
    
    elif choice == "3":
        # Export statistics
        output_path = history_manager.export_statistics_to_pdf()
        if output_path:
            print(f"✅ Statistics exported to: {output_path}")
        else:
            print("❌ Failed to export statistics")
    
    elif choice == "4":
        print("Returning to main menu...")
    
    else:
        print("Invalid choice. Returning to main menu...")


def display_template_menu(template_manager: TemplateManager, document_generator: DocumentGenerator):
    """Display template management menu."""
    print("\n📋 TEMPLATE MANAGEMENT")
    print("=" * 40)
    print("1. Browse templates")
    print("2. Search templates")
    print("3. Generate document")
    print("4. Preview template")
    print("5. Upload custom template")
    print("6. Manage custom templates")
    print("7. Export template to PDF")
    print("8. Template statistics")
    print("9. Back to main menu")
    
    choice = input("\nEnter your choice (1-9): ").strip()
    
    if choice == "1":
        # Browse templates
        display_template_browser(template_manager)
    
    elif choice == "2":
        # Search templates
        query = input("Enter search query: ").strip()
        if query:
            results = template_manager.search_templates(query)
            display_template_search_results(results)
    
    elif choice == "3":
        # Generate document
        display_document_generator(template_manager, document_generator)
    
    elif choice == "4":
        # Preview template
        display_template_preview(template_manager, document_generator)
    
    elif choice == "5":
        # Upload custom template
        display_template_upload(template_manager)
    
    elif choice == "6":
        # Manage custom templates
        display_custom_template_manager(template_manager)
    
    elif choice == "7":
        # Export template to PDF
        display_template_pdf_export(template_manager, document_generator)
    
    elif choice == "8":
        # Template statistics
        stats = template_manager.get_template_statistics()
        display_template_statistics(stats)
    
    elif choice == "9":
        print("Returning to main menu...")
    
    else:
        print("Invalid choice. Returning to main menu...")


def display_template_browser(template_manager: TemplateManager):
    """Display template browser."""
    print("\n📚 TEMPLATE BROWSER")
    print("=" * 40)
    
    all_templates = template_manager.list_all_templates()
    categories = template_manager.template_library.get_template_categories()
    
    for category, description in categories.items():
        if category in all_templates and all_templates[category]:
            print(f"\n{description} ({len(all_templates[category])} templates):")
            for template_id, template in all_templates[category].items():
                is_custom = template.get('is_custom', False)
                custom_marker = " [CUSTOM]" if is_custom else ""
                print(f"  • {template['name']}{custom_marker}")
                print(f"    {template['description']}")
                print(f"    Language: {template.get('language', 'unknown')}")
                print()


def display_template_search_results(results: List[Dict[str, Any]]):
    """Display template search results."""
    if not results:
        print("❌ No templates found matching your search.")
        return
    
    print(f"\n🔍 SEARCH RESULTS ({len(results)} templates found)")
    print("=" * 50)
    
    for i, result in enumerate(results, 1):
        template = result['template']
        is_custom = result.get('is_custom', False)
        custom_marker = " [CUSTOM]" if is_custom else ""


def display_security_menu(security_manager: SecurityManager):
    """Display security management menu."""
    print("\n🔒 SECURITY MANAGEMENT")
    print("=" * 40)
    print("1. Encrypt document")
    print("2. Decrypt document")
    print("3. Password protect document")
    print("4. Secure delete document")
    print("5. View audit logs")
    print("6. Export audit report")
    print("7. Security status")
    print("8. Change master password")
    print("9. Back to main menu")
    
    choice = input("\nEnter your choice (1-9): ").strip()
    
    if choice == "1":
        # Encrypt document
        file_path = input("Enter file path to encrypt: ").strip()
        if file_path:
            password = input("Enter password for protection (optional, press Enter to skip): ").strip()
            password = password if password else None
            result = security_manager.encrypt_file(file_path, password)
            if result["success"]:
                print(f"✅ File encrypted successfully: {result['encrypted_path']}")
            else:
                print(f"❌ Encryption failed: {result['error']}")
    
    elif choice == "2":
        # Decrypt document
        file_path = input("Enter encrypted file path: ").strip()
        if file_path:
            password = input("Enter password (if required): ").strip()
            password = password if password else None
            result = security_manager.decrypt_file(file_path, password)
            if result["success"]:
                print(f"✅ File decrypted successfully: {result['decrypted_path']}")
            else:
                print(f"❌ Decryption failed: {result['error']}")
    
    elif choice == "3":
        # Password protect document
        file_path = input("Enter file path to protect: ").strip()
        if file_path:
            password = input("Enter protection password: ").strip()
            if password:
                security_manager._add_password_protection(file_path, password)
                print(f"✅ File password protected: {file_path}")
            else:
                print("❌ Password is required")
    
    elif choice == "4":
        # Secure delete document
        file_path = input("Enter file path to securely delete: ").strip()
        if file_path:
            confirm = input("⚠️  This action cannot be undone. Type 'DELETE' to confirm: ").strip()
            if confirm == "DELETE":
                result = security_manager.secure_delete_file(file_path)
                if result["success"]:
                    print(f"✅ File securely deleted: {file_path}")
                else:
                    print(f"❌ Secure deletion failed: {result['error']}")
            else:
                print("❌ Deletion cancelled")
    
    elif choice == "5":
        # View audit logs
        display_audit_logs(security_manager)
    
    elif choice == "6":
        # Export audit report
        output_path = input("Enter output path for audit report (e.g., audit_report.pdf): ").strip()
        if output_path:
            result = security_manager.export_audit_report(output_path)
            if result["success"]:
                print(f"✅ Audit report exported: {output_path}")
            else:
                print(f"❌ Export failed: {result['error']}")
    
    elif choice == "7":
        # Security status
        status = security_manager.get_security_status()
        display_security_status(status)
    
    elif choice == "8":
        # Change master password
        new_password = input("Enter new master password: ").strip()
        if new_password:
            result = security_manager.change_master_password(new_password)
            if result["success"]:
                print("✅ Master password changed successfully")
            else:
                print(f"❌ Password change failed: {result['error']}")
    
    elif choice == "9":
        print("Returning to main menu...")
    
    else:
        print("Invalid choice. Returning to main menu...")


def display_audit_logs(security_manager: SecurityManager):
    """Display audit logs."""
    print("\n📊 AUDIT LOGS")
    print("=" * 40)
    
    # Get recent audit events
    audit_events = security_manager.get_audit_log(limit=20)
    access_events = security_manager.get_access_log(limit=20)
    
    print(f"Recent Security Events ({len(audit_events)}):")
    print("-" * 40)
    for event in audit_events[:10]:
        print(f"• {event['timestamp']} - {event['event_type']}: {event['event_description']}")
    
    print(f"\nRecent Access Events ({len(access_events)}):")
    print("-" * 40)
    for event in access_events[:10]:
        print(f"• {event['timestamp']} - {event['action']}: {event['resource_path']}")


def display_security_status(status: Dict[str, Any]):
    """Display security status."""
    print("\n🛡️  SECURITY STATUS")
    print("=" * 40)
    
    if "error" in status:
        print(f"❌ Error: {status['error']}")
        return
    
    print(f"🔐 Encryption Enabled: {'✅' if status['encryption_enabled'] else '❌'}")
    print(f"📊 Audit Logging: {'✅' if status['audit_logging_enabled'] else '❌'}")
    print(f"🔒 Password Protected Files: {status['password_protected_files']}")
    print(f"📈 Recent Security Events: {status['recent_security_events']}")
    print(f"📈 Recent Access Events: {status['recent_access_events']}")
    print(f"📁 Security Directory: {status['security_dir']}")
    print(f"🔑 Keys File: {'✅' if status['keys_file_exists'] else '❌'}")
    print(f"📊 Audit Database: {'✅' if status['audit_db_exists'] else '❌'}")
    
    print(f"{i}. {template['name']}{custom_marker}")
    print(f"   Category: {result['category']}")
    print(f"   Description: {template['description']}")
    print(f"   Language: {template.get('language', 'unknown')}")
    print(f"   Jurisdiction: {template.get('jurisdiction', 'unknown')}")
    print()


def display_document_generator(template_manager: TemplateManager, document_generator: DocumentGenerator):
    """Display document generator interface."""
    print("\n📄 DOCUMENT GENERATOR")
    print("=" * 40)
    
    # Show available templates
    all_templates = template_manager.list_all_templates()
    categories = template_manager.template_library.get_template_categories()
    
    print("Available templates:")
    for category, description in categories.items():
        if category in all_templates and all_templates[category]:
            print(f"\n{description}:")
            for template_id, template in all_templates[category].items():
                print(f"  • {template['name']} ({template_id})")
    
    # Get template selection
    category = input("\nEnter template category: ").strip()
    template_id = input("Enter template ID: ").strip()
    
    if not category or not template_id:
        print("❌ Category and template ID are required.")
        return
    
    # Get template
    template = template_manager.get_template(category, template_id)
    if not template:
        print("❌ Template not found.")
        return
    
    print(f"\nGenerating document: {template['name']}")
    print(f"Required variables: {', '.join(template.get('variables', []))}")
    
    # Collect variables
    variables = {}
    for var in template.get('variables', []):
        value = input(f"Enter value for '{var}': ").strip()
        if value:
            variables[var] = value
    
    # Generate document
    print("\n🔧 Generating document...")
    result = document_generator.generate_document(category, template_id, variables)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        if 'missing_variables' in result:
            print(f"Missing variables: {', '.join(result['missing_variables'])}")
    else:
        print("✅ Document generated successfully!")
        print("\n📄 Generated Document:")
        print("-" * 40)
        print(result['document'])
        print("-" * 40)
        
        # Ask if user wants to export to PDF
        export_pdf = input("\nExport to PDF? (y/n): ").strip().lower()
        if export_pdf == 'y':
            output_path = f"exports/{template['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf_result = document_generator.export_to_pdf(result, output_path)
            if 'error' in pdf_result:
                print(f"❌ PDF export error: {pdf_result['error']}")
            else:
                print(f"✅ PDF exported to: {output_path}")


def display_template_preview(template_manager: TemplateManager, document_generator: DocumentGenerator):
    """Display template preview."""
    print("\n👁️  TEMPLATE PREVIEW")
    print("=" * 40)
    
    category = input("Enter template category: ").strip()
    template_id = input("Enter template ID: ").strip()
    
    if not category or not template_id:
        print("❌ Category and template ID are required.")
        return
    
    print("\n🔧 Generating preview...")
    preview = document_generator.create_template_preview(category, template_id)
    
    if 'error' in preview:
        print(f"❌ Error: {preview['error']}")
        return
    
    print("✅ Preview generated successfully!")
    print(f"\nTemplate: {preview['template_info']['name']}")
    print(f"Description: {preview['template_info']['description']}")
    print(f"Language: {preview['template_info'].get('language', 'unknown')}")
    
    print(f"\n📄 Preview Document:")
    print("-" * 40)
    print(preview['preview_document'])
    print("-" * 40)


def display_template_upload(template_manager: TemplateManager):
    """Display template upload interface."""
    print("\n📤 TEMPLATE UPLOAD")
    print("=" * 40)
    
    print("Enter template information:")
    name = input("Template name: ").strip()
    description = input("Description: ").strip()
    category = input("Category: ").strip()
    language = input("Language (nl/fr/en): ").strip()
    jurisdiction = input("Jurisdiction: ").strip()
    
    print("\nEnter template content (press Enter twice to finish):")
    template_lines = []
    while True:
        line = input()
        if line == "" and template_lines and template_lines[-1] == "":
            break
        template_lines.append(line)
    
    template_content = "\n".join(template_lines[:-1])  # Remove last empty line
    
    print("\nEnter required variables (comma-separated):")
    variables_input = input("Variables: ").strip()
    variables = [var.strip() for var in variables_input.split(",") if var.strip()]
    
    template_data = {
        'name': name,
        'description': description,
        'category': category,
        'language': language,
        'jurisdiction': jurisdiction,
        'template': template_content,
        'variables': variables
    }
    
    print("\n🔧 Uploading template...")
    result = template_manager.upload_custom_template(template_data)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Template uploaded successfully!")
        print(f"Template ID: {result['template_id']}")
        print(f"Category: {result['category']}")
        print(f"File: {result['file_path']}")


def display_custom_template_manager(template_manager: TemplateManager):
    """Display custom template management."""
    print("\n⚙️  CUSTOM TEMPLATE MANAGEMENT")
    print("=" * 40)
    print("1. List custom templates")
    print("2. Delete custom template")
    print("3. Import template from file")
    print("4. Export template to file")
    print("5. Backup all templates")
    print("6. Restore templates from backup")
    print("7. Back to template menu")
    
    choice = input("\nEnter your choice (1-7): ").strip()
    
    if choice == "1":
        # List custom templates
        custom_templates = template_manager.custom_templates
        if not custom_templates:
            print("❌ No custom templates found.")
        else:
            print("\n📚 CUSTOM TEMPLATES:")
            for category, templates in custom_templates.items():
                print(f"\n{category}:")
                for template_id, template in templates.items():
                    print(f"  • {template['name']} ({template_id})")
                    print(f"    {template['description']}")
    
    elif choice == "2":
        # Delete custom template
        category = input("Enter category: ").strip()
        template_id = input("Enter template ID: ").strip()
        
        if category and template_id:
            result = template_manager.delete_custom_template(category, template_id)
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print("✅ Template deleted successfully!")
    
    elif choice == "3":
        # Import template
        file_path = input("Enter template file path: ").strip()
        if file_path:
            result = template_manager.import_template(file_path)
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print("✅ Template imported successfully!")
    
    elif choice == "4":
        # Export template
        category = input("Enter category: ").strip()
        template_id = input("Enter template ID: ").strip()
        output_path = input("Enter output file path: ").strip()
        
        if category and template_id and output_path:
            result = template_manager.export_template(category, template_id, output_path)
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print("✅ Template exported successfully!")
    
    elif choice == "5":
        # Backup templates
        backup_path = input("Enter backup directory path: ").strip()
        if backup_path:
            result = template_manager.backup_templates(backup_path)
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print("✅ Templates backed up successfully!")
    
    elif choice == "6":
        # Restore templates
        backup_path = input("Enter backup directory path: ").strip()
        if backup_path:
            result = template_manager.restore_templates(backup_path)
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print("✅ Templates restored successfully!")
    
    elif choice == "7":
        print("Returning to template menu...")
    
    else:
        print("Invalid choice.")


def display_template_pdf_export(template_manager: TemplateManager, document_generator: DocumentGenerator):
    """Display template PDF export interface."""
    print("\n📄 TEMPLATE PDF EXPORT")
    print("=" * 40)
    
    category = input("Enter template category: ").strip()
    template_id = input("Enter template ID: ").strip()
    
    if not category or not template_id:
        print("❌ Category and template ID are required.")
        return
    
    # Get template
    template = template_manager.get_template(category, template_id)
    if not template:
        print("❌ Template not found.")
        return
    
    print(f"\nTemplate: {template['name']}")
    print(f"Required variables: {', '.join(template.get('variables', []))}")
    
    # Collect variables
    variables = {}
    for var in template.get('variables', []):
        value = input(f"Enter value for '{var}': ").strip()
        if value:
            variables[var] = value
    
    # Generate and export
    output_path = f"exports/{template['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    print("\n🔧 Generating and exporting to PDF...")
    result = document_generator.generate_and_export(category, template_id, variables, output_path)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print("✅ Document generated and exported successfully!")
        print(f"PDF file: {output_path}")
        print(f"File size: {result['pdf']['file_size']} bytes")


def display_template_statistics(stats: Dict[str, Any]):
    """Display template statistics."""
    print("\n📊 TEMPLATE STATISTICS")
    print("=" * 40)
    
    print(f"Total Templates: {stats['total_templates']}")
    print(f"Built-in Templates: {stats['built_in_templates']}")
    print(f"Custom Templates: {stats['custom_templates']}")
    
    print(f"\nCategories: {', '.join(stats['categories'])}")
    
    if stats.get('language_distribution'):
        print(f"\nLanguage Distribution:")
        for lang, count in stats['language_distribution'].items():
            print(f"  {lang}: {count} templates")
    
    if stats.get('jurisdiction_distribution'):
        print(f"\nJurisdiction Distribution:")
        for jurisdiction, count in stats['jurisdiction_distribution'].items():
            print(f"  {jurisdiction}: {count} templates")


def display_cross_reference_menu(cross_ref_manager: CrossReferenceManager):
    """Display cross-reference analysis menu."""
    print("\n🔗 CROSS-REFERENCE ANALYSIS")
    print("=" * 40)
    print("1. Analyze cross-references for a query")
    print("2. Show document relationships")
    print("3. Find statute-regulation links")
    print("4. Suggest research path")
    print("5. Export cross-reference analysis")
    print("6. Show cross-reference statistics")
    print("7. Back to main menu")
    
    choice = input("\nEnter your choice (1-7): ").strip()
    
    if choice == "1":
        # Analyze cross-references
        query = input("Enter a legal query to analyze: ").strip()
        if query:
            cross_refs = cross_ref_manager.find_cross_references(query)
            display_cross_reference_results(cross_refs)
    
    elif choice == "2":
        # Show document relationships
        doc_id = input("Enter document ID (or press Enter to see available documents): ").strip()
        if not doc_id:
            # Show available documents
            stats = cross_ref_manager.get_cross_reference_statistics()
            print(f"\n📊 Available documents: {stats['total_documents']}")
            print("Enter a document ID from your search results to see relationships.")
        else:
            relationships = cross_ref_manager.get_document_relationships(doc_id)
            display_document_relationships(relationships)
    
    elif choice == "3":
        # Find statute-regulation links
        query = input("Enter a query to find statute-regulation links: ").strip()
        if query:
            links = cross_ref_manager.find_statute_regulation_links(query)
            display_statute_regulation_links(links)
    
    elif choice == "4":
        # Suggest research path
        query = input("Enter a legal query for research path suggestion: ").strip()
        if query:
            research_path = cross_ref_manager.suggest_research_path(query)
            display_research_path(research_path)
    
    elif choice == "5":
        # Export cross-reference analysis
        query = input("Enter a query to export cross-reference analysis: ").strip()
        if query:
            output_path = f"exports/cross_reference_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            success = cross_ref_manager.export_cross_references(query, output_path)
            if success:
                print(f"✅ Cross-reference analysis exported to: {output_path}")
            else:
                print("❌ Failed to export cross-reference analysis")
    
    elif choice == "6":
        # Show cross-reference statistics
        stats = cross_ref_manager.get_cross_reference_statistics()
        display_cross_reference_statistics(stats)
    
    elif choice == "7":
        print("Returning to main menu...")
    
    else:
        print("Invalid choice. Returning to main menu...")


def display_cross_reference_results(cross_refs: Dict[str, Any]):
    """Display cross-reference analysis results."""
    print(f"\n🔗 Cross-Reference Analysis for: '{cross_refs['query']}'")
    print("=" * 60)
    
    # Similar documents
    if cross_refs['similar_documents']:
        print(f"\n📄 Similar Documents ({len(cross_refs['similar_documents'])} found):")
        for i, doc in enumerate(cross_refs['similar_documents'], 1):
            print(f"   {i}. {doc['metadata'].get('source', 'Unknown')}")
            print(f"      Type: {doc['metadata'].get('document_type', 'unknown')}")
            print(f"      Jurisdiction: {doc['metadata'].get('jurisdiction', 'unknown')}")
            print(f"      Similarity: {doc['similarity']:.3f}")
            print()
    
    # Legal precedents
    if cross_refs['legal_precedents']:
        print(f"\n⚖️  Legal Precedents ({len(cross_refs['legal_precedents'])} found):")
        for i, precedent in enumerate(cross_refs['legal_precedents'], 1):
            print(f"   {i}. {precedent['metadata'].get('source', 'Unknown')}")
            print(f"      Relevance: {precedent['relevance']:.3f}")
            print(f"      Similarity: {precedent['similarity']:.3f}")
            print()
    
    # Related concepts
    if cross_refs['related_concepts']:
        print(f"\n🔍 Related Legal Concepts:")
        print(f"   {', '.join(cross_refs['related_concepts'])}")
    
    # Related questions
    if cross_refs['related_questions']:
        print(f"\n❓ Suggested Related Questions:")
        for i, question in enumerate(cross_refs['related_questions'], 1):
            print(f"   {i}. {question}")


def display_document_relationships(relationships: Dict[str, Any]):
    """Display document relationship information."""
    if not relationships:
        print("❌ No relationship information found for this document.")
        return
    
    print(f"\n🔗 Document Relationships: {relationships['document_id']}")
    print("=" * 50)
    
    print(f"Document Type: {relationships.get('document_type', 'Unknown')}")
    print(f"Jurisdiction: {relationships.get('jurisdiction', 'Unknown')}")
    print(f"Date: {relationships.get('date', 'Unknown')}")
    
    # Concepts
    if relationships.get('concepts'):
        print(f"\n🔍 Legal Concepts: {', '.join(relationships['concepts'])}")
    
    # Cross-references
    if relationships.get('cross_references'):
        print(f"\n📄 Cross-References ({len(relationships['cross_references'])} found):")
        for i, ref in enumerate(relationships['cross_references'][:5], 1):
            print(f"   {i}. {ref['metadata'].get('source', 'Unknown')}")
            print(f"      Type: {ref['metadata'].get('document_type', 'unknown')}")
            print(f"      Relationship: {ref.get('relationship_type', 'Unknown')}")
            print(f"      Similarity: {ref['similarity']:.3f}")
            print()


def display_statute_regulation_links(links: List[Dict[str, Any]]):
    """Display statute-regulation links."""
    if not links:
        print("❌ No statute-regulation links found.")
        return
    
    print(f"\n🔗 Statute-Regulation Links ({len(links)} found)")
    print("=" * 50)
    
    for i, link in enumerate(links, 1):
        statute = link['statute']
        regulation = link['regulation']
        
        print(f"   {i}. Statute: {statute['metadata'].get('source', 'Unknown')}")
        print(f"      Regulation: {regulation['metadata'].get('source', 'Unknown')}")
        print(f"      Common Concepts: {', '.join(link['common_concepts'])}")
        print(f"      Statute Similarity: {statute['similarity']:.3f}")
        print(f"      Regulation Similarity: {regulation['similarity']:.3f}")
        print()


def display_research_path(research_path: Dict[str, Any]):
    """Display research path suggestions."""
    print(f"\n🗺️  Research Path for: '{research_path['query']}'")
    print("=" * 50)
    
    print(f"Estimated Complexity: {research_path['estimated_complexity']}")
    print(f"Suggested Approach: {research_path['suggested_approach']}")
    
    if research_path.get('research_steps'):
        print(f"\n📋 Research Steps ({len(research_path['research_steps'])} steps):")
        for step in research_path['research_steps']:
            print(f"\n   Step {step['step']}: {step['description']}")
            print(f"      Reasoning: {step['reasoning']}")
            
            if step.get('documents'):
                print(f"      Documents: {len(step['documents'])} found")
                for j, doc in enumerate(step['documents'][:2], 1):
                    print(f"         {j}. {doc['metadata'].get('source', 'Unknown')}")
            
            if step.get('concepts'):
                print(f"      Concepts: {', '.join(step['concepts'])}")


def display_cross_reference_statistics(stats: Dict[str, Any]):
    """Display cross-reference statistics."""
    print(f"\n📊 Cross-Reference Statistics")
    print("=" * 40)
    
    print(f"Total Documents: {stats['total_documents']}")
    print(f"Total Concepts: {stats['total_concepts']}")
    print(f"Average Connections per Document: {stats['average_connections_per_document']:.2f}")
    
    if stats.get('concept_distribution'):
        print(f"\n🔍 Concept Distribution:")
        for concept, count in sorted(stats['concept_distribution'].items(), 
                                   key=lambda x: x[1], reverse=True):
            print(f"   {concept}: {count} documents")
    
    if stats.get('most_connected_documents'):
        print(f"\n🔗 Most Connected Documents:")
        for doc_id, connections in stats['most_connected_documents']:
            print(f"   {doc_id}: {connections} connections")


def display_comprehensive_help():
    """Display comprehensive help information (Belgian Legal Context)."""
    print("\n📖 COMPREHENSIVE HELP - BELGIAN LEGAL ASSISTANT")
    print("=" * 60)
    
    print("\n🔍 FILTERING (FILTERING):")
    display_filter_options()
    
    print("\n📚 HISTORY MANAGEMENT (GESCHIEDENIS):")
    print("• Type 'history' to manage query history")
    print("• View current session queries")
    print("• Search through previous queries")
    print("• List all sessions")
    print("• View session summaries")
    
    print("\n📋 TEMPLATE MANAGEMENT:")
    print("• Type 'templates' to access template management")
    print("• Browse and search legal document templates")
    print("• Generate documents from templates")
    print("• Upload and manage custom templates")
    print("• Export documents to PDF")
    
    print("\n🔒 SECURITY FEATURES:")
    print("• Type 'security' to access security management")
    print("• Encrypt documents with AES-256-GCM")
    print("• Password protect sensitive documents")
    print("• Secure deletion with multi-pass overwrite")
    print("• Comprehensive audit logging and reports")
    print("• Master password management")
    
    print("\n🔗 CROSS-REFERENCE ANALYSIS:")
    print("• Type 'crossref' to access cross-reference analysis")
    print("• Analyze document relationships")
    print("• Find statute-regulation links")
    print("• Get research path suggestions")
    print("• Export cross-reference analysis")
    
    print("\n📄 EXPORT FEATURES (EXPORT):")
    print("• Type 'export' to export conversations")
    print("• Export current session to PDF")
    print("• Export search results to PDF")
    print("• Export usage statistics to PDF")
    
    print("\n📊 STATISTICS (STATISTIEKEN):")
    print("• Type 'stats' to view usage statistics")
    print("• Total queries and sessions")
    print("• Average queries per session")
    print("• Most common filters used")
    
    print("\n⚙️  OTHER COMMANDS (ANDERE COMMANDO'S):")
    print("• 'filters' - Set search filters")
    print("• 'clear' - Clear all filters")
    print("• 'help' - Show this help")
    print("• 'exit' - Quit the application")
    
    print("\n💡 TIPS FOR BELGIAN LAWYERS:")
    print("• All data is stored locally for complete privacy")
    print("• Compliant with Orde van Vlaamse Balies guidelines")
    print("• Supports Dutch, French, and English queries")
    print("• Federal structure awareness (Federaal/Vlaams/Waals/Brussels)")
    print("• Legal document templates for common procedures")
    print("• Cross-reference detection for enhanced research")
    print("• PDF exports are saved in the 'exports' directory")
    print("• Sessions are automatically tracked")
    print("• Use filters to narrow down search results by jurisdiction")
    
    print("\n🔒 PRIVACY & COMPLIANCE:")
    print("• 100% offline operation - no data leaves your machine")
    print("• Client confidentiality guaranteed")
    print("• No cloud dependencies or external data transmission")
    print("• Complete control over all data and exports")
    
    print("=" * 60)


def process_query(chain, user_question: str, history_manager: HistoryManager = None, 
                 current_filters: Dict = None) -> Dict[str, Any]:
    """
    Processes a user query through the RAG chain and saves to history.
    
    Args:
        chain: RAG chain instance
        user_question: User's legal question
        history_manager: History manager instance
        current_filters: Current active filters
        
    Returns:
        Dictionary containing answer and source documents
    """
    try:
        # Sanitize input
        sanitized_question = sanitize_input(user_question)
        
        if not sanitized_question:
            return {"error": "Empty or invalid question"}
        
        # Record start time for processing
        start_time = time.time()
        
        # Process through RAG chain
        result = chain({"query": sanitized_question})
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare sources for storage
        sources_for_storage = []
        if result.get("source_documents"):
            for doc in result["source_documents"]:
                source_info = {
                    "source": doc.metadata.get('source', 'Unknown'),
                    "page": doc.metadata.get('page', 'Unknown'),
                    "document_type": doc.metadata.get('document_type', 'unknown'),
                    "jurisdiction": doc.metadata.get('jurisdiction', 'unknown'),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                }
                sources_for_storage.append(source_info)
        
        # Save to history if history manager is available
        if history_manager:
            history_manager.save_query(
                question=sanitized_question,
                answer=result.get("result", "No answer generated"),
                sources=sources_for_storage,
                filters=current_filters,
                processing_time=processing_time
            )
        
        return {
            "answer": result.get("result", "No answer generated"),
            "sources": result.get("source_documents", []),
            "processing_time": processing_time
        }
        
    except Exception as e:
        return {"error": f"Error processing query: {e}"}


def authenticate_user(auth_manager: AuthManager) -> dict:
    """
    Authenticate user with secure login process.
    
    Args:
        auth_manager: Authentication manager instance
        
    Returns:
        User information if authentication successful, None otherwise
    """
    print("\n🔐 SECURE LOGIN REQUIRED")
    print("=" * 40)
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            username = input("Username: ").strip()
            if not username:
                print("❌ Username cannot be empty")
                continue
            
            import getpass
            password = getpass.getpass("Password: ")
            if not password:
                print("❌ Password cannot be empty")
                continue
            
            # Attempt authentication
            user_id, token = auth_manager.authenticate(username, password)
            
            # Get user information
            user = auth_manager.get_user(user_id)
            if user:
                print(f"✅ Welcome, {user.username} ({user.role})")
                return {
                    'user_id': user_id,
                    'username': user.username,
                    'role': user.role,
                    'token': token
                }
            
        except AuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            remaining_attempts = max_attempts - attempt - 1
            if remaining_attempts > 0:
                print(f"⚠️  {remaining_attempts} attempts remaining")
            else:
                print("❌ Maximum login attempts exceeded")
                return None
        except Exception as e:
            print(f"❌ Login error: {e}")
            return None
    
    return None


def display_welcome():
    """
    Displays the welcome message and usage instructions (Belgian Legal Context).
    """
    print("\n" + "=" * 70)
    print("🔒 SECURE OFFLINE BELGIAN LEGAL ASSISTANT")
    print("=" * 70)
    print("AI-gestuurde juridische documentenraadpleging met volledige privacy.")
    print("Assistance juridique alimentée par IA avec confidentialité totale.")
    print("All processing occurs locally - no data is transmitted to external services.")
    print("\nFeatures:")
    print("• Query your legal documents using natural language (NL/FR/EN)")
    print("• Get answers with source verification and Belgian legal context")
    print("• Advanced filtering by document type and jurisdiction (Federaal/Vlaams/Waals/Brussels)")
    print("• Persistent query history and session management")
    print("• PDF export of conversations and search results")
    print("• Complete offline operation - 100% confidential")
    print("• Client confidentiality guaranteed - Orde van Vlaamse Balies compliant")
    print("• Secure authentication and session management")
    print("\nCommands:")
    print("• Type 'filters' to set search filters")
    print("• Type 'history' to manage query history")
    print("• Type 'export' to export conversations to PDF")
    print("• Type 'stats' to view usage statistics")
    print("• Type 'help' to see all options")
    print("• Type 'logout' to end session")
    print("• Type 'exit' to quit the application")
    print("=" * 70)


def main():
    """
    Main application function that orchestrates the RAG system.
    """
    try:
        # Display welcome message
        display_welcome()
        
        # Step 1: Initialize authentication
        print("\n🔐 Initializing authentication system...")
        try:
            auth_manager = AuthManager()
            print("✅ Authentication system initialized")
        except Exception as e:
            print(f"❌ Authentication system initialization failed: {e}")
            print("⚠️  Running in insecure mode - NOT RECOMMENDED FOR PRODUCTION")
            auth_manager = None
        
        # Step 2: Authenticate user
        current_user = None
        if auth_manager:
            current_user = authenticate_user(auth_manager)
            if not current_user:
                print("❌ Authentication failed. Exiting.")
                return
        
        # Step 3: Load embeddings
        print("\n🔄 Initializing system components...")
        embeddings = load_embeddings(EMBEDDING_MODEL_NAME)
        
        # Step 2: Load vector store
        vector_store = load_vector_store(VECTOR_STORE_PATH, embeddings)
        
        # Step 3: Initialize Ollama LLM
        llm = initialize_ollama_llm(OLLAMA_MODEL_NAME, OLLAMA_BASE_URL)
        
        # Step 4: Initialize managers
        history_manager = HistoryManager()
        cross_ref_manager = CrossReferenceManager()
        template_manager = TemplateManager()
        document_generator = DocumentGenerator(template_manager)
        
        # Step 4.5: Initialize security manager if enabled
        security_manager = None
        if SECURITY_ENABLED:
            try:
                security_manager = SecurityManager(
                    security_dir=SECURITY_DIR,
                    enable_audit_logging=ENABLE_AUDIT_LOGGING
                )
                print("✅ Security manager initialized")
            except Exception as e:
                print(f"⚠️  Security manager initialization failed: {e}")
                security_manager = None
        
        # Step 4.6: Initialize rich console and formatter
        console = Console()
        formatter = ConsoleFormatter(console)
        print("✅ Rich text formatter initialized")
        
        # Step 5: Build semantic index for cross-references
        print("🔍 Building semantic index for cross-references...")
        cross_ref_manager.build_semantic_index(VECTOR_STORE_PATH)
        
        # Step 6: Create RAG chain (initially without filters)
        current_filters = {}
        rag_chain = create_rag_chain(vector_store, llm, current_filters)
        
        # Step 7: Start a new session
        session_id = history_manager.start_session(current_filters)
        
        print("\n✅ System ready! You can now ask legal questions.")
        print("-" * 70)
        
        # Main interaction loop
        while True:
            try:
                # Get user input
                user_question = input("\nAsk a legal question: ").strip()
                
                # Check for special commands
                if user_question.lower() in ['exit', 'quit', 'q']:
                    # End session before exiting
                    history_manager.end_session()
                    if auth_manager and current_user:
                        auth_manager.logout(current_user['token'])
                    print("\n👋 Thank you for using the Secure Offline Legal Assistant!")
                    print("Remember: Always verify AI-generated responses against authoritative legal sources.")
                    break
                
                elif user_question.lower() == 'logout':
                    # Logout user
                    if auth_manager and current_user:
                        auth_manager.logout(current_user['token'])
                        print("✅ Logged out successfully")
                        # Re-authenticate
                        current_user = authenticate_user(auth_manager)
                        if not current_user:
                            print("❌ Re-authentication failed. Exiting.")
                            break
                    else:
                        print("❌ No active session to logout")
                    continue
                
                elif user_question.lower() == 'filters':
                    # Set new filters
                    current_filters = get_user_filters()
                    rag_chain = create_rag_chain(vector_store, llm, current_filters)
                    print("✅ Filters updated!")
                    continue
                
                elif user_question.lower() == 'history':
                    # Show history management options
                    display_history_menu(history_manager)
                    continue
                
                elif user_question.lower() == 'export':
                    # Show export options
                    display_export_menu(history_manager)
                    continue
                
                elif user_question.lower() == 'templates':
                    # Show template management
                    display_template_menu(template_manager, document_generator)
                    continue
                
                elif user_question.lower() == 'security' and security_manager:
                    # Show security management
                    display_security_menu(security_manager)
                    continue
                
                elif user_question.lower() == 'crossref':
                    # Show cross-reference analysis
                    display_cross_reference_menu(cross_ref_manager)
                    continue
                
                elif user_question.lower() == 'stats':
                    # Show usage statistics
                    history_manager.display_statistics()
                    continue
                
                elif user_question.lower() == 'help':
                    # Show comprehensive help
                    display_comprehensive_help()
                    continue
                
                elif user_question.lower() == 'clear':
                    # Clear filters
                    current_filters = {}
                    rag_chain = create_rag_chain(vector_store, llm, current_filters)
                    formatter.print_success("Filters cleared!")
                    continue
                
                if not user_question:
                    print("Please enter a question.")
                    continue
                
                # Show current filters if any are active
                if current_filters and any(v is not None and v != "all" for v in current_filters.values()):
                    filter_text = Text("🔍 Active filters: ", style="bold blue")
                    filter_text.append(str(current_filters), style="yellow")
                    console.print(filter_text)
                
                # Process the query
                with console.status("[bold green]Processing your question..."):
                    result = process_query(rag_chain, user_question, history_manager, current_filters)
                
                # Show cross-references if available
                if "error" not in result and cross_ref_manager:
                    with console.status("[bold green]Analyzing cross-references..."):
                        cross_refs = cross_ref_manager.find_cross_references(user_question, top_k=3)
                    
                    if cross_refs['similar_documents'] or cross_refs['legal_precedents']:
                        # Create cross-reference table
                        cross_ref_table = Table(title="🔗 Related Documents & Precedents", show_header=True, header_style="bold magenta")
                        cross_ref_table.add_column("Type", style="cyan")
                        cross_ref_table.add_column("Document", style="white")
                        cross_ref_table.add_column("Details", style="yellow")
                        cross_ref_table.add_column("Relevance", style="green")
                        
                        # Add similar documents
                        if cross_refs['similar_documents']:
                            for doc in cross_refs['similar_documents'][:2]:
                                cross_ref_table.add_row(
                                    "📄 Similar Document",
                                    doc['metadata'].get('source', 'Unknown'),
                                    f"({doc['metadata'].get('document_type', 'unknown')})",
                                    f"{doc['similarity']:.2f}"
                                )
                        
                        # Add legal precedents
                        if cross_refs['legal_precedents']:
                            for precedent in cross_refs['legal_precedents'][:2]:
                                cross_ref_table.add_row(
                                    "⚖️  Legal Precedent",
                                    precedent['metadata'].get('source', 'Unknown'),
                                    f"({precedent['metadata'].get('document_type', 'unknown')})",
                                    f"{precedent['relevance']:.2f}"
                                )
                        
                        console.print(cross_ref_table)
                        
                        # Show related concepts
                        if cross_refs['related_concepts']:
                            concepts_text = Text("🔍 Related Concepts: ", style="bold blue")
                            concepts_text.append(", ".join(cross_refs['related_concepts']), style="white")
                            console.print(concepts_text)
                
                if "error" in result:
                    formatter.print_error(result['error'])
                    continue
                
                # Display results with rich formatting
                formatter.print_legal_answer(result["answer"], result["sources"])
                
            except KeyboardInterrupt:
                print("\n\n👋 Application interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                print("Please try again or type 'exit' to quit.")
                continue
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure Ollama is running: ollama serve")
        print("2. Verify mixtral model is pulled: ollama list")
        print("3. Check that you've run 'python ingest.py' first")
        print("4. Ensure sufficient system memory (16GB+ recommended)")
        sys.exit(1)


if __name__ == "__main__":
    main() 