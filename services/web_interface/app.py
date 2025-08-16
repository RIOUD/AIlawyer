#!/usr/bin/env python3
"""
Web Interface Service - Main Application

Provides the user interface and API gateway functionality for the Legal Assistant AI Platform.
"""

import os
import sys
import time
from pathlib import Path

# Add shared library to path
sys.path.append(str(Path(__file__).parent.parent.parent / "shared"))

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import httpx

from shared.config import ConfigManager
from shared.models import ServiceResponse
from shared.utils import setup_logging, extract_security_context, create_service_response

# Initialize configuration
config = ConfigManager("web_interface")
if not config.validate():
    print("Configuration validation failed")
    sys.exit(1)

# Setup logging
logger = setup_logging("web_interface", config.service_config.log_level)

# Initialize FastAPI app
app = FastAPI(
    title="Legal Assistant AI Platform - Web Interface",
    description="Web interface and API gateway for the Legal Assistant AI Platform",
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

# Service URLs (in production, these would be environment variables)
SERVICE_URLS = {
    "security": "http://localhost:8001",
    "document_processing": "http://localhost:8002", 
    "query_processing": "http://localhost:8003"
}

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str


class QueryRequest(BaseModel):
    question: str
    filters: Optional[Dict[str, Any]] = None


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
    return {"status": "healthy", "service": "web_interface"}


# Serve main page
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main application page."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Legal Assistant AI Platform</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .header {
                background-color: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            .card {
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .login-form {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .login-form input {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .login-form button {
                padding: 10px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .login-form button:hover {
                background-color: #2980b9;
            }
            .query-form {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .query-form textarea {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-height: 100px;
                resize: vertical;
            }
            .query-form button {
                padding: 10px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .query-form button:hover {
                background-color: #229954;
            }
            .hidden {
                display: none;
            }
            .response {
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 4px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔒 Legal Assistant AI Platform</h1>
            <p>Secure, Offline Legal Document Processing and Query System</p>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>🔐 Authentication</h2>
                <form class="login-form" id="loginForm">
                    <input type="text" id="username" placeholder="Username" required>
                    <input type="password" id="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
                <div id="loginStatus"></div>
            </div>
            
            <div class="card">
                <h2>❓ Legal Query</h2>
                <form class="query-form hidden" id="queryForm">
                    <textarea id="question" placeholder="Ask your legal question here..." required></textarea>
                    <button type="submit">Submit Query</button>
                </form>
                <div id="queryResponse"></div>
            </div>
        </div>
        
        <script>
            let authToken = null;
            
            // Login form handler
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                try {
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ username, password })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        authToken = data.data.token;
                        document.getElementById('loginStatus').innerHTML = 
                            '<div class="response">✅ Login successful! Welcome, ' + data.data.user.username + '</div>';
                        document.getElementById('queryForm').classList.remove('hidden');
                        document.getElementById('loginForm').classList.add('hidden');
                    } else {
                        document.getElementById('loginStatus').innerHTML = 
                            '<div class="response">❌ Login failed: ' + data.error + '</div>';
                    }
                } catch (error) {
                    document.getElementById('loginStatus').innerHTML = 
                        '<div class="response">❌ Error: ' + error.message + '</div>';
                }
            });
            
            // Query form handler
            document.getElementById('queryForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const question = document.getElementById('question').value;
                
                try {
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + authToken
                        },
                        body: JSON.stringify({ 
                            question,
                            session_id: 'web_session_' + Date.now()
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        const responseData = data.data;
                        document.getElementById('queryResponse').innerHTML = `
                            <div class="response">
                                <h3>Answer:</h3>
                                <p>${responseData.answer}</p>
                                <h4>Sources:</h4>
                                <ul>
                                    ${responseData.sources.map(source => 
                                        `<li>${source.title} (${source.source}) - Relevance: ${source.relevance}</li>`
                                    ).join('')}
                                </ul>
                                <p><small>Processing time: ${responseData.processing_time.toFixed(2)}s</small></p>
                            </div>
                        `;
                    } else {
                        document.getElementById('queryResponse').innerHTML = 
                            '<div class="response">❌ Query failed: ' + data.error + '</div>';
                    }
                } catch (error) {
                    document.getElementById('queryResponse').innerHTML = 
                        '<div class="response">❌ Error: ' + error.message + '</div>';
                }
            });
        </script>
    </body>
    </html>
    """


# API Gateway endpoints

# Authentication proxy
@app.post("/api/auth/login", response_model=ServiceResponse)
async def login_proxy(request: LoginRequest):
    """Proxy login request to security service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVICE_URLS['security']}/auth/login",
                json={"username": request.username, "password": request.password},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return create_service_response(
                    success=data.get("success", False),
                    data=data.get("data"),
                    error=data.get("error"),
                    message=data.get("message")
                )
            else:
                return create_service_response(
                    success=False,
                    error="Authentication service unavailable"
                )
                
    except Exception as e:
        logger.error(f"Login proxy failed: {e}")
        return create_service_response(
            success=False,
            error="Authentication service unavailable"
        )


# Query proxy
@app.post("/api/query", response_model=ServiceResponse)
async def query_proxy(
    request: QueryRequest,
    current_user = Depends(get_current_user)
):
    """Proxy query request to query processing service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVICE_URLS['query_processing']}/query",
                json={
                    "question": request.question,
                    "filters": request.filters or {},
                    "session_id": "web_session_" + str(int(time.time()))
                },
                headers={"Authorization": f"Bearer {current_user.token}"},
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return create_service_response(
                    success=data.get("success", False),
                    data=data.get("data"),
                    error=data.get("error"),
                    message=data.get("message")
                )
            else:
                return create_service_response(
                    success=False,
                    error="Query processing service unavailable"
                )
                
    except Exception as e:
        logger.error(f"Query proxy failed: {e}")
        return create_service_response(
            success=False,
            error="Query processing service unavailable"
        )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.service_config.host,
        port=config.service_config.port,
        reload=config.service_config.debug
    ) 