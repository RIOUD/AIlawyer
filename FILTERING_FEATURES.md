# Advanced Filtering Features

## 🎯 Overview

The Secure Offline Legal Assistant now includes advanced filtering capabilities that allow you to narrow down search results based on document metadata. This feature enhances the precision of legal research by enabling targeted queries across specific document types, jurisdictions, and time periods.

## 🔍 Available Filters

### 1. Document Type Filter
Filter by the type of legal document:
- **contracts**: Employment agreements, NDAs, service contracts, etc.
- **case_law**: Court decisions, opinions, rulings, judgments
- **statutes**: Laws, regulations, codes, ordinances
- **briefs**: Legal briefs, motions, petitions, complaints
- **legal_opinions**: Advisory opinions, counsel opinions

### 2. Jurisdiction Filter
Filter by the legal jurisdiction:
- **federal**: United States federal law, Supreme Court decisions
- **state**: State-specific laws and regulations
- **local**: County, city, and municipal ordinances
- **international**: Treaties, international agreements

### 3. Date Range Filter
Filter by document date or year:
- **Start Date**: Documents from this date forward
- **End Date**: Documents up to this date
- **Year Only**: Documents from a specific year
- **Date Formats**: YYYY-MM-DD, YYYY, MM/DD/YYYY

### 4. Source Filter
Filter by document recency:
- **all**: All documents (default)
- **recent**: Documents modified in the last 30 days
- **archived**: Documents older than 30 days

## 🚀 How to Use Filters

### Setting Filters
1. Start the application: `python app.py`
2. Type `filters` to access the filter menu
3. Follow the prompts to set your desired filters
4. Ask your legal question

### Example Usage

```
Ask a legal question: filters

📋 Document Type:
   1. contracts
   2. case_law
   3. statutes
   4. briefs
   5. legal_opinions
   Enter number or 'all': 2

🏛️  Jurisdiction:
   1. federal
   2. state
   3. local
   4. international
   Enter number or 'all': 1

📁 Source:
   1. all
   2. recent
   3. archived
   Enter number or 'all': 2

📅 Date Range (optional):
   Start date (YYYY-MM-DD or YYYY): 2023
   End date (YYYY-MM-DD or YYYY): 2024

✅ Filters updated!

Ask a legal question: What are the privacy rights in digital surveillance?
```

### Filter Commands

- **`filters`** - Set new search filters
- **`help`** - Show available filter options
- **`clear`** - Clear all active filters
- **`exit`** - Quit the application

## 📊 Metadata Extraction

The system automatically extracts metadata from your documents during ingestion:

### Filename Analysis
- Detects document type from filename keywords
- Identifies jurisdiction from filename patterns
- Extracts dates from filename format

### Content Analysis
- Analyzes document content for type indicators
- Identifies jurisdiction references in text
- Extracts dates mentioned in the document

### File System Metadata
- Records file creation and modification dates
- Tracks document source information
- Maintains audit trail of document processing

## 🔧 Technical Implementation

### Metadata Storage
- All metadata is stored locally in ChromaDB
- No external data transmission
- Secure, encrypted storage

### Filter Application
- Filters are applied during document retrieval
- Uses ChromaDB's native filtering capabilities
- Maintains search relevance while filtering

### Performance Optimization
- Efficient metadata indexing
- Fast filter application
- Minimal impact on search speed

## 📋 Example Filter Combinations

### Federal Case Law Research
```
Document Type: case_law
Jurisdiction: federal
Date Range: 2020-2024
Source: all
```
**Use Case**: Research recent federal court decisions on constitutional issues

### State Contract Analysis
```
Document Type: contracts
Jurisdiction: state
Date Range: 2024
Source: recent
```
**Use Case**: Review recent state-specific employment contracts

### Local Regulatory Compliance
```
Document Type: statutes
Jurisdiction: local
Date Range: 2023-2024
Source: all
```
**Use Case**: Check recent local ordinances and regulations

### International Treaty Research
```
Document Type: statutes
Jurisdiction: international
Date Range: 2021-2024
Source: all
```
**Use Case**: Research international trade agreements and treaties

## 🧪 Testing the Features

### Quick Test Setup
1. Run the demo: `python test_filters.py`
2. Process documents: `python ingest.py`
3. Start application: `python app.py`
4. Test filters: Type `filters` and experiment

### Sample Test Documents
The demo creates test documents with known metadata:
- `federal_case_law_2023.pdf` - Federal case law from 2023
- `california_contract_2024.pdf` - State contract from 2024
- `local_ordinance_2022.pdf` - Local ordinance from 2022
- `international_treaty_2021.pdf` - International treaty from 2021

### Test Questions
Try these questions with different filter combinations:
- "What are the privacy rights in digital surveillance?"
- "What are the employment contract requirements?"
- "What are the local business regulations?"
- "What are the international trade provisions?"

## ⚙️ Configuration

### Customizing Filter Patterns
Edit `config.py` to customize:
- Document type detection patterns
- Jurisdiction identification rules
- Date extraction formats
- Filter options and defaults

### Adding New Filter Types
1. Add patterns to `DOCUMENT_TYPE_PATTERNS`
2. Update `JURISDICTION_PATTERNS` if needed
3. Modify `get_filter_options()` function
4. Update the filter application logic

## 🔒 Security Features

### Privacy Protection
- All filtering happens locally
- No metadata transmitted externally
- Secure local storage only

### Data Integrity
- Input validation for all filters
- Error handling for invalid filter combinations
- Graceful fallback to unfiltered search

## 📈 Benefits

### Enhanced Precision
- Target specific document types
- Focus on relevant jurisdictions
- Filter by time periods

### Improved Efficiency
- Faster, more relevant results
- Reduced noise in search results
- Better source verification

### Professional Workflow
- Supports legal research methodologies
- Enables systematic document review
- Facilitates compliance checking

## 🎯 Best Practices

### Filter Strategy
1. Start with broad filters and narrow down
2. Use date ranges to focus on current law
3. Combine document type and jurisdiction for precision
4. Clear filters when switching research topics

### Query Optimization
1. Use specific legal terms in questions
2. Combine filters with targeted keywords
3. Review source metadata for relevance
4. Adjust filters based on initial results

---

**💡 Tip**: The filtering system works best when you have a diverse collection of legal documents with clear metadata. The more documents you have, the more powerful the filtering becomes. 