# Secure Offline Belgian Legal Assistant

A production-ready Retrieval-Augmented Generation (RAG) system designed specifically for **Belgian legal professionals** who require complete data privacy and offline operation. This system enables Belgian lawyers to query their private legal document collections using AI assistance without any cloud dependencies or data exposure.

**Specially adapted for Belgian law with:**
- Federal structure awareness (Federaal/Vlaams/Waals/Brussels)
- Belgian legal terminology and document types
- Multi-language support (Dutch/French/English)
- Orde van Vlaamse Balies compliance
- Complete confidentiality for client data

## 🏗️ Architecture

This system implements a secure RAG (Retrieval-Augmented Generation) architecture with the following components:

- **Document Ingestion**: Processes PDF legal documents and creates vector embeddings
- **Vector Database**: ChromaDB for persistent storage of document embeddings
- **Local LLM**: Mixtral-8x7B served via Ollama for offline inference
- **RAG Chain**: LangChain-based retrieval and generation pipeline
- **Source Verification**: Every answer includes citations to source documents

## 🔒 Security Features

- **Complete Offline Operation**: No internet connection required after initial setup
- **Local Data Processing**: All documents and embeddings stored locally
- **No Cloud Dependencies**: Eliminates third-party data exposure risks
- **Source Verification**: Every answer is traceable to specific source documents
- **Client Confidentiality**: Sensitive legal data never leaves your machine
- **Document Encryption at Rest**: AES-256-GCM encryption for sensitive documents
- **Password Protection**: Optional password protection for highly sensitive files
- **Secure Deletion**: Multi-pass secure deletion to prevent data recovery
- **Comprehensive Audit Logging**: Complete audit trails for compliance
- **Master Password Management**: Secure key management and password rotation

### Rich Text Formatting
- **Professional Presentation**: Enhanced console output with rich text formatting
- **Legal Term Highlighting**: Automatic highlighting of important legal terminology
- **Color-coded Sources**: Visual identification of document types and jurisdictions
- **Structured Layout**: Professional document layout with headers and sections
- **Progress Indicators**: Animated status displays for long operations

## 📋 Prerequisites

### 1. Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

### 2. Pull Mixtral Model
```bash
ollama pull mixtral
```

### 3. Python Environment
Ensure you have Python 3.8+ installed with pip.

## 🚀 Setup Instructions

### 1. Clone/Download Project
```bash
git clone <repository-url>
cd Lawyeragent
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare Source Documents
Create a `source_documents` directory and place your legal PDF files inside:
```bash
mkdir source_documents
# Copy your legal PDF documents into this directory
```

### 4. Run Document Ingestion
Process your legal documents to create the vector database:
```bash
python ingest.py
```

### 5. Start the Legal Assistant
Launch the interactive legal assistant:
```bash
python app.py
```

## 💬 Usage

### Asking Questions
Once the application is running, you can ask legal questions in natural language:

```
Ask a legal question: What are the requirements for filing a motion to dismiss?
```

### Advanced Filtering
The system supports advanced filtering to narrow down search results:

**Available Filters (Belgian Legal Context):**
- **Document Type**: wetboeken, jurisprudentie, contracten, advocatenstukken, rechtsleer, reglementering
- **Jurisdiction**: federaal, vlaams, waals, brussels, gemeentelijk, provinciaal, eu
- **Language**: Dutch (Nederlands), French (Français), English, All Languages
- **Date Range**: Filter by specific years or date ranges
- **Source**: all, recent (last 30 days), archived (older than 30 days)

**Using Filters:**
```
Ask a legal question: filters
```
This will prompt you to set filters for your search.

### Query History & Session Management
The system automatically tracks all queries and maintains session history:

**History Commands:**
- `history` - Access history management menu
- `export` - Export conversations to PDF
- `stats` - View usage statistics

**Features:**
- **Persistent Storage**: All queries saved locally in SQLite database
- **Session Tracking**: Automatic session management with timestamps
- **Search History**: Search through previous queries and answers
- **PDF Export**: Export conversations, search results, and statistics
- **Usage Analytics**: View query patterns and filter usage

### Security Commands:
- `security` - Access security management (encryption, audit logs, secure deletion)
- `encrypt` - Encrypt sensitive documents
- `decrypt` - Decrypt protected documents
- `audit` - View security audit logs
- `protect` - Password protect documents

### Other Commands:**
- `help` - Show comprehensive help
- `clear` - Clear all active filters
- `exit` - Quit the application

### Understanding Responses
Each response includes:
- **Answer**: The AI-generated response based on your legal documents
- **Sources**: Specific documents and sections used to generate the answer
- **Metadata**: Document type, jurisdiction, and date information for each source

### Example Filtered Queries (Belgian Legal Context)
```
# Search only federal jurisprudence from 2023
filters → Document Type: jurisprudentie, Jurisdiction: federaal, Date: 2023
Question: Wat zijn de rechten van een werknemer bij een arbeidsovereenkomst?

# Search only Flemish decrees
filters → Document Type: wetboeken, Jurisdiction: vlaams
Question: Welke arbeidsvoorwaarden gelden in Vlaanderen?

# Search Brussels ordinances in French
filters → Document Type: wetboeken, Jurisdiction: brussels, Language: fr
Question: Quelles sont les obligations pour les commerces à Bruxelles?
```

## 📁 Project Structure

```
Lawyeragent/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config.py                   # Belgian legal configuration and filter settings
├── ingest.py                   # Document ingestion script with Belgian metadata extraction
├── app.py                      # Main RAG application with Belgian legal context
├── database.py                 # SQLite database operations
├── history_manager.py          # History and session management
├── export_utils.py             # PDF export functionality
├── setup.py                    # Complete setup automation
├── test_setup.py              # System verification
├── test_filters.py            # Filtering capabilities demo
├── test_history.py            # History management demo
├── create_belgian_sample_document.py  # Belgian legal document generator
├── create_sample_document.py   # Generic sample document generator
├── source_documents/           # Your legal PDF files
├── chroma_db/                 # Vector database (auto-created)
├── legal_assistant.db         # Query history database (auto-created)
├── exports/                   # PDF export directory (auto-created)
├── security/                  # Security files (encryption keys, audit logs)
├── security_manager.py        # Security management system
├── test_security.py           # Security features test suite
├── demo_security.py           # Security features demonstration
├── rich_formatter.py          # Rich text formatting system
└── demo_rich_formatting.py    # Rich formatting demonstration
```

## ⚙️ Configuration

Key configuration variables are defined at the top of `ingest.py` and `app.py`:

- `SOURCE_DOCUMENTS_PATH`: Directory containing source PDFs (default: "./source_documents")
- `VECTOR_STORE_PATH`: Vector database storage location (default: "./chroma_db")
- `EMBEDDING_MODEL_NAME`: Sentence transformer model for embeddings (default: 'all-MiniLM-L6-v2')
- `OLLAMA_MODEL_NAME`: Ollama model name (default: "mixtral")
- `CHUNK_SIZE`: Text chunk size for document splitting (default: 1000)
- `CHUNK_OVERLAP`: Overlap between text chunks (default: 200)

## 🔧 Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Verify mixtral model is pulled: `ollama list`

2. **Memory Issues**
   - Mixtral-8x7B requires significant RAM (16GB+ recommended)
   - Consider using a smaller model if needed

3. **Document Processing Errors**
   - Ensure PDF files are not corrupted
   - Check file permissions on source_documents directory

### Performance Optimization

- **Large Document Collections**: Consider processing documents in batches
- **Memory Usage**: Monitor system resources during operation
- **Response Time**: First query may be slower as models load into memory

## 📄 License

This project is designed for legal professionals and should be used in compliance with applicable legal and ethical guidelines.

## 🤝 Contributing

This is a specialized tool for legal professionals. Contributions should focus on security, accuracy, and legal compliance.

---

**⚠️ Important**: This system is designed for legal professionals who understand their ethical obligations regarding AI-assisted legal work. Always verify AI-generated responses against authoritative legal sources and consult with qualified legal professionals when appropriate. 