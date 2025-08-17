# 🏛️ Belgian Legal Knowledge Base - Offline Setup Guide

## 🎯 Overview

This guide explains how to set up the complete offline Belgian legal knowledge base for the LawyerAgent platform. The system provides **complete offline access** to all Belgian federal, regional, and community legal codes.

## 📊 What You Get

- **40 Belgian Legal Codes** (Federal, Regional, Community)
- **15,741 Articles** extracted and indexed
- **290 Keywords** identified across 9 legal topics
- **306 MB** total offline database
- **Complete search functionality** without internet
- **Multi-language support** (Dutch, French, English, German)

## 🚀 Quick Setup

### Prerequisites

```bash
# Install required Python packages
pip install requests beautifulsoup4 PyPDF2 flask flask-babel
```

### One-Command Setup

```bash
# Run the complete setup script
python3 setup_offline_legal_knowledge.py
```

This will automatically:
1. ✅ Scrape all Belgian legal codes from Justel
2. ✅ Download all PDF documents (68.5 MB)
3. ✅ Extract and process all content
4. ✅ Create search indexes and metadata
5. ✅ Integrate with the web application

## 📁 Manual Setup (Step by Step)

If you prefer to run each step individually:

### Step 1: Scrape Legal Codes
```bash
python3 justel_scraper.py
```
- Scrapes the complete list of Belgian legal codes
- Creates `justel_legal_codes.json` with metadata

### Step 2: Download PDFs
```bash
python3 offline_legal_knowledge_downloader.py
```
- Downloads all 40 legal code PDFs
- Extracts text content from PDFs
- Creates structured database

### Step 3: Process Content
```bash
python3 legal_content_processor.py
```
- Extracts articles, sections, and keywords
- Creates search indexes
- Generates metadata and statistics

## 🔍 Using the Offline Knowledge Base

### Web Interface

1. **Start the application:**
   ```bash
   python3 web_app.py
   ```

2. **Access the research page:**
   - Navigate to `http://localhost:5000/research`
   - You'll see "Offline Legal Knowledge Base: Status: Available"

3. **Search offline content:**
   - Use the search box to find legal articles
   - Browse by practice areas
   - View statistics and metadata

### API Endpoints

```bash
# Get offline statistics
curl http://localhost:5000/api/legal/offline-stats

# Search offline content
curl -X POST http://localhost:5000/api/legal/offline-search \
  -H "Content-Type: application/json" \
  -d '{"query": "employment law"}'
```

## 📊 Database Structure

```
offline_legal_knowledge/
├── pdfs/                    # Original PDF documents
├── content/                 # Extracted text content
├── database/                # SQLite database
├── metadata/
│   ├── processing_summary.json
│   ├── search_index.json
│   └── legal_codes_metadata.json
└── logs/                    # Processing logs
```

## 🎯 Legal Categories

### Federal Codes (17)
- Civil Code
- Criminal Code
- Judicial Code
- Commercial Code
- Social Security Code
- And more...

### Regional Codes (19)
- Flemish Regional Laws
- Walloon Regional Laws
- Brussels Regional Laws
- And more...

### Community Codes (4)
- French Community Laws
- Flemish Community Laws
- German Community Laws
- And more...

## 🔧 Configuration

### Environment Variables

```bash
# Database settings
LEGAL_DB_PATH=offline_legal_knowledge/database/legal_codes.db

# Search settings
SEARCH_INDEX_PATH=offline_legal_knowledge/metadata/search_index.json

# Processing settings
MAX_WORKERS=4
CHUNK_SIZE=1000
```

### Customization

You can modify the processing parameters in `legal_content_processor.py`:

```python
# Adjust processing settings
MAX_ARTICLES_PER_CODE = 1000
MIN_KEYWORD_LENGTH = 3
TOPIC_CLUSTERING_THRESHOLD = 0.7
```

## 🛠️ Troubleshooting

### Common Issues

1. **PDF Download Fails**
   ```bash
   # Check internet connection
   curl -I https://www.ejustice.just.fgov.be
   
   # Retry with different user agent
   # Edit offline_legal_knowledge_downloader.py
   ```

2. **Processing Errors**
   ```bash
   # Check available memory
   free -h
   
   # Reduce parallel processing
   # Set MAX_WORKERS=1 in legal_content_processor.py
   ```

3. **Search Not Working**
   ```bash
   # Verify database exists
   ls -la offline_legal_knowledge/database/
   
   # Rebuild search index
   python3 legal_content_processor.py
   ```

### Logs and Debugging

```bash
# View processing logs
tail -f offline_legal_knowledge/logs/processing.log

# Check database integrity
sqlite3 offline_legal_knowledge/database/legal_codes.db ".tables"
```

## 📈 Performance

### Storage Requirements
- **Total Size:** 306 MB
- **PDFs:** 68.5 MB
- **Database:** 33 MB
- **Search Index:** 7.3 MB
- **Metadata:** 350 KB

### Search Performance
- **Average Query Time:** < 100ms
- **Index Size:** 7.3 MB
- **Supported Queries:** Full-text, semantic, keyword

## 🔄 Updates and Maintenance

### Updating Legal Codes

```bash
# Run complete update
python3 setup_offline_legal_knowledge.py --update

# Or update specific components
python3 justel_scraper.py --update
python3 offline_legal_knowledge_downloader.py --update
```

### Backup and Restore

```bash
# Create backup
tar -czf legal_knowledge_backup_$(date +%Y%m%d).tar.gz offline_legal_knowledge/

# Restore from backup
tar -xzf legal_knowledge_backup_20250817.tar.gz
```

## 🎉 Success Indicators

When setup is complete, you should see:

1. ✅ **Directory Structure:**
   ```
   offline_legal_knowledge/
   ├── pdfs/ (40 files)
   ├── content/ (40 files)
   ├── database/ (legal_codes.db)
   └── metadata/ (processing_summary.json)
   ```

2. ✅ **Web Interface:**
   - Research page shows "Status: Available"
   - Statistics display correctly
   - Search returns results

3. ✅ **API Responses:**
   ```json
   {
     "total_codes": 40,
     "total_articles": 15741,
     "categories": 9,
     "topics": 290
   }
   ```

## 🆘 Support

If you encounter issues:

1. **Check the logs:** `offline_legal_knowledge/logs/`
2. **Verify prerequisites:** All Python packages installed
3. **Check disk space:** Ensure 500MB+ available
4. **Review network:** Internet required for initial download

## 📚 Additional Resources

- [OFFLINE_LEGAL_RESEARCH_GUIDE.md](OFFLINE_LEGAL_RESEARCH_GUIDE.md) - Detailed technical guide
- [BELGIAN_LEGAL_RESEARCH_INTEGRATION.md](BELGIAN_LEGAL_RESEARCH_INTEGRATION.md) - Integration overview
- [Justel Official Database](https://www.ejustice.just.fgov.be) - Source of legal codes

---

**🎯 Your offline Belgian legal knowledge base is now ready for production use!** 