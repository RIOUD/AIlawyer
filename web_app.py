#!/usr/bin/env python3
"""
LawyerAgent Web Interface
Flask-based web application for the Secure Offline Belgian Legal Assistant
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import existing components
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

# Import new error handling and logging
from exceptions import (
    LegalAssistantError, ValidationError, DatabaseError, SecurityError,
    InputValidationError, QueryValidationError, SessionError
)
from logger import get_logger, log_function_call
from error_handler import ErrorContext
from error_handler import init_error_handling, handle_errors

app = Flask(__name__)

# Import security configuration
try:
    from security_config import get_config
    config = get_config()
    app.secret_key = config.secret_key
except ImportError:
    # Fallback for development
    import os
    app.secret_key = os.getenv('SECRET_KEY', os.urandom(32).hex())

# Initialize logger and error handling
logger = get_logger("web_app")
error_handler = init_error_handling(app, logger)

# Initialize components
try:
    history_manager = HistoryManager()
    template_manager = TemplateManager()
    document_generator = DocumentGenerator(template_manager)
    logger.info("Web application components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize web application components: {e}")
    raise

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
    },
    {
        "name": "brussels_ordonnantie_handel_2022.pdf",
        "type": "wetboeken",
        "jurisdiction": "brussels",
        "language": "french",
        "date": "2022-09-10"
    },
    {
        "name": "arrest_hof_cassatie_2023.pdf",
        "type": "jurisprudentie",
        "jurisdiction": "federaal",
        "language": "dutch",
        "date": "2023-11-05"
    }
]

SAMPLE_TEMPLATES = [
    {
        "id": "employment_contract",
        "name": "Employment Contract (Arbeidsovereenkomst)",
        "category": "contracten",
        "description": "Standard employment contract template for Belgian law",
        "variables": ["employer_name", "employee_name", "position", "salary", "start_date"]
    },
    {
        "id": "nda_agreement",
        "name": "Non-Disclosure Agreement (NDA)",
        "category": "contracten", 
        "description": "Confidentiality agreement template",
        "variables": ["company_name", "employee_name", "confidentiality_period"]
    },
    {
        "id": "service_agreement",
        "name": "Service Agreement (Dienstverleningsovereenkomst)",
        "category": "contracten",
        "description": "Service provider agreement template",
        "variables": ["client_name", "service_provider", "services", "payment_terms"]
    }
]

@app.route('/')
@handle_errors(logger)
def index():
    """Main dashboard page."""
    with ErrorContext("load_dashboard", logger):
        logger.info("Loading dashboard page")
        return render_template('index.html', 
                             documents=SAMPLE_DOCUMENTS,
                             templates=SAMPLE_TEMPLATES)

@app.route('/query')
@handle_errors(logger)
def query_page():
    """Legal query interface."""
    with ErrorContext("load_query_interface", logger):
        logger.info("Loading query interface")
        return render_template('query.html')

@app.route('/api/query', methods=['POST'])
@handle_errors(logger)
def process_query():
    """Process a legal query (demo response)."""
    with ErrorContext("process_legal_query", logger):
        data = request.get_json()
        if not data:
            raise InputValidationError("No JSON data provided")
        
        query = data.get('query', '')
        if not query or not query.strip():
            raise InputValidationError("Query cannot be empty", field="query")
        
        logger.info(f"Processing legal query: {query[:100]}...")
        
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
        
        # Save to history
        history_manager.add_query(query, demo_response["answer"], demo_response["sources"])
        
        logger.info(f"Query processed successfully, confidence: {demo_response['confidence']}")
        return jsonify(demo_response)

@app.route('/filters')
@handle_errors(logger)
def filters_page():
    """Filter management page."""
    with ErrorContext("load_filters_page", logger):
        logger.info("Loading filters page")
        filter_options = get_filter_options()
        return render_template('filters.html', filter_options=filter_options)

@app.route('/templates')
@handle_errors(logger)
def templates_page():
    """Document templates page."""
    with ErrorContext("load_templates_page", logger):
        logger.info("Loading templates page")
        return render_template('templates.html', templates=SAMPLE_TEMPLATES)

@app.route('/security')
def security_page():
    """Security management page."""
    return render_template('security.html')

@app.route('/history')
def history_page():
    """Query history page."""
    # Get recent queries from history manager
    recent_queries = history_manager.get_recent_queries(limit=10)
    return render_template('history.html', queries=recent_queries)

@app.route('/landing')
@handle_errors(logger)
def landing():
    """Landing page for marketing and investor presentations."""
    with ErrorContext("load_landing_page", logger):
        logger.info("Loading landing page")
        return render_template('landing.html')

@app.route('/demo')
@handle_errors(logger)
def demo():
    """Demo page for showcasing platform capabilities."""
    with ErrorContext("load_demo_page", logger):
        logger.info("Loading demo page")
        return render_template('demo.html')

@app.route('/contact')
@handle_errors(logger)
def contact():
    """Contact page for inquiries."""
    with ErrorContext("load_contact_page", logger):
        logger.info("Loading contact page")
        return render_template('contact.html')

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
    
    app.run(host='0.0.0.0', port=5000, debug=True) 