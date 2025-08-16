#!/usr/bin/env python3
"""
Simple Web Interface for Legal Assistant AI Platform
Flask-based web application for the Secure Offline Belgian Legal Assistant
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

app = Flask(__name__)

# Simple secret key for development
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
    },
    {
        "name": "eu_richtlijn_privacy_2021.pdf",
        "type": "reglementering",
        "jurisdiction": "eu",
        "language": "dutch",
        "date": "2021-06-15"
    }
]

SAMPLE_TEMPLATES = [
    {
        "id": "employment_contract",
        "name": "Employment Contract",
        "description": "Standard Belgian employment contract template",
        "category": "contracts",
        "language": "dutch"
    },
    {
        "id": "privacy_policy",
        "name": "Privacy Policy",
        "description": "GDPR-compliant privacy policy template",
        "category": "compliance",
        "language": "dutch"
    }
]

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html', 
                         documents=SAMPLE_DOCUMENTS,
                         templates=SAMPLE_TEMPLATES)

@app.route('/landing')
def landing():
    """Landing page for marketing and investor presentations."""
    return render_template('landing.html')

@app.route('/demo')
def demo():
    """Demo page for showcasing platform capabilities."""
    return render_template('demo.html')

@app.route('/contact')
def contact():
    """Contact page for inquiries."""
    return render_template('contact.html')

@app.route('/query')
def query_page():
    """Legal query interface."""
    return render_template('query.html')

@app.route('/templates')
def templates_page():
    """Document templates page."""
    return render_template('templates.html', templates=SAMPLE_TEMPLATES)

@app.route('/security')
def security_page():
    """Security management page."""
    return render_template('security.html')

@app.route('/history')
def history_page():
    """Query history page."""
    return render_template('history.html', queries=[])

@app.route('/filters')
def filters_page():
    """Filter management page."""
    return render_template('filters.html')

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process a legal query (demo response)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    query = data.get('query', '')
    if not query or not query.strip():
        return jsonify({"error": "Query cannot be empty"}), 400
    
    # Demo response - in real app this would use the AI model
    demo_response = {
        "answer": f"Based on the Belgian legal documents in your collection, here's what I found regarding: '{query}'",
        "sources": [
            {
                "document": "arbeidsovereenkomst_model_2024.pdf",
                "type": "contracten",
                "jurisdiction": "vlaams",
                "relevance": 0.95
            },
            {
                "document": "vlaams_decreet_arbeid_2024.pdf",
                "type": "wetboeken", 
                "jurisdiction": "vlaams",
                "relevance": 0.87
            }
        ],
        "confidence": 0.92,
        "timestamp": datetime.now().isoformat()
    }
    
    return jsonify(demo_response)

@app.route('/api/generate_document', methods=['POST'])
def generate_document():
    """Generate document from template."""
    data = request.get_json()
    template_id = data.get('template_id')
    variables = data.get('variables', {})
    
    # Demo document generation
    demo_document = {
        "content": f"Generated document from template {template_id} with variables: {variables}",
        "filename": f"generated_{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        "status": "success"
    }
    
    return jsonify(demo_document)

@app.route('/api/security/status')
def security_status():
    """Get security status."""
    status = {
        "encryption_enabled": True,
        "audit_logging": True,
        "password_protected_files": 3,
        "recent_security_events": 5,
        "security_level": "high"
    }
    return jsonify(status)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🌐 Starting LawyerAgent Web Interface...")
    print("📱 Access the application at: http://localhost:5000")
    print("🔒 Secure offline legal assistant with web interface")
    print("🎯 Landing page: http://localhost:5000/landing")
    print("🎮 Demo page: http://localhost:5000/demo")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 