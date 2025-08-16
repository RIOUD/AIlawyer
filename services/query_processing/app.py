#!/usr/bin/env python3
"""
Query Processing Service - Main Application

Handles natural language queries and RAG operations with secure API endpoints.
"""

import os
import sys
from pathlib import Path

# Add shared library to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

from shared.config import ConfigManager
from shared.models import QueryRequest, QueryResponse, ServiceResponse
from shared.utils import setup_logging, validate_input, extract_security_context, create_service_response

# Initialize configuration
config = ConfigManager("query_processing")
if not config.validate():
    print("Configuration validation failed")
    sys.exit(1)

# Setup logging
logger = setup_logging("query_processing", config.service_config.log_level)

# Initialize FastAPI app
app = FastAPI(
    title="Query Processing Service",
    description="Handles natural language queries and RAG operations",
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
class QueryRequestModel(BaseModel):
    question: str
    filters: Optional[Dict[str, Any]] = None
    session_id: str


class QueryResponseModel(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    processing_time: float
    confidence_score: float
    related_queries: List[str] = []


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
    return {"status": "healthy", "service": "query_processing"}


# Process query endpoint
@app.post("/query", response_model=ServiceResponse)
async def process_query(
    request: QueryRequestModel,
    current_user = Depends(get_current_user)
):
    """Process a natural language query."""
    try:
        # Validate input
        is_valid, sanitized_question, errors = validate_input(request.question)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid question: {errors}")
        
        # Create query request
        query_request = QueryRequest(
            question=sanitized_question,
            user_id=current_user.user_id,
            filters=request.filters or {},
            session_id=request.session_id,
            priority=1
        )
        
        # Process query (this would integrate with existing RAG logic)
        import time
        start_time = time.time()
        
        # Mock processing for now
        answer = f"Mock response to: {sanitized_question}"
        sources = [
            {
                "title": "Sample Legal Document",
                "source": "sample_document.pdf",
                "page": 1,
                "relevance": 0.95
            }
        ]
        
        processing_time = time.time() - start_time
        
        # Create response
        query_response = QueryResponse(
            answer=answer,
            sources=sources,
            processing_time=processing_time,
            confidence_score=0.85,
            related_queries=["What are the legal requirements?", "How does this apply to my case?"]
        )
        
        logger.info(f"Query processed: {sanitized_question[:50]}... by user {current_user.user_id}")
        
        return create_service_response(
            success=True,
            data=query_response,
            message="Query processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Get query history
@app.get("/queries/history")
async def get_query_history(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    """Get query history for the current user."""
    try:
        # Mock query history for now
        history = [
            {
                "id": "query_1",
                "question": "What are the requirements for an employment contract?",
                "answer": "Employment contracts must include...",
                "created_at": "2024-01-15T10:30:00Z",
                "processing_time": 2.5
            },
            {
                "id": "query_2", 
                "question": "How to terminate a contract in Belgium?",
                "answer": "Contract termination procedures...",
                "created_at": "2024-01-15T11:15:00Z",
                "processing_time": 1.8
            }
        ]
        
        return create_service_response(
            success=True,
            data={
                "queries": history[skip:skip+limit],
                "total": len(history),
                "skip": skip,
                "limit": limit
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get query history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Get query statistics
@app.get("/queries/statistics")
async def get_query_statistics(current_user = Depends(get_current_user)):
    """Get query processing statistics."""
    try:
        if current_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Mock statistics for now
        stats = {
            "total_queries": 1250,
            "average_processing_time": 2.3,
            "queries_today": 45,
            "queries_this_week": 320,
            "most_common_topics": [
                "employment_contracts",
                "contract_termination", 
                "privacy_regulations",
                "tax_compliance"
            ]
        }
        
        return create_service_response(
            success=True,
            data=stats
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get query statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Search queries
@app.get("/queries/search")
async def search_queries(
    q: str,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user)
):
    """Search through query history."""
    try:
        # Validate search query
        is_valid, sanitized_query, errors = validate_input(q)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid search query: {errors}")
        
        # Mock search results for now
        results = [
            {
                "id": "query_1",
                "question": "What are the requirements for an employment contract?",
                "answer": "Employment contracts must include...",
                "created_at": "2024-01-15T10:30:00Z",
                "relevance": 0.95
            }
        ]
        
        return create_service_response(
            success=True,
            data={
                "results": results,
                "total": len(results),
                "query": sanitized_query,
                "skip": skip,
                "limit": limit
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search queries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.service_config.host,
        port=config.service_config.port,
        reload=config.service_config.debug
    ) 