# Legal Document Template Features

## 🎯 Overview

The Legal Document Template system provides comprehensive template management for Belgian legal documents, including built-in templates, custom template uploads, document generation, and PDF export capabilities. This feature streamlines legal document creation and ensures consistency across legal procedures.

## 📋 Key Features

### 1. Template Library
- **Built-in Templates**: Comprehensive collection of Belgian legal document templates
- **Multi-language Support**: Dutch, French, and English templates
- **Jurisdiction Awareness**: Templates for federal, regional, and local levels
- **Category Organization**: Organized by document type and purpose

### 2. Document Generation
- **Variable Substitution**: Dynamic document generation with user-provided variables
- **Template Validation**: Automatic validation of required variables
- **Preview Functionality**: Preview templates with sample data
- **Batch Generation**: Generate multiple documents simultaneously

### 3. Custom Template Management
- **Template Upload**: Upload custom templates with full metadata
- **Template Import/Export**: Import and export templates in JSON format
- **Template Backup**: Backup and restore custom template collections
- **Template Search**: Search across all templates by name and description

### 4. PDF Export
- **Professional Formatting**: Legal document formatting with proper styling
- **Metadata Inclusion**: Include template information and variables used
- **Batch Export**: Export multiple documents to PDF simultaneously
- **Custom Styling**: Professional legal document appearance

## 🚀 How to Use

### Accessing Template Features

**In the main application, use this command:**

```
Ask a legal question: templates    # Access template management
```

### Template Management Menu

When you type `templates`, you'll see:

```
📋 TEMPLATE MANAGEMENT
========================================
1. Browse templates
2. Search templates
3. Generate document
4. Preview template
5. Upload custom template
6. Manage custom templates
7. Export template to PDF
8. Template statistics
9. Back to main menu

Enter your choice (1-9):
```

## 📚 Available Template Categories

### 1. Motions (Rechtszaken en Procedures)
- **Dagvaarding**: Summons for civil court proceedings
- **Conclusie**: Legal conclusions and pleadings
- **Requête**: French-language court requests

### 2. Contracts (Contracten en Overeenkomsten)
- **Arbeidsovereenkomst**: Employment contract template
- **Huurovereenkomst**: Rental agreement template

### 3. Legal Letters (Juridische Brieven)
- **Ingebrekestelling**: Formal notice of default
- **Mise en demeure**: French-language formal notice

### 4. Citation Formats (Citatieformaten)
- **Belgische Citatie**: Belgian legal citation format
- **European Citation**: European case law citation format

### 5. Contract Clauses (Contractclausules)
- **Geheimhoudingsclausule**: Confidentiality clause
- **Force Majeure Clause**: Force majeure clause

### 6. Forms (Formulieren)
- **Klachtformulier**: Complaint form template

## 🇧🇪 Belgian Legal Context

### Language Support
- **Dutch (nl)**: Primary language for Flemish legal documents
- **French (fr)**: Primary language for Walloon and Brussels documents
- **English (en)**: International and EU documents

### Jurisdiction Support
- **Federaal**: Federal level documents and procedures
- **Vlaams**: Flemish Community and Region
- **Waals**: Walloon Region
- **Brussels**: Brussels-Capital Region
- **EU**: European Union documents

### Template Examples

#### Dutch Employment Contract
```text
ARBEIDSOVEREENKOMST VOOR ONBEPAALDE TIJD

Tussen:
{werkgever_naam}, gevestigd te {werkgever_adres}, hierna te noemen "de werkgever",
en
{werknemer_naam}, wonende te {werknemer_adres}, hierna te noemen "de werknemer",

Wordt de volgende arbeidsovereenkomst gesloten:

ARTIKEL 1 - FUNCTIE
De werknemer wordt aangesteld als {functie} en zal werkzaam zijn op de afdeling {afdeling}.
```

#### French Court Request
```text
REQUÊTE

Au nom du Roi,

Le soussigné, {avocat_nom}, avocat à {lieu}, exerçant à {adresse}, 
cite {defendeur_nom}, demeurant à {defendeur_adresse}, à comparaître devant le 
{tribunal_nom} à {tribunal_lieu}, le {date} à {heure} heures.
```

## 🔧 Template Operations

### 1. Browse Templates
- View all available templates organized by category
- See template descriptions, languages, and jurisdictions
- Identify custom vs. built-in templates

### 2. Search Templates
- Search by template name or description
- Find templates across all categories
- Filter results by language or jurisdiction

### 3. Generate Document
- Select template by category and ID
- Provide required variables
- Generate complete legal document
- Option to export to PDF

### 4. Preview Template
- Preview template with sample data
- See how template looks with realistic values
- Understand template structure before use

### 5. Upload Custom Template
- Create custom templates with full metadata
- Define template variables and structure
- Organize by category and jurisdiction
- Support for all languages

### 6. Manage Custom Templates
- List all custom templates
- Delete unwanted templates
- Import templates from JSON files
- Export templates to files
- Backup and restore template collections

### 7. Export to PDF
- Generate professional PDF documents
- Include template metadata and variables
- Professional legal document formatting
- Automatic file naming and organization

### 8. Template Statistics
- View total template counts
- See language and jurisdiction distribution
- Monitor custom template usage
- Track template categories

## 📄 Document Generation Process

### Step-by-Step Workflow
```
1. Select Template Category
   ↓
2. Choose Specific Template
   ↓
3. Review Required Variables
   ↓
4. Provide Variable Values
   ↓
5. Generate Document
   ↓
6. Review Generated Content
   ↓
7. Export to PDF (Optional)
```

### Variable Validation
The system automatically validates:
- **Required Variables**: All required variables must be provided
- **Variable Types**: Variables are treated as strings for substitution
- **Missing Variables**: Clear error messages for missing variables
- **Extra Variables**: Warnings for unused variables

### Sample Variable Collection
```python
# Example variables for employment contract
variables = {
    'werkgever_naam': 'Bedrijf BVBA',
    'werkgever_adres': 'Industrieweg 15, 9000 Gent',
    'werknemer_naam': 'Anna Andersen',
    'werknemer_adres': 'Werknemerstraat 20, 3500 Hasselt',
    'functie': 'Advocaat',
    'afdeling': 'Burgerlijk Recht',
    'werkplaats': 'Gent',
    'brutoloon': '3.500',
    'loondatum': '25',
    'vakantiedagen': '20',
    'werkuren': '38',
    'werkdagen': '5',
    'proeftijd': '3',
    'opzegtermijn': '3',
    'plaats': 'Gent',
    'datum': '15 januari 2024'
}
```

## 📤 Custom Template Creation

### Template Structure
```json
{
    "name": "Template Name",
    "description": "Template description",
    "category": "template_category",
    "language": "nl",
    "jurisdiction": "federaal",
    "template": "Template content with {variables}",
    "variables": ["variable1", "variable2", "variable3"]
}
```

### Required Fields
- **name**: Template display name
- **description**: Template description
- **category**: Template category (motions, contracts, etc.)
- **language**: Language code (nl, fr, en)
- **jurisdiction**: Jurisdiction code
- **template**: Template content with variable placeholders
- **variables**: List of required variables

### Variable Placeholders
- Use `{variable_name}` format in template content
- Variables are case-sensitive
- All variables must be defined in the variables list
- Variables are substituted with provided values

## 📊 PDF Export Features

### Professional Formatting
- **Legal Document Styling**: Professional legal document appearance
- **Structured Layout**: Clear sections and formatting
- **Metadata Tables**: Template information and variables used
- **Professional Typography**: Legal document fonts and spacing

### Export Options
- **Single Document Export**: Export individual documents
- **Batch Export**: Export multiple documents simultaneously
- **Automatic Naming**: Generate filenames with timestamps
- **Directory Organization**: Organize exports by date and type

### PDF Content Structure
```
1. Document Title
2. Template Description
3. Metadata Table (Category, Language, Jurisdiction, Generation Date)
4. Variables Used Table
5. Generated Document Content
6. Professional Formatting
```

## 🛠️ Advanced Features

### Template Backup and Restore
- **Backup All Templates**: Create complete backup of custom templates
- **Restore from Backup**: Restore templates from backup files
- **Metadata Preservation**: Maintain all template metadata
- **Version Control**: Track template changes and versions

### Template Import/Export
- **JSON Format**: Standard JSON format for template exchange
- **Import Validation**: Validate imported templates
- **Export Options**: Export individual or multiple templates
- **Sharing Capabilities**: Share templates with colleagues

### Template Statistics
- **Usage Tracking**: Track template usage and popularity
- **Language Distribution**: Monitor language usage patterns
- **Jurisdiction Analysis**: Analyze jurisdiction-specific templates
- **Category Breakdown**: Understand template category distribution

## 🔒 Security and Privacy

### Local Storage
- **No External Dependencies**: All templates stored locally
- **Client Confidentiality**: No template data transmission
- **Complete Control**: Full control over template content
- **Professional Compliance**: Meets legal confidentiality requirements

### Data Protection
- **Template Encryption**: Templates stored securely
- **Access Control**: Local access only
- **No Cloud Storage**: No external template storage
- **Privacy Compliance**: Compliant with legal privacy requirements

## 📈 Performance Features

### Generation Speed
- **Fast Template Processing**: Quick document generation
- **Efficient Variable Substitution**: Optimized template processing
- **Batch Processing**: Efficient handling of multiple documents
- **Memory Optimization**: Efficient memory usage for large templates

### Scalability
- **Large Template Collections**: Handle extensive template libraries
- **Multiple Categories**: Support for unlimited template categories
- **Custom Template Growth**: Scale with custom template additions
- **Performance Monitoring**: Track template processing performance

## 💡 Best Practices

### Template Creation
- **Clear Variable Names**: Use descriptive variable names
- **Comprehensive Descriptions**: Provide detailed template descriptions
- **Proper Categorization**: Organize templates by logical categories
- **Language Consistency**: Maintain consistent language usage

### Document Generation
- **Variable Validation**: Always validate required variables
- **Template Preview**: Preview templates before generation
- **Professional Formatting**: Ensure professional document appearance
- **Regular Updates**: Keep templates current with legal requirements

### Template Management
- **Regular Backups**: Backup custom templates regularly
- **Version Control**: Track template changes and versions
- **Quality Assurance**: Review and validate template content
- **Documentation**: Maintain template documentation

## 🎯 Use Cases

### 1. Legal Practice Management
```
1. Create standard templates for common procedures
2. Generate documents quickly with variable substitution
3. Maintain consistency across all legal documents
4. Export professional PDF documents for clients
```

### 2. Contract Management
```
1. Use contract templates for various agreement types
2. Customize contracts with specific terms and conditions
3. Generate employment and rental agreements
4. Include standard legal clauses and provisions
```

### 3. Court Document Preparation
```
1. Generate summons and pleadings from templates
2. Create legal conclusions and court requests
3. Ensure proper formatting for court submission
4. Maintain professional legal document standards
```

### 4. Client Communication
```
1. Generate formal legal letters and notices
2. Create complaint forms and client documents
3. Maintain professional communication standards
4. Export documents for client records
```

## 🔧 Technical Implementation

### Template Storage
- **JSON Format**: Templates stored in structured JSON format
- **File-based Storage**: Templates stored as individual files
- **Directory Organization**: Organized by category and type
- **Metadata Preservation**: Complete template metadata storage

### Variable Processing
- **String Substitution**: Simple and efficient variable replacement
- **Validation Engine**: Comprehensive variable validation
- **Error Handling**: Clear error messages for validation failures
- **Type Safety**: Safe variable processing and substitution

### PDF Generation
- **ReportLab Integration**: Professional PDF generation
- **Legal Styling**: Legal document formatting and styling
- **Metadata Inclusion**: Complete document metadata
- **Professional Layout**: Professional legal document appearance

---

**💡 Tip**: The template system provides a comprehensive solution for legal document generation. Use built-in templates for common procedures and create custom templates for specialized needs. Always preview templates before generation and export to PDF for professional presentation. 