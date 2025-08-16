#!/usr/bin/env python3
"""
Document Processing Service - Main Application

Handles document ingestion, processing, and storage with secure API endpoints.
"""

import os
import sys
from pathlib import Path

# Add shared library to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

from shared.config import ConfigManager
from shared.models import Document, DocumentType, Jurisdiction, ServiceResponse
from shared.utils import setup_logging, validate_input, extract_security_context, create_service_response, generate_id

# Initialize configuration
config = ConfigManager("document_processing")
if not config.validate():
    print("Configuration validation failed")
    sys.exit(1)

# Setup logging
logger = setup_logging("document_processing", config.service_config.log_level)

# Initialize FastAPI app
app = FastAPI(
    title="Document Processing Service",
    description="Handles document ingestion, processing, and storage",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class DocumentUploadRequest(BaseModel):
    title: str
    document_type: DocumentType
    jurisdiction: Jurisdiction
    language: str
    metadata: Optional[Dict[str, Any]] = None


class ProcessingStatusResponse(BaseModel):
    document_id: str
    status: str
    progress: float
    message: str


# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and validate current user from JWT token."""
    token = credentials.credentials
    security_context = extract_security_context(token, config.security_config.jwt_secret)
    
    if not security_context:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return security_context


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "document_processing"}


# Document upload endpoint
@app.post("/documents/upload", response_model=ServiceResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    request: DocumentUploadRequest = None,
    current_user = Depends(get_current_user)
):
    """Upload and process a document."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate input
        is_valid, sanitized_title, errors = validate_input(request.title)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid title: {errors}")
        
        # Check file type
        allowed_extensions = ['.pdf', '.txt', '.docx', '.doc']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Create document record
        document_id = "doc_" + generate_id()
        
        # Save file
        file_path = f"uploads/{document_id}_{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Start background processing
        background_tasks.add_task(
            process_document_background,
            document_id,
            file_path,
            request,
            current_user.user_id
        )
        
        logger.info(f"Document upload initiated: {document_id} by user {current_user.user_id}")
        
        return create_service_response(
            success=True,
            data={"document_id": document_id, "status": "processing"},
            message="Document upload initiated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_document_background(document_id: str, file_path: str, request: DocumentUploadRequest, user_id: str):
    """Background task to process document."""
    try:
        logger.info(f"Starting background processing for document: {document_id}")
        
        # Update status to processing
        # db_manager.update_document_status(document_id, "processing", 0.0, "Processing document...")
        
        # Process document (extract text, create embeddings, etc.)
        # This would integrate with the existing document processing logic
        
        # Update status to completed
        # db_manager.update_document_status(document_id, "completed", 100.0, "Document processed successfully")
        
        logger.info(f"Background processing completed for document: {document_id}")
        
    except Exception as e:
        logger.error(f"Background processing failed for document {document_id}: {e}")
        # db_manager.update_document_status(document_id, "failed", 0.0, f"Processing failed: {str(e)}")


# Get document status
@app.get("/documents/{document_id}/status", response_model=ProcessingStatusResponse)
async def get_document_status(
    document_id: str,
    current_user = Depends(get_current_user)
):
    """Get the processing status of a document."""
    try:
        # Mock status for now
        status = {
            "status": "completed",
            "progress": 100.0,
            "message": "Document processed successfully"
        }
        
        return ProcessingStatusResponse(
            document_id=document_id,
            status=status["status"],
            progress=status["progress"],
            message=status["message"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get document status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.service_config.host,
        port=config.service_config.port,
        reload=config.service_config.debug
    ) 