#!/usr/bin/env python3
"""
LawyerAgent Web Interface
Flask-based web application for the Secure Offline Belgian Legal Assistant
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, g
from flask_babel import Babel, gettext, ngettext, lazy_gettext
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import existing components
from config import (
    VECTOR_STORE_PATH, EMBEDDING_MODEL_NAME, OLLAMA_MODEL_NAME, 
    OLLAMA_BASE_URL, MAX_RETRIEVAL_DOCS, SECURITY_ENABLED, SECURITY_DIR, ENABLE_AUDIT_LOGGING,
    get_filter_options, DEFAULT_FILTERS, SEARCH_CONFIG, UI_CONFIG
)

# Language configuration (moved inline to avoid import issues)
LANGUAGES = {
    'nl': 'Nederlands',
    'fr': 'Français', 
    'en': 'English',
    'de': 'Deutsch'
}

DEFAULT_LANGUAGE = 'nl'  # Dutch as primary language
SUPPORTED_LANGUAGES = ['nl', 'fr', 'en', 'de']

# Babel Configuration
BABEL_DEFAULT_LOCALE = 'nl'
BABEL_DEFAULT_TIMEZONE = 'Europe/Brussels'
from history_manager import HistoryManager
from cross_reference import CrossReferenceManager
from template_manager import TemplateManager
from document_generator import DocumentGenerator
from security_manager import SecurityManager

# Import logging
from logger import get_logger

app = Flask(__name__)

# Set secret key for sessions
import os
app.secret_key = os.getenv('SECRET_KEY', os.urandom(32).hex())

# Initialize Babel for internationalization
babel = Babel(app)

# Configure Babel
app.config['BABEL_DEFAULT_LOCALE'] = BABEL_DEFAULT_LOCALE
app.config['BABEL_DEFAULT_TIMEZONE'] = BABEL_DEFAULT_TIMEZONE
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# Initialize logger
logger = get_logger("web_app")

# Initialize components
try:
    history_manager = HistoryManager()
    template_manager = TemplateManager()
    document_generator = DocumentGenerator(template_manager)
    logger.info("Web application components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize web application components: {e}")
    raise

def get_locale():
    """Get the locale for the current request."""
    # Check if user has selected a language
    if 'language' in session:
        return session['language']
    
    # Check if language is in URL parameters
    if request.args.get('lang'):
        lang = request.args.get('lang')
        if lang in SUPPORTED_LANGUAGES:
            session['language'] = lang
            return lang
    
    # Check browser's preferred language
    if request.accept_languages:
        for lang in request.accept_languages.best_match(SUPPORTED_LANGUAGES):
            if lang in SUPPORTED_LANGUAGES:
                session['language'] = lang
                return lang
    
    # Default to Dutch
    session['language'] = DEFAULT_LANGUAGE
    return DEFAULT_LANGUAGE

# Set the locale selector function
babel.init_app(app, locale_selector=get_locale)

@app.before_request
def before_request():
    """Set up global variables for templates."""
    g.languages = LANGUAGES
    g.current_language = get_locale()
    g.language_name = LANGUAGES.get(g.current_language, 'Nederlands')

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
def index():
    """Main dashboard page."""
    logger.info("Loading dashboard page")
    return render_template('index.html', 
                         recent_documents=SAMPLE_DOCUMENTS[:4],
                         templates=SAMPLE_TEMPLATES)

@app.route('/query')
def query_page():
    """Legal query interface."""
    logger.info("Loading query interface")
    return render_template('query.html')

@app.route('/documents')
def documents_page():
    """Documents management page."""
    logger.info("Loading documents page")
    return render_template('documents.html', documents=SAMPLE_DOCUMENTS)

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process a legal query (demo response)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    query = data.get('query', '')
    if not query or not query.strip():
        return jsonify({"error": "Query cannot be empty"}), 400
    
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
def filters_page():
    """Filter management page."""
    logger.info("Loading filters page")
    filter_options = get_filter_options()
    return render_template('filters.html', filter_options=filter_options)

@app.route('/templates')
def templates_page():
    """Document templates page."""
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
def landing():
    """Landing page for marketing and investor presentations."""
    logger.info("Loading landing page")
    return render_template('landing.html')

@app.route('/demo')
def demo():
    """Demo page for showcasing platform capabilities."""
    logger.info("Loading demo page")
    return render_template('demo.html')

@app.route('/contact')
def contact():
    """Contact page for inquiries."""
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

@app.route('/language/<lang>')
def change_language(lang):
    """Change the application language."""
    if lang in SUPPORTED_LANGUAGES:
        session['language'] = lang
        logger.info(f"Language changed to: {lang}")
        flash(gettext('Language changed successfully'), 'success')
    else:
        flash(gettext('Unsupported language'), 'error')
    
    # Redirect back to the previous page or dashboard
    return redirect(request.referrer or url_for('index')) # Changed from 'dashboard' to 'index' as per new_code

@app.route('/api/languages')
def get_languages():
    """Get available languages."""
    return jsonify({
        'languages': LANGUAGES,
        'current': session.get('language', DEFAULT_LANGUAGE),
        'default': DEFAULT_LANGUAGE
    })

# Client Management Routes
@app.route('/clients')
def clients_page():
    """Client management page."""
    logger.info("Loading clients page")
    # Sample client data
    sample_clients = [
        {
            "id": 1,
            "name": "Maître Jean Dupont",
            "email": "jean.dupont@avocat.be",
            "phone": "+32 2 123 45 67",
            "practice_area": "Employment Law",
            "status": "active",
            "cases": 3,
            "revenue": 2750
        },
        {
            "id": 2,
            "name": "Me. Marie Dubois",
            "email": "marie.dubois@avocat.be",
            "phone": "+32 2 234 56 78",
            "practice_area": "Commercial Law",
            "status": "active",
            "cases": 2,
            "revenue": 1800
        },
        {
            "id": 3,
            "name": "Adv. Pierre Martin",
            "email": "pierre.martin@avocat.be",
            "phone": "+32 2 345 67 89",
            "practice_area": "Employment Law",
            "status": "active",
            "cases": 1,
            "revenue": 1200
        },
        {
            "id": 4,
            "name": "Mevr. Sophie Leroy",
            "email": "sophie.leroy@avocat.be",
            "phone": "+32 2 456 78 90",
            "practice_area": "Commercial Law",
            "status": "active",
            "cases": 1,
            "revenue": 950
        }
    ]
    return render_template('clients.html', clients=sample_clients)

@app.route('/calendar')
def calendar_page():
    """Calendar and scheduling page."""
    logger.info("Loading calendar page")
    # Sample calendar events
    sample_events = [
        {
            "id": 1,
            "title": "Court Hearing - Dupont Case",
            "date": "2024-01-20",
            "time": "14:00",
            "type": "court_hearing",
            "client": "Maître Jean Dupont",
            "location": "Brussels Court of First Instance"
        },
        {
            "id": 2,
            "title": "Client Meeting - Dubois",
            "date": "2024-01-22",
            "time": "10:00",
            "type": "client_meeting",
            "client": "Me. Marie Dubois",
            "location": "Office"
        },
        {
            "id": 3,
            "title": "Document Review - Martin Case",
            "date": "2024-01-23",
            "time": "16:00",
            "type": "document_review",
            "client": "Adv. Pierre Martin",
            "location": "Office"
        }
    ]
    return render_template('calendar.html', events=sample_events)

@app.route('/billing')
def billing_page():
    """Billing and invoicing page."""
    logger.info("Loading billing page")
    # Sample billing data
    sample_invoices = [
        {
            "id": "INV-2024-001",
            "client": "Maître Jean Dupont",
            "amount": 850,
            "status": "paid",
            "date": "2024-01-15",
            "due_date": "2024-01-30",
            "description": "Employment contract review"
        },
        {
            "id": "INV-2024-002",
            "client": "Me. Marie Dubois",
            "amount": 1200,
            "status": "pending",
            "date": "2024-01-18",
            "due_date": "2024-02-02",
            "description": "Commercial dispute consultation"
        },
        {
            "id": "INV-2024-003",
            "client": "Adv. Pierre Martin",
            "amount": 650,
            "status": "draft",
            "date": "2024-01-20",
            "due_date": "2024-02-05",
            "description": "Legal opinion preparation"
        }
    ]
    
    billing_stats = {
        "monthly_revenue": 2275,
        "pending_amount": 1850,
        "overdue_amount": 0,
        "total_clients": 4
    }
    
    return render_template('billing.html', invoices=sample_invoices, stats=billing_stats)

@app.route('/analytics')
def analytics_page():
    """Analytics and reporting page."""
    logger.info("Loading analytics page")
    
    # Sample analytics data
    analytics_data = {
        "revenue_trend": [
            {"month": "Oct", "revenue": 1800},
            {"month": "Nov", "revenue": 2100},
            {"month": "Dec", "revenue": 1950},
            {"month": "Jan", "revenue": 2275}
        ],
        "practice_areas": [
            {"area": "Employment Law", "clients": 3, "revenue": 2750},
            {"area": "Commercial Law", "clients": 2, "revenue": 1800}
        ],
        "client_growth": [
            {"month": "Oct", "clients": 2},
            {"month": "Nov", "clients": 3},
            {"month": "Dec", "clients": 3},
            {"month": "Jan", "clients": 4}
        ],
        "case_status": [
            {"status": "Active", "count": 10},
            {"status": "Pending", "count": 3},
            {"status": "Closed", "count": 7}
        ]
    }
    
    return render_template('analytics.html', data=analytics_data)

@app.route('/research')
def research_page():
    """Legal research page."""
    logger.info("Loading research page")
    
    # Check for offline legal knowledge base
    from pathlib import Path
    import json
    
    offline_data_dir = Path("offline_legal_knowledge")
    offline_available = offline_data_dir.exists()
    offline_stats = {}
    
    if offline_available:
        try:
            # Load offline statistics
            metadata_dir = offline_data_dir / "metadata"
            if metadata_dir.exists():
                summary_file = metadata_dir / "processing_summary.json"
                if summary_file.exists():
                    with open(summary_file, 'r', encoding='utf-8') as f:
                        offline_stats = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load offline stats: {e}")
    
    # Enhanced research data with official Belgian legal sources
    research_data = {
        "offline_available": offline_available,
        "offline_stats": offline_stats,
        "recent_searches": [
            "Belgian employment law termination",
            "Commercial contract disputes",
            "EU privacy regulations",
            "Flemish regional law"
        ],
        "saved_research": [
            {
                "title": "Employment Law Cases 2024",
                "date": "2024-01-15",
                "results": 45
            },
            {
                "title": "Commercial Law Updates",
                "date": "2024-01-10",
                "results": 23
            }
        ],
        "legal_databases": [
            "Belgian Official Gazette (Moniteur Belge)",
            "Court of Cassation (Hof van Cassatie)",
            "Constitutional Court (Grondwettelijk Hof)",
            "EU Legal Database (EUR-Lex)",
            "Justel Database (FPS Justice)"
        ],
        "belgian_legal_codes": [
            {
                "name": "Burgerlijk Wetboek",
                "english": "Civil Code",
                "french": "Code Civil",
                "german": "Bürgerliches Gesetzbuch",
                "url": "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac=",
                "category": "Federal",
                "last_updated": "2024-01-15"
            },
            {
                "name": "Strafwetboek",
                "english": "Criminal Code", 
                "french": "Code Pénal",
                "german": "Strafgesetzbuch",
                "url": "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac=",
                "category": "Federal",
                "last_updated": "2024-01-10"
            },
            {
                "name": "Wetboek van Strafvordering",
                "english": "Code of Criminal Procedure",
                "french": "Code d'Instruction Criminelle", 
                "german": "Strafprozessordnung",
                "url": "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac=",
                "category": "Federal",
                "last_updated": "2024-01-12"
            },
            {
                "name": "Gerechtelijk Wetboek",
                "english": "Judicial Code",
                "french": "Code Judiciaire",
                "german": "Gerichtsgesetzbuch",
                "url": "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac=",
                "category": "Federal",
                "last_updated": "2024-01-08"
            },
            {
                "name": "Wetboek van koophandel",
                "english": "Commercial Code",
                "french": "Code de Commerce",
                "german": "Handelsgesetzbuch",
                "url": "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac=",
                "category": "Federal",
                "last_updated": "2024-01-14"
            },
            {
                "name": "Wetboek van economisch recht",
                "english": "Economic Law Code",
                "french": "Code de Droit Économique",
                "german": "Wirtschaftsgesetzbuch",
                "url": "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac=",
                "category": "Federal",
                "last_updated": "2024-01-16"
            },
            {
                "name": "Vlaamse Codex Fiscaliteit",
                "english": "Flemish Tax Code",
                "french": "Code Fiscal Flamand",
                "german": "Flämischer Steuercodex",
                "url": "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac=",
                "category": "Regional",
                "last_updated": "2024-01-13"
            },
            {
                "name": "Vlaamse Wooncode",
                "english": "Flemish Housing Code",
                "french": "Code du Logement Flamand",
                "german": "Flämischer Wohnungscodex",
                "url": "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac=",
                "category": "Regional",
                "last_updated": "2024-01-11"
            },
            {
                "name": "Waals Wetboek van Sociale Actie en Gezondheid",
                "english": "Walloon Social Action and Health Code",
                "french": "Code Wallon de l'Action Sociale et de la Santé",
                "german": "Wallonisches Gesetzbuch für Soziale Aktion und Gesundheit",
                "url": "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac=",
                "category": "Regional",
                "last_updated": "2024-01-09"
            },
            {
                "name": "Brussels Wetboek van Ruimtelijke Ordening",
                "english": "Brussels Spatial Planning Code",
                "french": "Code Bruxellois de l'Aménagement du Territoire",
                "german": "Brüsseler Raumordnungsgesetzbuch",
                "url": "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac=",
                "category": "Regional",
                "last_updated": "2024-01-07"
            }
        ],
        "practice_areas": [
            "Arbeidsrecht / Droit du Travail / Employment Law",
            "Handelsrecht / Droit Commercial / Commercial Law", 
            "Burgerlijk Recht / Droit Civil / Civil Law",
            "Strafrecht / Droit Pénal / Criminal Law",
            "Fiscaal Recht / Droit Fiscal / Tax Law",
            "Sociaal Recht / Droit Social / Social Law",
            "Ruimtelijke Ordening / Aménagement du Territoire / Spatial Planning",
            "Milieurecht / Droit de l'Environnement / Environmental Law"
        ]
    }
    
    return render_template('research.html', data=research_data)

# API Routes for functionality
@app.route('/api/clients', methods=['GET'])
def get_clients():
    """Get all clients."""
    # This would normally fetch from database
    return jsonify({"clients": []})

@app.route('/api/clients', methods=['POST'])
def add_client():
    """Add a new client."""
    data = request.get_json()
    # This would normally save to database
    return jsonify({"success": True, "message": "Client added successfully"})

@app.route('/api/calendar/events', methods=['GET'])
def get_events():
    """Get calendar events."""
    # This would normally fetch from database
    return jsonify({"events": []})

@app.route('/api/calendar/events', methods=['POST'])
def add_event():
    """Add a new calendar event."""
    data = request.get_json()
    # This would normally save to database
    return jsonify({"success": True, "message": "Event added successfully"})

@app.route('/api/billing/invoices', methods=['GET'])
def get_invoices():
    """Get all invoices."""
    # This would normally fetch from database
    return jsonify({"invoices": []})

@app.route('/api/billing/invoices', methods=['POST'])
def create_invoice():
    """Create a new invoice."""
    data = request.get_json()
    # This would normally save to database
    return jsonify({"success": True, "message": "Invoice created successfully"})

@app.route('/api/analytics/revenue', methods=['GET'])
def get_revenue_analytics():
    """Get revenue analytics."""
    # This would normally calculate from database
    return jsonify({
        "monthly_revenue": 2275,
        "trend": "+12%",
        "growth_rate": 12.5
    })

@app.route('/api/legal/offline-search', methods=['POST'])
def offline_legal_search():
    """Search offline legal knowledge base."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Check if offline knowledge base is available
        from pathlib import Path
        import json
        
        offline_data_dir = Path("offline_legal_knowledge")
        if not offline_data_dir.exists():
            return jsonify({"error": "Offline knowledge base not available"}), 404
        
        # Load search index
        index_file = offline_data_dir / "metadata" / "search_index.json"
        if not index_file.exists():
            return jsonify({"error": "Search index not found"}), 404
        
        with open(index_file, 'r', encoding='utf-8') as f:
            search_index = json.load(f)
        
        # Simple text-based search
        results = []
        query_lower = query.lower()
        
        # Search in legal codes
        for code_data in search_index.get('search_data', []):
            score = 0
            name = code_data.get('name', '').lower()
            summary = code_data.get('summary', '').lower()
            topics = [topic.lower() for topic in code_data.get('topics', [])]
            keywords = [kw.lower() for kw in code_data.get('keywords', [])]
            
            # Calculate relevance score
            if query_lower in name:
                score += 10
            if query_lower in summary:
                score += 5
            for topic in topics:
                if query_lower in topic:
                    score += 3
            for keyword in keywords:
                if query_lower in keyword:
                    score += 2
            
            if score > 0:
                results.append({
                    'name': code_data.get('name'),
                    'category': code_data.get('category'),
                    'summary': code_data.get('summary'),
                    'topics': code_data.get('topics', []),
                    'score': score,
                    'url': code_data.get('url'),
                    'pdf_url': code_data.get('pdf_url')
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            "query": query,
            "results": results[:20],  # Limit to top 20 results
            "total_results": len(results),
            "search_type": "offline"
        })
        
    except Exception as e:
        logger.error(f"Error in offline legal search: {e}")
        return jsonify({"error": "Search failed"}), 500

@app.route('/api/legal/offline-stats', methods=['GET'])
def get_offline_stats():
    """Get offline legal knowledge base statistics."""
    try:
        from pathlib import Path
        import json
        
        offline_data_dir = Path("offline_legal_knowledge")
        if not offline_data_dir.exists():
            return jsonify({"error": "Offline knowledge base not available"}), 404
        
        # Load statistics
        summary_file = offline_data_dir / "metadata" / "processing_summary.json"
        if not summary_file.exists():
            return jsonify({"error": "Statistics not found"}), 404
        
        with open(summary_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error getting offline stats: {e}")
        return jsonify({"error": "Failed to get statistics"}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🌐 Starting LawyerAgent Web Interface...")
    print("📱 Access the application at: http://localhost:5000")
    print("🔒 Secure offline legal assistant with web interface")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 