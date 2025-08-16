#!/usr/bin/env python3
"""
Secure Offline Legal Assistant - Document Ingestion Script

This script processes legal PDF documents from the source_documents directory,
creates vector embeddings, and stores them in a persistent ChromaDB database
for use by the RAG system.

Security Features:
- All processing occurs locally
- No data transmitted to external services
- Input validation and sanitization
- Secure file handling
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

# LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Import configuration
from config import (
    SOURCE_DOCUMENTS_PATH, VECTOR_STORE_PATH, EMBEDDING_MODEL_NAME,
    CHUNK_SIZE, CHUNK_OVERLAP, METADATA_EXTRACTION_ENABLED,
    DOCUMENT_TYPE_PATTERNS, JURISDICTION_PATTERNS, DATE_PATTERNS
)


def validate_directory(path: str) -> bool:
    """
    Validates that a directory exists and is accessible.
    
    Args:
        path: Directory path to validate
        
    Returns:
        True if directory exists and is accessible, False otherwise
    """
    try:
        return os.path.isdir(path) and os.access(path, os.R_OK)
    except (OSError, PermissionError):
        return False


def get_pdf_files(directory_path: str) -> List[str]:
    """
    Scans directory for PDF files and returns their paths.
    
    Args:
        directory_path: Path to directory to scan
        
    Returns:
        List of PDF file paths
        
    Raises:
        FileNotFoundError: If directory doesn't exist
        PermissionError: If directory is not accessible
    """
    if not validate_directory(directory_path):
        raise FileNotFoundError(f"Directory not found or not accessible: {directory_path}")
    
    pdf_files = []
    try:
        for file_path in Path(directory_path).glob("*.pdf"):
            if file_path.is_file() and file_path.stat().st_size > 0:
                pdf_files.append(str(file_path))
    except (OSError, PermissionError) as e:
        raise PermissionError(f"Cannot access directory {directory_path}: {e}")
    
    return pdf_files


def extract_metadata_from_filename(filename: str) -> Dict[str, Any]:
    """
    Extracts metadata from filename using pattern matching.
    
    Args:
        filename: Name of the PDF file
        
    Returns:
        Dictionary of extracted metadata
    """
    metadata = {
        "source": filename,
        "document_type": "unknown",
        "jurisdiction": "unknown",
        "date": None,
        "filename": filename
    }
    
    filename_lower = filename.lower()
    
    # Extract document type
    for doc_type, patterns in DOCUMENT_TYPE_PATTERNS.items():
        if any(pattern in filename_lower for pattern in patterns):
            metadata["document_type"] = doc_type
            break
    
    # Extract jurisdiction
    for jurisdiction, patterns in JURISDICTION_PATTERNS.items():
        if any(pattern in filename_lower for pattern in patterns):
            metadata["jurisdiction"] = jurisdiction
            break
    
    # Extract date from filename
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, filename)
        if matches:
            metadata["date"] = matches[0]
            break
    
    return metadata


def extract_metadata_from_content(content: str, filename: str) -> Dict[str, Any]:
    """
    Extracts metadata from document content.
    
    Args:
        content: Document text content
        filename: Name of the source file
        
    Returns:
        Dictionary of extracted metadata
    """
    metadata = extract_metadata_from_filename(filename)
    content_lower = content.lower()
    
    # Enhance document type detection from content
    if metadata["document_type"] == "unknown":
        for doc_type, patterns in DOCUMENT_TYPE_PATTERNS.items():
            if any(pattern in content_lower for pattern in patterns):
                metadata["document_type"] = doc_type
                break
    
    # Enhance jurisdiction detection from content
    if metadata["jurisdiction"] == "unknown":
        for jurisdiction, patterns in JURISDICTION_PATTERNS.items():
            if any(pattern in content_lower for pattern in patterns):
                metadata["jurisdiction"] = jurisdiction
                break
    
    # Extract date from content if not found in filename
    if not metadata["date"]:
        for pattern in DATE_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                metadata["date"] = matches[0]
                break
    
    return metadata


def load_documents(pdf_files: List[str]) -> List:
    """
    Loads PDF documents using PyPDFLoader with metadata extraction.
    
    Args:
        pdf_files: List of PDF file paths
        
    Returns:
        List of loaded documents with enhanced metadata
        
    Raises:
        Exception: If document loading fails
    """
    documents = []
    
    for pdf_file in pdf_files:
        try:
            print(f"Loading document: {os.path.basename(pdf_file)}")
            loader = PyPDFLoader(pdf_file)
            doc_pages = loader.load()
            
            # Extract metadata for each page
            for page in doc_pages:
                if METADATA_EXTRACTION_ENABLED:
                    # Extract metadata from content
                    metadata = extract_metadata_from_content(
                        page.page_content, 
                        os.path.basename(pdf_file)
                    )
                    
                    # Add file creation/modification time
                    try:
                        stat = os.stat(pdf_file)
                        metadata["file_created"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
                        metadata["file_modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    except Exception:
                        pass
                    
                    # Update page metadata
                    page.metadata.update(metadata)
                
                documents.append(page)
                
        except Exception as e:
            print(f"Warning: Failed to load {pdf_file}: {e}")
            continue
    
    if not documents:
        raise Exception("No documents were successfully loaded")
    
    print(f"Successfully loaded {len(documents)} document pages with metadata")
    return documents


def split_documents(documents: List, chunk_size: int, chunk_overlap: int) -> List:
    """
    Splits documents into smaller chunks for processing.
    
    Args:
        documents: List of documents to split
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of document chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks")
    return chunks


def create_embeddings(model_name: str):
    """
    Creates HuggingFace embeddings instance.
    
    Args:
        model_name: Name of the sentence transformer model
        
    Returns:
        HuggingFaceEmbeddings instance
    """
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},  # Use CPU for security and compatibility
            encode_kwargs={'normalize_embeddings': True}
        )
        print(f"Initialized embedding model: {model_name}")
        return embeddings
    except Exception as e:
        raise Exception(f"Failed to initialize embedding model: {e}")


def create_vector_store(chunks: List, embeddings, vector_store_path: str):
    """
    Creates and populates the ChromaDB vector store.
    
    Args:
        chunks: Document chunks to store
        embeddings: Embeddings model instance
        vector_store_path: Path to store the vector database
        
    Returns:
        ChromaDB vector store instance
    """
    try:
        # Create vector store directory if it doesn't exist
        os.makedirs(vector_store_path, exist_ok=True)
        
        # Create or load existing vector store
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=vector_store_path
        )
        
        # Persist the database
        vector_store.persist()
        
        print(f"Vector store created/updated at {vector_store_path}")
        return vector_store
        
    except Exception as e:
        raise Exception(f"Failed to create vector store: {e}")


def main():
    """
    Main ingestion function that orchestrates the document processing pipeline.
    """
    print("=== Secure Offline Legal Assistant - Document Ingestion ===")
    print(f"Source documents path: {SOURCE_DOCUMENTS_PATH}")
    print(f"Vector store path: {VECTOR_STORE_PATH}")
    print(f"Embedding model: {EMBEDDING_MODEL_NAME}")
    print(f"Chunk size: {CHUNK_SIZE}, Overlap: {CHUNK_OVERLAP}")
    print("-" * 60)
    
    try:
        # Step 1: Get PDF files
        print("Step 1: Scanning for PDF documents...")
        pdf_files = get_pdf_files(SOURCE_DOCUMENTS_PATH)
        
        if not pdf_files:
            print(f"No PDF files found in {SOURCE_DOCUMENTS_PATH}")
            print("Please add PDF documents to the source_documents directory and run again.")
            sys.exit(1)
        
        print(f"Found {len(pdf_files)} PDF file(s)")
        
        # Step 2: Load documents
        print("\nStep 2: Loading PDF documents...")
        documents = load_documents(pdf_files)
        
        # Step 3: Split documents into chunks
        print("\nStep 3: Splitting documents into chunks...")
        chunks = split_documents(documents, CHUNK_SIZE, CHUNK_OVERLAP)
        
        # Step 4: Initialize embeddings
        print("\nStep 4: Initializing embedding model...")
        embeddings = create_embeddings(EMBEDDING_MODEL_NAME)
        
        # Step 5: Create vector store
        print("\nStep 5: Creating vector store...")
        vector_store = create_vector_store(chunks, embeddings, VECTOR_STORE_PATH)
        
        # Step 6: Verification and metadata summary
        print("\nStep 6: Verifying vector store and metadata...")
        collection_count = vector_store._collection.count()
        print(f"Vector store contains {collection_count} embeddings")
        
        # Print metadata summary
        if METADATA_EXTRACTION_ENABLED:
            print("\n📊 Metadata Summary:")
            try:
                # Get a sample of documents to show metadata distribution
                sample_docs = vector_store.get()
                if sample_docs and 'metadatas' in sample_docs:
                    doc_types = {}
                    jurisdictions = {}
                    
                    for metadata in sample_docs['metadatas']:
                        if metadata:
                            doc_type = metadata.get('document_type', 'unknown')
                            jurisdiction = metadata.get('jurisdiction', 'unknown')
                            
                            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                            jurisdictions[jurisdiction] = jurisdictions.get(jurisdiction, 0) + 1
                    
                    if doc_types:
                        print("Document Types:")
                        for doc_type, count in doc_types.items():
                            print(f"  - {doc_type}: {count} documents")
                    
                    if jurisdictions:
                        print("Jurisdictions:")
                        for jurisdiction, count in jurisdictions.items():
                            print(f"  - {jurisdiction}: {count} documents")
                            
            except Exception as e:
                print(f"Could not retrieve metadata summary: {e}")
        
        print("\n" + "=" * 60)
        print("✅ INGESTION COMPLETE")
        print(f"Vector store created/updated at {VECTOR_STORE_PATH}")
        print("You can now run 'python app.py' to start the legal assistant.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main() 