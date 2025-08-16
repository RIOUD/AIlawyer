#!/usr/bin/env python3
"""
Belgian Legal Document Generator

This script creates sample Belgian legal documents for testing the
Secure Offline Belgian Legal Assistant system.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_belgian_sample_documents():
    """Creates sample Belgian legal documents for testing."""
    
    # Ensure directory exists
    os.makedirs("source_documents", exist_ok=True)
    
    # Create sample documents with Belgian legal context
    documents = [
        {
            "filename": "vlaams_decreet_arbeid_2024.pdf",
            "title": "VLAAMS DECREET BETREFFENDE ARBEID (2024)",
            "content": """
            Dit Vlaams decreet regelt de arbeidsvoorwaarden en -omstandigheden in Vlaanderen.
            Het decreet bevat bepalingen over arbeidsovereenkomsten, werkgeversverplichtingen,
            en werknemersrechten binnen de Vlaamse bevoegdheid.
            
            Belangrijke artikelen:
            - Artikel 1: Definities en toepassingsgebied
            - Artikel 5: Verplichtingen van de werkgever
            - Artikel 12: Rechten van de werknemer
            - Artikel 18: Sancties en handhaving
            """,
            "expected_type": "wetboeken",
            "expected_jurisdiction": "vlaams",
            "expected_date": "2024"
        },
        {
            "filename": "arrest_hof_cassatie_2023.pdf",
            "title": "ARREST HOF VAN CASSATIE (2023)",
            "content": """
            Dit arrest van het Hof van Cassatie handelt over de interpretatie van artikel 544
            van het Burgerlijk Wetboek betreffende eigendom. Het hof oordeelt dat eigendom
            het recht is om over een zaak te beschikken op de meest absolute wijze.
            
            Belangrijke overwegingen:
            - Eigendom omvat het recht van gebruik en genot
            - Beperkingen kunnen worden opgelegd door wet of overeenkomst
            - Eigendom kan worden beperkt door rechten van derden
            - De eigenaar heeft het recht om zijn eigendom te verdedigen
            """,
            "expected_type": "jurisprudentie",
            "expected_jurisdiction": "federaal",
            "expected_date": "2023"
        },
        {
            "filename": "brussels_ordonnantie_handel_2022.pdf",
            "title": "BRUSSELSE ORDONNANTIE BETREFFENDE HANDEL (2022)",
            "content": """
            Deze Brusselse ordonnantie regelt de handelsactiviteiten in het Brussels
            Hoofdstedelijk Gewest. Zij bevat bepalingen over handelsvergunningen,
            openingstijden, en handelsreglementering.
            
            Hoofdbepalingen:
            - Vergunningsplicht voor handelsactiviteiten
            - Regeling van openingstijden
            - Handhaving en sancties
            - Overgangsbepalingen
            """,
            "expected_type": "wetboeken",
            "expected_jurisdiction": "brussels",
            "expected_date": "2022"
        },
        {
            "filename": "arbeidsovereenkomst_model_2024.pdf",
            "title": "MODEL ARBEIDSOVEREENKOMST (2024)",
            "content": """
            Dit model van arbeidsovereenkomst is gebaseerd op de bepalingen van het
            Arbeidsovereenkomstenbesluit van 1945 en de daaropvolgende wetgeving.
            
            Belangrijke clausules:
            - Identificatie van werkgever en werknemer
            - Functieomschrijving en plaats van tewerkstelling
            - Arbeidsvoorwaarden en vergoeding
            - Duur van de overeenkomst
            - Opzegtermijnen en -voorwaarden
            """,
            "expected_type": "contracten",
            "expected_jurisdiction": "federaal",
            "expected_date": "2024"
        },
        {
            "filename": "conclusie_vordering_2024.pdf",
            "title": "CONCLUSIE TOT VORDERING (2024)",
            "content": """
            Deze conclusie tot vordering wordt ingediend bij de rechtbank van eerste
            aanleg te Brussel in het kader van een geschil betreffende een
            arbeidsovereenkomst.
            
            Vorderingen:
            - Verklaring van nietigheid van de opzegging
            - Toekenning van een schadevergoeding
            - Veroordeling in de proceskosten
            - Alle andere nuttige maatregelen
            """,
            "expected_type": "advocatenstukken",
            "expected_jurisdiction": "federaal",
            "expected_date": "2024"
        },
        {
            "filename": "eu_richtlijn_privacy_2021.pdf",
            "title": "EU-RICHTLIJN PRIVACY EN GEGEVENSBESCHERMING (2021)",
            "content": """
            Deze Europese richtlijn regelt de bescherming van persoonsgegevens binnen
            de Europese Unie. Zij bevat bepalingen over de verwerking van
            persoonsgegevens en de rechten van betrokkenen.
            
            Kernbeginselen:
            - Rechtmatigheid, behoorlijkheid en transparantie
            - Doelbinding en minimale gegevensverwerking
            - Juistheid en actualiteit
            - Integriteit en vertrouwelijkheid
            """,
            "expected_type": "wetboeken",
            "expected_jurisdiction": "eu",
            "expected_date": "2021"
        }
    ]
    
    # Create each test document
    for doc_info in documents:
        filename = f"source_documents/{doc_info['filename']}"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title = Paragraph(doc_info['title'], styles['Heading1'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Add content
        content = Paragraph(doc_info['content'], styles['Normal'])
        story.append(content)
        
        # Build the PDF
        doc.build(story)
        
        print(f"✅ Created Belgian document: {doc_info['filename']}")
        print(f"   Expected type: {doc_info['expected_type']}")
        print(f"   Expected jurisdiction: {doc_info['expected_jurisdiction']}")
        print(f"   Expected date: {doc_info['expected_date']}")
        print()


def test_belgian_filtering_demo():
    """Demonstrates the Belgian filtering capabilities."""
    print("🧪 BELGIAN LEGAL ASSISTANT - FILTERING DEMO")
    print("=" * 60)
    
    print("\n1. Creating Belgian legal documents...")
    create_belgian_sample_documents()
    
    print("\n2. Running ingestion with Belgian metadata extraction...")
    print("   Run: python ingest.py")
    print("   This will extract Belgian-specific metadata from the documents")
    
    print("\n3. Testing Belgian filters in the application...")
    print("   Run: python app.py")
    print("   Then try these commands:")
    print("   - Type 'filters' to set Belgian-specific filters")
    print("   - Type 'help' to see Belgian legal context options")
    print("   - Type 'clear' to clear all filters")
    
    print("\n4. Example Belgian filter combinations to test:")
    print("   - Document type: jurisprudentie")
    print("   - Jurisdiction: federaal")
    print("   - Date range: 2023-2024")
    print("   - Language: nl (Dutch)")
    
    print("\n5. Sample Belgian legal questions to test:")
    print("   - 'Wat zijn de rechten van een werknemer bij een arbeidsovereenkomst?'")
    print("   - 'Hoe wordt eigendom gedefinieerd volgens het Burgerlijk Wetboek?'")
    print("   - 'Welke vergunningsplichten gelden voor handelsactiviteiten in Brussel?'")
    print("   - 'Quels sont les droits du travailleur en cas de licenciement?'")
    
    print("\n6. Belgian Legal Context Features:")
    print("   - Federal structure awareness (Federaal/Vlaams/Waals/Brussels)")
    print("   - Belgian legal terminology and concepts")
    print("   - Multi-language support (Dutch/French/English)")
    print("   - Orde van Vlaamse Balies compliance")
    print("   - Complete offline operation for confidentiality")
    
    print("\n" + "=" * 60)
    print("✅ Belgian Legal Assistant demo setup complete!")
    print("Follow the steps above to test Belgian legal filtering.")


if __name__ == "__main__":
    test_belgian_filtering_demo() 