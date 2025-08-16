# Query History & Session Management Features

## 🎯 Overview

The Secure Offline Legal Assistant now includes comprehensive query history and session management capabilities. This feature enables lawyers to maintain persistent records of all their legal research queries, export conversations for client records, and analyze their usage patterns.

## 📚 Key Features

### 1. Persistent Query Storage
- **Local SQLite Database**: All queries stored securely on your machine
- **Automatic Saving**: Every question and answer automatically saved
- **Rich Metadata**: Includes sources, filters, processing time, and timestamps
- **No Cloud Dependencies**: Complete privacy and data sovereignty

### 2. Session Management
- **Automatic Sessions**: Sessions start when you launch the application
- **Session Tracking**: Each session has unique ID and metadata
- **Filter Association**: Sessions remember which filters were used
- **Session Summary**: View session statistics and query count

### 3. Search Through History
- **Full-Text Search**: Search through questions and answers
- **Session Filtering**: Search within specific sessions
- **Keyword Matching**: Find relevant previous queries
- **Result Ranking**: Results sorted by relevance and recency

### 4. PDF Export Capabilities
- **Session Export**: Export complete conversation history
- **Search Results Export**: Export filtered search results
- **Statistics Export**: Export usage analytics and patterns
- **Professional Formatting**: Clean, legal-document ready PDFs

## 🚀 How to Use

### Accessing History Features

**In the main application, use these commands:**

```
Ask a legal question: history    # Access history management
Ask a legal question: export     # Access export options
Ask a legal question: stats      # View usage statistics
```

### History Management Menu

When you type `history`, you'll see:

```
📚 HISTORY MANAGEMENT
========================================
1. View current session
2. Search query history
3. List all sessions
4. View session summary
5. Back to main menu

Enter your choice (1-5):
```

**Options Explained:**
- **View current session**: See all queries in your current session
- **Search query history**: Search through all previous queries
- **List all sessions**: See all your past sessions with summaries
- **View session summary**: Get detailed stats about current session

### Export Menu

When you type `export`, you'll see:

```
📄 EXPORT OPTIONS
==============================
1. Export current session to PDF
2. Export search results to PDF
3. Export usage statistics to PDF
4. Back to main menu

Enter your choice (1-4):
```

**Export Options:**
- **Current session**: Export all queries from your current session
- **Search results**: Export results from a specific search term
- **Usage statistics**: Export comprehensive usage analytics

## 📊 Data Structure

### Session Information
Each session includes:
- **Session ID**: Unique identifier (8 characters)
- **Start Time**: When the session began
- **End Time**: When the session ended (or "Active")
- **Total Queries**: Number of questions asked
- **Filters Used**: Any filters applied during the session
- **Status**: Active or ended

### Query Information
Each query includes:
- **Question**: The exact question asked
- **Answer**: The AI-generated response
- **Sources**: List of source documents with metadata
- **Filters Applied**: Any filters used for the query
- **Query Time**: Exact timestamp
- **Processing Time**: How long the query took

### Source Metadata
For each source document:
- **Source File**: Original PDF filename
- **Page Number**: Page where information was found
- **Document Type**: contracts, case_law, statutes, etc.
- **Jurisdiction**: federal, state, local, international
- **Content Preview**: First 200 characters of the source

## 📄 PDF Export Features

### Session Export Format
Exported session PDFs include:
- **Title Page**: Session information and metadata
- **Session Summary**: Start time, filters, query count
- **Query History**: All questions and answers with timestamps
- **Source Citations**: Document references for each answer
- **Processing Times**: Performance metrics for each query

### Search Results Export Format
Exported search PDFs include:
- **Search Metadata**: Search term and result count
- **Export Information**: Date and time of export
- **Matching Queries**: All queries containing the search term
- **Cross-Session Results**: Results from multiple sessions
- **Source Information**: Document references for each result

### Statistics Export Format
Exported statistics PDFs include:
- **Usage Metrics**: Total queries, sessions, averages
- **Filter Analysis**: Most commonly used filters
- **Performance Data**: Processing time statistics
- **Trend Analysis**: Usage patterns over time

## 🔧 Technical Implementation

### Database Schema
The SQLite database uses two main tables:

**Sessions Table:**
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_queries INTEGER DEFAULT 0,
    filters_used TEXT,
    status TEXT DEFAULT 'active'
)
```

**Queries Table:**
```sql
CREATE TABLE queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources TEXT,
    filters_applied TEXT,
    query_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_time REAL,
    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
)
```

### File Storage
- **Database**: `legal_assistant.db` (SQLite file)
- **Exports**: `exports/` directory (PDF files)
- **Automatic Creation**: Files created when first needed

### Security Features
- **Local Storage Only**: No data transmitted externally
- **SQLite Encryption**: Database can be encrypted if needed
- **File Permissions**: Standard file system security
- **No Cloud Sync**: Complete data sovereignty

## 📈 Usage Analytics

### Available Statistics
- **Total Queries**: Number of questions asked
- **Total Sessions**: Number of research sessions
- **Average Queries per Session**: Usage patterns
- **Most Common Filters**: Popular filter combinations
- **Processing Times**: Performance metrics

### Example Statistics Output
```
📈 Usage Statistics
==============================
Total Queries: 47
Total Sessions: 8
Avg Queries per Session: 5.88

Most Common Filters:
  - document_type: case_law: 23 times
  - jurisdiction: federal: 15 times
  - document_type: contracts: 12 times
==============================
```

## 🎯 Use Cases

### Legal Research Workflow
1. **Start Session**: Launch application (session starts automatically)
2. **Ask Questions**: All queries automatically saved
3. **Apply Filters**: Filter by document type, jurisdiction, etc.
4. **Review History**: Search through previous research
5. **Export Results**: Create PDF for client or court records
6. **End Session**: Close application (session ends automatically)

### Client Documentation
- Export complete research sessions for client files
- Include source citations and metadata
- Professional PDF formatting for legal documents
- Maintain audit trail of research process

### Research Continuity
- Resume research from previous sessions
- Find relevant previous queries quickly
- Track research progress over time
- Maintain context across multiple sessions

### Performance Analysis
- Monitor query processing times
- Identify most useful filter combinations
- Track research efficiency
- Optimize workflow based on patterns

## 🔒 Privacy & Security

### Data Protection
- **Local Storage**: All data remains on your machine
- **No Network Access**: Zero external data transmission
- **Client Confidentiality**: Sensitive research stays private
- **Audit Trail**: Complete record of all research activity

### Compliance Features
- **Data Sovereignty**: Complete control over all data
- **Export Capability**: Easy data portability
- **Deletion Options**: Remove sessions when needed
- **Backup Friendly**: Standard file-based storage

## 🛠️ Advanced Features

### Session Management
- **Automatic Cleanup**: Remove old sessions (configurable)
- **Session Recovery**: Resume interrupted sessions
- **Filter Persistence**: Remember filter preferences
- **Cross-Session Search**: Search across all sessions

### Export Customization
- **Multiple Formats**: PDF export with professional styling
- **Custom Filenames**: Automatic naming with timestamps
- **Batch Export**: Export multiple sessions at once
- **Selective Export**: Choose specific queries to export

### Search Capabilities
- **Full-Text Search**: Search questions and answers
- **Metadata Search**: Search by document type, jurisdiction
- **Date Range Search**: Search within time periods
- **Filter-Based Search**: Search within specific filter sets

## 💡 Best Practices

### Session Organization
- **Clear Session Purpose**: Use sessions for specific research topics
- **Regular Exports**: Export important sessions regularly
- **Session Cleanup**: Remove old sessions periodically
- **Backup Strategy**: Regular backups of the database

### Search Optimization
- **Use Specific Terms**: More specific searches yield better results
- **Combine Keywords**: Use multiple search terms
- **Filter Results**: Use session filters to narrow searches
- **Review Context**: Check timestamps and session context

### Export Strategy
- **Client Records**: Export sessions for client documentation
- **Court Filings**: Export relevant research for legal filings
- **Research Notes**: Use exports for personal research notes
- **Collaboration**: Share exports with legal team members

---

**💡 Tip**: The history system works automatically in the background. Simply use the application normally, and all your queries will be saved. Use the `history` and `export` commands when you need to review or share your research. 