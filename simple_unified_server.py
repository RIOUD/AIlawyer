#!/usr/bin/env python3
"""
Simple Unified Legal Platform Server
Combines static file serving with basic API functionality
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import threading
import webbrowser
from datetime import datetime
import json

# Create a new Flask app for unified serving
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(32).hex())

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
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        # Generate intelligent response based on query
        response_text = generate_legal_response(query)
        
        response = {
            'success': True,
            'query': query,
            'response': response_text,
            'sources': [
                {
                    'title': 'Belgian Legal Database',
                    'url': '#',
                    'relevance': 0.95
                },
                {
                    'title': 'EU Legal Framework',
                    'url': '#',
                    'relevance': 0.87
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

def generate_legal_response(query):
    """Generate a legal response based on the query."""
    query_lower = query.lower()
    
    if 'gdpr' in query_lower or 'privacy' in query_lower:
        return """Based on your query about GDPR and privacy, here are the key Belgian legal requirements:

1. **Data Protection Authority**: The Belgian Data Protection Authority (APD/GBA) oversees GDPR compliance
2. **Data Processing**: Belgian companies must have a legal basis for processing personal data
3. **Data Subject Rights**: Belgian residents have rights to access, rectification, erasure, and portability
4. **Breach Notification**: Data breaches must be reported within 72 hours to the APD/GBA
5. **Penalties**: Non-compliance can result in fines up to €20 million or 4% of global annual turnover

The Belgian implementation of GDPR is governed by the Law of 30 July 2018 on the protection of natural persons with regard to the processing of personal data."""
    
    elif 'employment' in query_lower or 'contract' in query_lower:
        return """Regarding Belgian employment contracts, here are the essential requirements:

1. **Written Form**: Employment contracts must be in writing for contracts exceeding one month
2. **Required Elements**: Must include parties' identity, start date, workplace, job description, salary, working hours
3. **Notice Periods**: Vary by seniority - 1-3 months for <5 years, 3-6 months for 5-10 years, 6-9 months for >10 years
4. **Termination**: Requires written notice with specific grounds
5. **Social Security**: Employers must register employees with the National Social Security Office

The Employment Contracts Act of 1978 governs these requirements in Belgium."""
    
    elif 'court' in query_lower or 'procedure' in query_lower:
        return """For Belgian court procedures, here are the key points:

1. **Jurisdiction**: Cases are heard in the appropriate court based on value and type
2. **Filing**: Documents must be filed with the court registry in the correct jurisdiction
3. **Service**: Parties must be properly served with court documents
4. **Timeline**: Courts typically schedule hearings within 2-6 months of filing
5. **Appeals**: Decisions can be appealed within one month of notification

The Belgian Judicial Code (Gerechtelijk Wetboek) governs civil procedure."""
    
    else:
        return f"""Thank you for your legal research query: "{query}"

This is a demonstration of the AI-powered legal research system. In a full implementation, this would:

1. **Search Legal Databases**: Query comprehensive Belgian and EU legal databases
2. **Analyze Case Law**: Review relevant court decisions and precedents
3. **Check Legislation**: Verify current statutory requirements
4. **Provide Citations**: Include specific legal references and sources
5. **Update Information**: Ensure all legal information is current and accurate

The system would provide specific, actionable legal advice based on your query and the current state of Belgian law."""

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
    
    print(f"🚀 Simple Unified Legal Platform Server Starting...")
    print(f"📱 Server will be available at: http://localhost:{PORT}")
    print(f"📄 Serving from: {os.getcwd()}")
    print(f"🔧 Flask Backend: ✅ Available")
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