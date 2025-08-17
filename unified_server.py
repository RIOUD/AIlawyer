#!/usr/bin/env python3
"""
Unified Legal Platform Server
Combines static file serving with Flask backend functionality
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import threading
import webbrowser
from datetime import datetime
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Flask app components
try:
    from web_app import app as flask_app
    from config import (
        VECTOR_STORE_PATH, EMBEDDING_MODEL_NAME, OLLAMA_MODEL_NAME, 
        OLLAMA_BASE_URL, MAX_RETRIEVAL_DOCS, SEARCH_CONFIG, UI_CONFIG
    )
    from history_manager import HistoryManager
    from cross_reference import CrossReferenceManager
    from template_manager import TemplateManager
    from document_generator import DocumentGenerator
    from security_manager import SecurityManager
    from exceptions import (
        LegalAssistantError, ValidationError, DatabaseError, SecurityError,
        InputValidationError, QueryValidationError, SessionError
    )
    from logger import get_logger, log_function_call
    from error_handler import ErrorContext, init_error_handling, handle_errors
    
    FLASK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Flask components not available: {e}")
    FLASK_AVAILABLE = False

# Create a new Flask app for unified serving
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(32).hex())

# Initialize components if available
if FLASK_AVAILABLE:
    try:
        logger = get_logger("unified_server")
        error_handler = init_error_handling(app, logger)
        history_manager = HistoryManager()
        template_manager = TemplateManager()
        document_generator = DocumentGenerator(template_manager)
        logger.info("Unified server components initialized successfully")
    except Exception as e:
        print(f"⚠️  Failed to initialize some components: {e}")
        FLASK_AVAILABLE = False

# Sample data for demonstration
SAMPLE_DOCUMENTS = [
    {
        "name": "arbeidsovereenkomst_model_2024.pdf",
        "type": "contracten",
        "jurisdiction": "vlaams",
        "language": "dutch",
        "date": "2024-01-15"
    },
    {
        "name": "vlaams_decreet_arbeid_2024.pdf", 
        "type": "wetboeken",
        "jurisdiction": "vlaams",
        "language": "dutch",
        "date": "2024-03-20"
    }
]

SAMPLE_CLIENTS = [
    {
        "id": 1,
        "name": "Jan Janssens",
        "email": "jan.janssens@email.com",
        "phone": "+32 2 123 45 67",
        "status": "active",
        "cases": 3,
        "last_contact": "2024-01-15"
    },
    {
        "id": 2,
        "name": "Marie Dubois",
        "email": "marie.dubois@email.com",
        "phone": "+32 2 234 56 78",
        "status": "active",
        "cases": 1,
        "last_contact": "2024-01-10"
    },
    {
        "id": 3,
        "name": "Pieter Van den Berg",
        "email": "pieter.vandenberg@email.com",
        "phone": "+32 2 345 67 89",
        "status": "inactive",
        "cases": 0,
        "last_contact": "2023-12-20"
    }
]

SAMPLE_EVENTS = [
    {
        "id": 1,
        "title": "Client Meeting - Jan Janssens",
        "date": "2024-01-20",
        "time": "14:00",
        "duration": "60",
        "type": "meeting",
        "client": "Jan Janssens",
        "description": "Review of employment contract case"
    },
    {
        "id": 2,
        "title": "Court Hearing - Case #2024-001",
        "date": "2024-01-22",
        "time": "10:30",
        "duration": "120",
        "type": "court",
        "client": "Marie Dubois",
        "description": "Preliminary hearing for commercial dispute"
    },
    {
        "id": 3,
        "title": "Document Review",
        "date": "2024-01-18",
        "time": "16:00",
        "duration": "90",
        "type": "work",
        "client": "Internal",
        "description": "Review GDPR compliance documents"
    }
]

# Routes for static pages
@app.route('/')
def landing():
    """Serve the landing page."""
    return send_from_directory('.', 'index.html')

@app.route('/login')
def login():
    """Serve the login page."""
    return send_from_directory('.', 'login.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page."""
    return send_from_directory('.', 'dashboard.html')

@app.route('/clients')
def clients():
    """Serve the clients page."""
    return send_from_directory('.', 'clients.html')

@app.route('/calendar')
def calendar():
    """Serve the calendar page."""
    return send_from_directory('.', 'calendar.html')

@app.route('/research')
def research():
    """Serve the research page."""
    return send_from_directory('.', 'research.html')

@app.route('/documents')
def documents():
    """Serve the documents page."""
    return send_from_directory('.', 'documents.html')

@app.route('/billing')
def billing():
    """Serve the billing page."""
    return send_from_directory('.', 'billing.html')

@app.route('/analytics')
def analytics():
    """Serve the analytics page."""
    return send_from_directory('.', 'analytics.html')

@app.route('/settings')
def settings():
    """Serve the settings page."""
    return send_from_directory('.', 'settings.html')

# API Routes for dynamic functionality
@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all clients."""
    return jsonify({
        'success': True,
        'clients': SAMPLE_CLIENTS,
        'total': len(SAMPLE_CLIENTS)
    })

@app.route('/api/clients', methods=['POST'])
def create_client():
    """Create a new client."""
    data = request.get_json()
    new_client = {
        'id': len(SAMPLE_CLIENTS) + 1,
        'name': data.get('name', ''),
        'email': data.get('email', ''),
        'phone': data.get('phone', ''),
        'status': 'active',
        'cases': 0,
        'last_contact': datetime.now().strftime('%Y-%m-%d')
    }
    SAMPLE_CLIENTS.append(new_client)
    return jsonify({
        'success': True,
        'client': new_client,
        'message': 'Client created successfully'
    })

@app.route('/api/calendar/events', methods=['GET'])
def get_events():
    """Get all calendar events."""
    return jsonify({
        'success': True,
        'events': SAMPLE_EVENTS,
        'total': len(SAMPLE_EVENTS)
    })

@app.route('/api/calendar/events', methods=['POST'])
def create_event():
    """Create a new calendar event."""
    data = request.get_json()
    new_event = {
        'id': len(SAMPLE_EVENTS) + 1,
        'title': data.get('title', ''),
        'date': data.get('date', ''),
        'time': data.get('time', ''),
        'duration': data.get('duration', '60'),
        'type': data.get('type', 'meeting'),
        'client': data.get('client', ''),
        'description': data.get('description', '')
    }
    SAMPLE_EVENTS.append(new_event)
    return jsonify({
        'success': True,
        'event': new_event,
        'message': 'Event created successfully'
    })

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process legal research queries."""
    if not FLASK_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'LLM functionality not available',
            'message': 'Please ensure all dependencies are installed'
        })
    
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Mock response for demonstration
        response = {
            'success': True,
            'query': query,
            'response': f"This is a mock response to your query: '{query}'. In a full implementation, this would use the legal database and LLM to provide accurate legal information.",
            'sources': [
                {
                    'title': 'Sample Legal Document',
                    'url': '#',
                    'relevance': 0.95
                }
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to process query'
        })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get all documents."""
    return jsonify({
        'success': True,
        'documents': SAMPLE_DOCUMENTS,
        'total': len(SAMPLE_DOCUMENTS)
    })

# Serve static files
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('.', filename)

def start_server():
    """Start the unified server."""
    PORT = 8080
    
    print(f"🚀 Unified Legal Platform Server Starting...")
    print(f"📱 Server will be available at: http://localhost:{PORT}")
    print(f"📄 Serving from: {os.getcwd()}")
    print(f"🔧 Flask Backend: {'✅ Available' if FLASK_AVAILABLE else '❌ Not Available'}")
    print(f"🛑 Press Ctrl+C to stop the server")
    print("-" * 60)
    print(f"🔗 Available Routes:")
    print(f"   - / (landing page)")
    print(f"   - /login")
    print(f"   - /dashboard")
    print(f"   - /clients (CRM)")
    print(f"   - /calendar")
    print(f"   - /research (LLM)")
    print(f"   - /documents")
    print(f"   - /billing")
    print(f"   - /analytics")
    print(f"   - /settings")
    print(f"")
    print(f"🔌 API Endpoints:")
    print(f"   - POST /api/query (Legal Research)")
    print(f"   - GET/POST /api/clients (CRM)")
    print(f"   - GET/POST /api/calendar/events (Calendar)")
    print(f"   - GET /api/documents (Documents)")
    print("-" * 60)
    
    # Try to open browser automatically
    try:
        webbrowser.open(f'http://localhost:{PORT}')
        print("🌐 Browser opened automatically!")
    except:
        print("⚠️  Could not open browser automatically. Please open manually.")
    
    try:
        app.run(host='0.0.0.0', port=PORT, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")

if __name__ == "__main__":
    start_server() 