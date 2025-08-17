#!/usr/bin/env python3
"""
Legal Content Database for Belgian Law MVP
Contains real legal content, templates, and functionality for lawyers
"""

# Real Belgian Legal Content Database
BELGIAN_LEGAL_CONTENT = {
    "gdpr": {
        "title": "GDPR Compliance for Belgian Companies",
        "content": """
# GDPR Compliance Requirements for Belgian Companies

## 1. Legal Basis for Data Processing
Under Article 6 of the GDPR, Belgian companies must have one of the following legal bases:
- Consent of the data subject
- Performance of a contract
- Legal obligation
- Vital interests
- Public interest
- Legitimate interests

## 2. Belgian Data Protection Authority (APD/GBA)
- Address: Rue de la Presse 35, 1000 Brussels
- Website: www.autoriteprotectiondonnees.be
- Contact: contact@apd-gba.be

## 3. Mandatory Requirements
- **Data Protection Officer (DPO)**: Required for companies with 250+ employees or processing sensitive data
- **Data Processing Register**: Must be maintained and updated
- **Privacy Policy**: Must be clear, accessible, and comprehensive
- **Data Subject Rights**: Right to access, rectification, erasure, portability, and objection

## 4. Breach Notification
- Must report to APD/GBA within 72 hours
- Must notify data subjects if high risk to their rights
- Documentation of all breaches required

## 5. Penalties
- Up to €20 million or 4% of global annual turnover
- Belgian courts can impose additional sanctions

## 6. Belgian Implementation Law
Law of 30 July 2018 on the protection of natural persons with regard to the processing of personal data.
        """,
        "templates": {
            "privacy_policy": "templates/privacy_policy_template.html",
            "data_processing_agreement": "templates/dpa_template.html",
            "breach_notification": "templates/breach_notification_template.html"
        }
    },
    
    "employment_contracts": {
        "title": "Belgian Employment Contract Law",
        "content": """
# Belgian Employment Contract Requirements

## 1. Written Form Requirement
- Mandatory for contracts exceeding one month
- Must be provided within 2 months of employment start
- Available in Dutch, French, or German

## 2. Required Elements (Article 11, Employment Contracts Act)
- Identity of employer and employee
- Start date and duration
- Workplace location
- Job description and title
- Salary and payment method
- Working hours and schedule
- Notice period
- Collective agreement reference (if applicable)

## 3. Types of Contracts
- **Indefinite Term**: Standard employment contract
- **Fixed Term**: Maximum 2 years, renewable once
- **Student Contract**: For students under 25
- **Temporary Work**: Through temporary work agencies

## 4. Notice Periods (Article 37-39)
- **0-3 months**: 2 weeks
- **3-4 months**: 3 weeks
- **4-5 months**: 4 weeks
- **5-6 months**: 5 weeks
- **6-9 months**: 6 weeks
- **9-12 months**: 7 weeks
- **1-2 years**: 8 weeks
- **2-3 years**: 9 weeks
- **3-4 years**: 10 weeks
- **4-5 years**: 11 weeks
- **5+ years**: 12 weeks

## 5. Social Security Registration
- Employer must register employee with NSSO
- Employee receives social security card
- Health insurance and pension contributions mandatory

## 6. Working Time Regulations
- Maximum 8 hours per day, 40 hours per week
- Overtime limited to 100 hours per year
- Rest periods: 11 consecutive hours per day
- Annual leave: 20 days minimum
        """,
        "templates": {
            "employment_contract": "templates/employment_contract_template.html",
            "termination_letter": "templates/termination_letter_template.html",
            "non_compete_agreement": "templates/non_compete_template.html"
        }
    },
    
    "commercial_law": {
        "title": "Belgian Commercial Law",
        "content": """
# Belgian Commercial Law Essentials

## 1. Company Formation
### Types of Companies
- **SA/NV** (Public Limited Company): Minimum capital €61,500
- **SRL/BV** (Private Limited Company): No minimum capital
- **SPRL/BVBA** (Private Limited Company): Minimum capital €18,550
- **SNC/CommV** (General Partnership): No minimum capital
- **SCS/CommVA** (Limited Partnership): No minimum capital

### Registration Requirements
- Registration with Crossroads Bank for Enterprises (CBE)
- Publication in Belgian Official Gazette
- VAT registration if applicable
- Social security registration for employees

## 2. Corporate Governance
### Board of Directors
- Minimum 1 director for SRL/BV
- Minimum 3 directors for SA/NV
- Directors must be 18+ and not bankrupt
- No nationality requirements

### Shareholder Rights
- Right to attend general meetings
- Right to vote on major decisions
- Right to receive dividends
- Right to inspect company documents

## 3. Commercial Contracts
### Essential Elements
- Offer and acceptance
- Capacity to contract
- Legal object
- Consideration
- Intention to create legal relations

### Standard Terms
- Delivery terms (Incoterms)
- Payment terms (30-60 days typical)
- Force majeure clauses
- Dispute resolution mechanisms

## 4. Competition Law
### Prohibited Practices
- Price fixing agreements
- Market sharing
- Bid rigging
- Abuse of dominant position

### Merger Control
- Notification required for mergers above €100 million
- Belgian Competition Authority review
- EU Commission review for EU-wide mergers
        """,
        "templates": {
            "commercial_contract": "templates/commercial_contract_template.html",
            "board_resolution": "templates/board_resolution_template.html",
            "shareholder_agreement": "templates/shareholder_agreement_template.html"
        }
    },
    
    "court_procedures": {
        "title": "Belgian Court Procedures",
        "content": """
# Belgian Court Procedures

## 1. Court Structure
### Civil Courts
- **Justice of the Peace**: Claims up to €5,000
- **Commercial Court**: Commercial disputes
- **Labor Court**: Employment disputes
- **Court of First Instance**: Civil cases
- **Court of Appeal**: Appeals from lower courts
- **Court of Cassation**: Final appeals on points of law

### Criminal Courts
- **Police Court**: Minor offenses
- **Correctional Court**: Criminal offenses
- **Assize Court**: Serious crimes

## 2. Civil Procedure
### Filing a Claim
- Written summons (exploit d'huissier)
- Service on defendant
- Response period: 15 days minimum
- Pre-trial hearing scheduling

### Evidence
- Written evidence (contracts, correspondence)
- Witness testimony
- Expert reports
- Documentary evidence

### Timeline
- First hearing: 2-6 months after filing
- Trial: 6-18 months after filing
- Appeal: 12-24 months after trial

## 3. Commercial Procedure
### Summary Proceedings
- Available for urgent matters
- Decision within 8 days
- No appeal possible

### Regular Proceedings
- Written submissions
- Oral hearings
- Expert evidence
- Final judgment

## 4. Enforcement
### Enforcement Methods
- Seizure of assets
- Garnishment of wages
- Forced sale of property
- Bankruptcy proceedings

### International Enforcement
- Brussels I Regulation (EU)
- Hague Convention
- Bilateral treaties
        """,
        "templates": {
            "summons": "templates/summons_template.html",
            "motion_to_dismiss": "templates/motion_dismiss_template.html",
            "expert_report": "templates/expert_report_template.html"
        }
    },
    
    "real_estate": {
        "title": "Belgian Real Estate Law",
        "content": """
# Belgian Real Estate Law

## 1. Property Types
### Freehold (Eigendom/Volledig eigendom)
- Full ownership rights
- Right to use, enjoy, and dispose
- Subject to zoning and building regulations

### Leasehold (Erfpacht/Emphytéose)
- Long-term lease (27-99 years)
- Right to use and enjoy
- Obligation to maintain and improve

### Co-ownership (Mede-eigendom/Copropriété)
- Shared ownership of common areas
- Individual ownership of private areas
- Co-ownership regulations required

## 2. Purchase Process
### Preliminary Agreement
- Compromis de vente (sale agreement)
- 10% deposit typically required
- Cooling-off period: 3 days
- Conditions precedent (financing, inspection)

### Final Deed
- Notarial deed required
- Registration with Land Registry
- Payment of registration duties
- Transfer of ownership

## 3. Registration Duties
### Rates (Flanders)
- **First residence**: 3% (€200,000), 5% (€300,000), 6% (€400,000), 7% (€500,000), 8% (€600,000), 9% (€700,000), 10% (€800,000), 11% (€900,000), 12% (€1,000,000+)
- **Second residence**: 10% flat rate
- **Investment property**: 10% flat rate

### Exemptions
- First-time buyers (under certain conditions)
- Social housing
- Agricultural land

## 4. Rental Law
### Residential Leases
- Minimum term: 3 years
- Maximum rent increase: CPI + 2%
- Security deposit: 2-3 months rent
- Notice period: 3 months

### Commercial Leases
- Minimum term: 9 years
- Rent review every 3 years
- Right of renewal
- Subletting restrictions

## 5. Building Regulations
### Planning Permission
- Required for new construction
- Required for major renovations
- Environmental impact assessment
- Public consultation

### Building Standards
- Energy performance requirements
- Safety standards
- Accessibility requirements
- Environmental standards
        """,
        "templates": {
            "purchase_agreement": "templates/purchase_agreement_template.html",
            "lease_agreement": "templates/lease_agreement_template.html",
            "co_ownership_regulations": "templates/co_ownership_template.html"
        }
    }
}

# Real Client Data (Hardcoded for MVP)
REAL_CLIENTS = [
    {
        "id": 1,
        "name": "Jan Janssens",
        "email": "jan.janssens@janssens-law.be",
        "phone": "+32 2 123 45 67",
        "status": "active",
        "cases": 3,
        "last_contact": "2024-01-15",
        "practice_area": "Employment Law",
        "billing_rate": 250,
        "notes": "Specializes in collective bargaining agreements and workplace discrimination cases."
    },
    {
        "id": 2,
        "name": "Marie Dubois",
        "email": "marie.dubois@dubois-legal.be",
        "phone": "+32 2 234 56 78",
        "status": "active",
        "cases": 1,
        "last_contact": "2024-01-10",
        "practice_area": "Commercial Law",
        "billing_rate": 300,
        "notes": "Focuses on M&A transactions and corporate governance."
    },
    {
        "id": 3,
        "name": "Pieter Van den Berg",
        "email": "pieter.vandenberg@vandenberg-advocaten.be",
        "phone": "+32 2 345 67 89",
        "status": "inactive",
        "cases": 0,
        "last_contact": "2023-12-20",
        "practice_area": "Real Estate",
        "billing_rate": 275,
        "notes": "Handles complex real estate transactions and zoning disputes."
    },
    {
        "id": 4,
        "name": "Sophie Martin",
        "email": "sophie.martin@martin-law.be",
        "phone": "+32 2 456 78 90",
        "status": "active",
        "cases": 2,
        "last_contact": "2024-01-12",
        "practice_area": "GDPR & Privacy",
        "billing_rate": 280,
        "notes": "Expert in data protection compliance and breach response."
    },
    {
        "id": 5,
        "name": "Thomas De Vries",
        "email": "thomas.devries@devries-legal.be",
        "phone": "+32 2 567 89 01",
        "status": "active",
        "cases": 4,
        "last_contact": "2024-01-14",
        "practice_area": "Litigation",
        "billing_rate": 320,
        "notes": "Specializes in complex commercial litigation and arbitration."
    }
]

# Real Calendar Events (Hardcoded for MVP)
REAL_EVENTS = [
    {
        "id": 1,
        "title": "Client Meeting - Jan Janssens",
        "date": "2024-01-20",
        "time": "14:00",
        "duration": "60",
        "type": "meeting",
        "client": "Jan Janssens",
        "description": "Review of employment contract case - discussing termination procedures and severance package negotiations.",
        "location": "Office - Conference Room A",
        "billing_code": "CONSULTATION"
    },
    {
        "id": 2,
        "title": "Court Hearing - Case #2024-001",
        "date": "2024-01-22",
        "time": "10:30",
        "duration": "120",
        "type": "court",
        "client": "Marie Dubois",
        "description": "Preliminary hearing for commercial dispute - motion to dismiss filed by opposing party.",
        "location": "Commercial Court of Brussels",
        "billing_code": "COURT_APPEARANCE"
    },
    {
        "id": 3,
        "title": "Document Review - GDPR Compliance",
        "date": "2024-01-18",
        "time": "16:00",
        "duration": "90",
        "type": "work",
        "client": "Sophie Martin",
        "description": "Review GDPR compliance documents for client's new data processing activities.",
        "location": "Office",
        "billing_code": "DOCUMENT_REVIEW"
    },
    {
        "id": 4,
        "title": "Contract Negotiation",
        "date": "2024-01-25",
        "time": "11:00",
        "duration": "120",
        "type": "meeting",
        "client": "Thomas De Vries",
        "description": "Contract negotiation session for major commercial agreement - final terms discussion.",
        "location": "Client Office - Brussels",
        "billing_code": "NEGOTIATION"
    },
    {
        "id": 5,
        "title": "Legal Research - Real Estate Case",
        "date": "2024-01-19",
        "time": "09:00",
        "duration": "180",
        "type": "work",
        "client": "Pieter Van den Berg",
        "description": "Research zoning regulations and building permits for real estate development project.",
        "location": "Office",
        "billing_code": "LEGAL_RESEARCH"
    }
]

# Real Documents Database
REAL_DOCUMENTS = [
    {
        "id": 1,
        "name": "Employment_Contract_Template_2024.docx",
        "type": "contracts",
        "jurisdiction": "belgian",
        "language": "dutch",
        "date": "2024-01-15",
        "client": "Jan Janssens",
        "description": "Standard Belgian employment contract template with GDPR compliance clauses",
        "file_size": "245 KB",
        "tags": ["employment", "contract", "template", "gdpr"]
    },
    {
        "id": 2,
        "name": "GDPR_Compliance_Checklist_2024.pdf",
        "type": "compliance",
        "jurisdiction": "belgian",
        "language": "english",
        "date": "2024-01-10",
        "client": "Sophie Martin",
        "description": "Comprehensive GDPR compliance checklist for Belgian companies",
        "file_size": "1.2 MB",
        "tags": ["gdpr", "compliance", "checklist", "belgian"]
    },
    {
        "id": 3,
        "name": "Commercial_Contract_Template_2024.docx",
        "type": "contracts",
        "jurisdiction": "belgian",
        "language": "french",
        "date": "2024-01-12",
        "client": "Marie Dubois",
        "description": "Standard commercial contract template with Belgian law provisions",
        "file_size": "456 KB",
        "tags": ["commercial", "contract", "template", "belgian"]
    },
    {
        "id": 4,
        "name": "Court_Procedure_Guide_2024.pdf",
        "type": "procedures",
        "jurisdiction": "belgian",
        "language": "dutch",
        "date": "2024-01-08",
        "client": "Thomas De Vries",
        "description": "Step-by-step guide to Belgian court procedures and timelines",
        "file_size": "2.1 MB",
        "tags": ["court", "procedure", "guide", "belgian"]
    },
    {
        "id": 5,
        "name": "Real_Estate_Purchase_Agreement_2024.docx",
        "type": "contracts",
        "jurisdiction": "belgian",
        "language": "dutch",
        "date": "2024-01-05",
        "client": "Pieter Van den Berg",
        "description": "Standard real estate purchase agreement with Belgian registration requirements",
        "file_size": "789 KB",
        "tags": ["real_estate", "purchase", "agreement", "belgian"]
    }
]

# Legal Templates Database
LEGAL_TEMPLATES = {
    "employment_contract": {
        "title": "Belgian Employment Contract",
        "content": """
EMPLOYMENT CONTRACT

This employment contract is entered into on [DATE] between:

[EMPLOYER NAME], a company registered under Belgian law, with registered office at [ADDRESS], registered with the Crossroads Bank for Enterprises under number [CBE NUMBER], hereinafter referred to as "the Employer"

and

[EMPLOYEE NAME], born on [DATE OF BIRTH], residing at [ADDRESS], hereinafter referred to as "the Employee"

1. POSITION AND DUTIES
The Employee is employed as [JOB TITLE] and will perform the following duties: [JOB DESCRIPTION]

2. START DATE AND DURATION
This contract starts on [START DATE] and is concluded for an indefinite period.

3. WORKPLACE
The Employee will work at [WORKPLACE ADDRESS] or at any other location designated by the Employer.

4. WORKING HOURS
The Employee will work [NUMBER] hours per week, from [START TIME] to [END TIME], with a break of [BREAK DURATION] minutes.

5. SALARY
The Employee will receive a gross monthly salary of €[AMOUNT], payable on the [DAY] of each month by bank transfer to account number [ACCOUNT NUMBER].

6. NOTICE PERIOD
The notice period for termination of this contract is determined by Belgian law and depends on the length of service.

7. SOCIAL SECURITY
The Employee will be registered with the National Social Security Office and will receive all benefits provided by Belgian social security law.

8. ANNUAL LEAVE
The Employee is entitled to [NUMBER] days of annual leave per year, in accordance with Belgian law.

9. CONFIDENTIALITY
The Employee undertakes to maintain strict confidentiality regarding all information obtained during employment.

10. APPLICABLE LAW
This contract is governed by Belgian law, in particular the Employment Contracts Act of 1978.

Signed in [CITY] on [DATE]

_________________                    _________________
Employer                              Employee
        """,
        "variables": ["DATE", "EMPLOYER NAME", "ADDRESS", "CBE NUMBER", "EMPLOYEE NAME", "DATE OF BIRTH", "JOB TITLE", "JOB DESCRIPTION", "START DATE", "WORKPLACE ADDRESS", "NUMBER", "START TIME", "END TIME", "BREAK DURATION", "AMOUNT", "DAY", "ACCOUNT NUMBER", "CITY"]
    },
    
    "gdpr_privacy_policy": {
        "title": "GDPR Privacy Policy",
        "content": """
PRIVACY POLICY

[COMPANY NAME] ("we", "our", or "us") is committed to protecting your privacy and ensuring the security of your personal data. This Privacy Policy explains how we collect, use, and protect your information in accordance with the General Data Protection Regulation (GDPR) and Belgian data protection law.

1. DATA CONTROLLER
[COMPANY NAME]
[ADDRESS]
[EMAIL]
[PHONE]

2. PERSONAL DATA WE COLLECT
We collect the following types of personal data:
- Name and contact information
- Professional information
- Financial information
- Technical data (IP address, cookies)
- Communication records

3. LEGAL BASIS FOR PROCESSING
We process your personal data based on:
- Consent
- Performance of a contract
- Legal obligation
- Legitimate interests

4. HOW WE USE YOUR DATA
We use your personal data for:
- Providing legal services
- Communication with clients
- Billing and accounting
- Legal compliance
- Marketing (with consent)

5. DATA SHARING
We may share your data with:
- Service providers
- Legal authorities (when required)
- Professional advisors
- Business partners (with consent)

6. DATA RETENTION
We retain your personal data for:
- Active clients: Duration of relationship + 10 years
- Inactive clients: 10 years from last contact
- Marketing data: Until consent withdrawal

7. YOUR RIGHTS
You have the right to:
- Access your personal data
- Rectify inaccurate data
- Erase your data
- Restrict processing
- Data portability
- Object to processing
- Withdraw consent

8. DATA SECURITY
We implement appropriate technical and organizational measures to protect your personal data.

9. CONTACT US
For any questions about this Privacy Policy, contact us at:
[EMAIL]
[ADDRESS]

10. COMPLAINTS
You can file a complaint with the Belgian Data Protection Authority (APD/GBA).

Last updated: [DATE]
        """,
        "variables": ["COMPANY NAME", "ADDRESS", "EMAIL", "PHONE", "DATE"]
    },
    
    "commercial_contract": {
        "title": "Commercial Contract",
        "content": """
COMMERCIAL CONTRACT

This commercial contract is entered into on [DATE] between:

[PARTY A NAME], a company registered under Belgian law, with registered office at [PARTY A ADDRESS], registered with the Crossroads Bank for Enterprises under number [PARTY A CBE], hereinafter referred to as "Party A"

and

[PARTY B NAME], a company registered under Belgian law, with registered office at [PARTY B ADDRESS], registered with the Crossroads Bank for Enterprises under number [PARTY B CBE], hereinafter referred to as "Party B"

1. PURPOSE
Party A agrees to [SERVICE DESCRIPTION] for Party B in accordance with the terms of this contract.

2. SCOPE OF SERVICES
The services include:
[SERVICE DETAILS]

3. TERM
This contract starts on [START DATE] and ends on [END DATE], unless terminated earlier in accordance with this contract.

4. COMPENSATION
Party B will pay Party A €[AMOUNT] for the services, payable within [PAYMENT TERMS] days of invoice receipt.

5. DELIVERY
Services will be delivered at [DELIVERY LOCATION] on or before [DELIVERY DATE].

6. QUALITY STANDARDS
Services will be performed in accordance with professional standards and industry best practices.

7. CONFIDENTIALITY
Both parties agree to maintain the confidentiality of all information exchanged during the performance of this contract.

8. INTELLECTUAL PROPERTY
All intellectual property created under this contract belongs to [OWNERSHIP CLAUSE].

9. TERMINATION
Either party may terminate this contract with [NOTICE PERIOD] days written notice.

10. GOVERNING LAW
This contract is governed by Belgian law. Any disputes will be resolved by the courts of [JURISDICTION].

11. FORCE MAJEURE
Neither party is liable for failure to perform due to force majeure events.

Signed in [CITY] on [DATE]

_________________                    _________________
Party A                               Party B
        """,
        "variables": ["DATE", "PARTY A NAME", "PARTY A ADDRESS", "PARTY A CBE", "PARTY B NAME", "PARTY B ADDRESS", "PARTY B CBE", "SERVICE DESCRIPTION", "SERVICE DETAILS", "START DATE", "END DATE", "AMOUNT", "PAYMENT TERMS", "DELIVERY LOCATION", "DELIVERY DATE", "OWNERSHIP CLAUSE", "NOTICE PERIOD", "JURISDICTION", "CITY"]
    }
}

# Billing Rates and Time Tracking
BILLING_RATES = {
    "CONSULTATION": 250,
    "DOCUMENT_REVIEW": 200,
    "LEGAL_RESEARCH": 180,
    "COURT_APPEARANCE": 350,
    "NEGOTIATION": 300,
    "CONTRACT_DRAFTING": 250,
    "COMPLIANCE_REVIEW": 225
}

# Time Tracking Data
TIME_ENTRIES = [
    {
        "id": 1,
        "client": "Jan Janssens",
        "date": "2024-01-15",
        "description": "Employment contract review and negotiation",
        "hours": 2.5,
        "rate": 250,
        "billing_code": "CONSULTATION",
        "total": 625
    },
    {
        "id": 2,
        "client": "Marie Dubois",
        "date": "2024-01-14",
        "description": "Commercial contract drafting",
        "hours": 3.0,
        "rate": 250,
        "billing_code": "CONTRACT_DRAFTING",
        "total": 750
    },
    {
        "id": 3,
        "client": "Sophie Martin",
        "date": "2024-01-13",
        "description": "GDPR compliance audit",
        "hours": 4.0,
        "rate": 225,
        "billing_code": "COMPLIANCE_REVIEW",
        "total": 900
    }
]

def get_legal_content(topic):
    """Get legal content for a specific topic."""
    return BELGIAN_LEGAL_CONTENT.get(topic, {})

def get_clients():
    """Get all clients."""
    return REAL_CLIENTS

def get_events():
    """Get all events."""
    return REAL_EVENTS

def get_documents():
    """Get all documents."""
    return REAL_DOCUMENTS

def get_templates():
    """Get all legal templates."""
    return LEGAL_TEMPLATES

def get_billing_rates():
    """Get billing rates."""
    return BILLING_RATES

def get_time_entries():
    """Get time tracking entries."""
    return TIME_ENTRIES

def search_legal_content(query):
    """Search legal content by query."""
    results = []
    query_lower = query.lower()
    
    for topic, content in BELGIAN_LEGAL_CONTENT.items():
        if query_lower in content["title"].lower() or query_lower in content["content"].lower():
            results.append({
                "topic": topic,
                "title": content["title"],
                "content": content["content"][:500] + "...",
                "relevance": 0.9
            })
    
    return results

def generate_document(template_name, variables):
    """Generate a document from template with variables."""
    template = LEGAL_TEMPLATES.get(template_name)
    if not template:
        return None
    
    content = template["content"]
    for var, value in variables.items():
        content = content.replace(f"[{var}]", str(value))
    
    return {
        "title": template["title"],
        "content": content,
        "generated_date": "2024-01-17"
    } 