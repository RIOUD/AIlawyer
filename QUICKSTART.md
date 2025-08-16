# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Run the Complete Setup
```bash
python setup.py
```

This will:
- Install all Python dependencies
- Check Ollama installation
- Download the Mixtral model
- Create sample documents
- Verify the system

### Step 2: Process Your Documents
```bash
python ingest.py
```

This processes all PDF files in the `source_documents/` directory and creates the vector database.

### Step 3: Start the Legal Assistant
```bash
python app.py
```

Ask legal questions and get answers with source verification!

## 📋 Example Usage

```
Ask a legal question: What are the requirements for filing a motion to dismiss?
```

## 🔧 Troubleshooting

### If setup fails:
1. Install Ollama: https://ollama.ai
2. Start Ollama: `ollama serve`
3. Run setup again: `python setup.py`

### If ingestion fails:
1. Ensure PDF files are in `source_documents/` directory
2. Check file permissions
3. Verify PDF files are not corrupted

### If app fails to start:
1. Ensure Ollama is running: `ollama serve`
2. Verify Mixtral model: `ollama list`
3. Check vector database exists: `ls chroma_db/`

## 💡 Tips

- **Memory**: Mixtral-8x7B requires 16GB+ RAM
- **Performance**: First query may be slow as models load
- **Security**: All processing is local - no data leaves your machine
- **Sources**: Every answer includes citations to source documents

## 📞 Support

For issues or questions, check the main README.md for detailed documentation. 