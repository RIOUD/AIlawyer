#!/usr/bin/env python3
"""
Rich Text Formatting Demonstration

This script demonstrates the enhanced rich text formatting features
for legal answers with professional styling and color coding.
"""

from rich.console import Console
from rich_formatter import ConsoleFormatter, LegalTextFormatter
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from datetime import datetime


def create_sample_legal_answer():
    """Create a sample legal answer for demonstration."""
    return """
ARBEIDSRECHTELIJKE ASPECTEN VAN ONTSLAG

In het Belgische arbeidsrecht gelden strikte regels voor het ontslag van werknemers. Hieronder volgt een overzicht van de belangrijkste aspecten:

ONTZLAAGPROCEDURE:
1. Schriftelijke kennisgeving vereist volgens artikel 37 van de wet van 3 juli 1978
2. Motivering van het ontslag is verplicht
3. Voorafgaand overleg met de vakbondsafgevaardigde indien aanwezig

OPZEGTERMIJNEN:
• Werknemers met minder dan 6 maanden anciënniteit: 28 dagen
• Werknemers met 6 maanden tot 5 jaar anciënniteit: 35 dagen
• Werknemers met meer dan 5 jaar anciënniteit: 42 dagen

REDENEN VOOR ONTSLAG:
- Ernstige fout van de werknemer (art. 35 van de wet van 3 juli 1978)
- Dringende redenen (art. 36 van de wet van 3 juli 1978)
- Economische redenen (art. 51 van de wet van 3 juli 1978)

SCHADEVERGOEDING:
Bij onrechtmatig ontslag kan de werknemer aanspraak maken op schadevergoeding gelijk aan zes maanden brutoloon (arrest Hof van Cassatie van 15 januari 2023).

PROCEDURE BIJ GESCHILLEN:
Geschillen over ontslag worden behandeld door de arbeidsrechtbank. De werknemer heeft 3 jaar om een vordering in te stellen (art. 39 van de wet van 3 juli 1978).
"""


def create_sample_sources():
    """Create sample source documents for demonstration."""
    return [
        {
            'metadata': {
                'source': 'Wet van 3 juli 1978 betreffende de arbeidsovereenkomsten',
                'document_type': 'wetboeken',
                'jurisdiction': 'federaal',
                'date': '1978-07-03'
            },
            'score': 0.95
        },
        {
            'metadata': {
                'source': 'Arrest Hof van Cassatie 15 januari 2023',
                'document_type': 'jurisprudentie',
                'jurisdiction': 'federaal',
                'date': '2023-01-15'
            },
            'score': 0.87
        },
        {
            'metadata': {
                'source': 'Collectieve arbeidsovereenkomst nr. 109',
                'document_type': 'contracten',
                'jurisdiction': 'federaal',
                'date': '2022-12-01'
            },
            'score': 0.82
        },
        {
            'metadata': {
                'source': 'Vlaams Decreet Arbeid 2024',
                'document_type': 'wetboeken',
                'jurisdiction': 'vlaams',
                'date': '2024-01-01'
            },
            'score': 0.78
        }
    ]


def demonstrate_rich_formatting():
    """Demonstrate all rich formatting features."""
    console = Console()
    formatter = ConsoleFormatter(console)
    
    # Clear screen and show title
    console.clear()
    console.print(Panel.fit("🎨 Rich Text Formatting Demonstration", style="bold blue"))
    console.print()
    
    # Step 1: Show sample legal answer with rich formatting
    console.print("📋 Step 1: Formatted Legal Answer", style="bold green")
    console.print("=" * 50)
    
    sample_answer = create_sample_legal_answer()
    sample_sources = create_sample_sources()
    
    # Display with rich formatting
    formatter.print_legal_answer(sample_answer, sample_sources)
    console.print()
    
    # Step 2: Show sources table only
    console.print("📚 Step 2: Sources Table", style="bold green")
    console.print("=" * 50)
    formatter.print_sources_only(sample_sources)
    console.print()
    
    # Step 3: Show legal terms glossary
    console.print("📖 Step 3: Legal Terms Glossary", style="bold green")
    console.print("=" * 50)
    
    legal_terms = [
        'artikel', 'wet', 'wetboek', 'decreet', 'arrest', 'vonnis',
        'werkgever', 'werknemer', 'arbeidsovereenkomst', 'schadevergoeding',
        'arbeidsrechtbank', 'opzegtermijn', 'anciënniteit'
    ]
    
    formatter.print_legal_terms(legal_terms)
    console.print()
    
    # Step 4: Show individual formatting examples
    console.print("🎯 Step 4: Individual Formatting Examples", style="bold green")
    console.print("=" * 50)
    
    # Legal citation formatting
    console.print("📝 Legal Citation Formatting:")
    citations = [
        "art. 37 van de wet van 3 juli 1978",
        "Arrest Hof van Cassatie van 15 januari 2023",
        "art. 35 van de wet van 3 juli 1978"
    ]
    
    for citation in citations:
        formatter.print_citation(citation)
    console.print()
    
    # Error and success messages
    console.print("💬 Error and Success Messages:")
    formatter.print_error("Invalid legal reference provided")
    formatter.print_success("Legal document processed successfully")
    console.print()
    
    # Document header
    console.print("📄 Document Header:")
    formatter.print_header("Legal Analysis Report", "Employment Law - Termination Procedures")
    console.print()
    
    # Step 5: Show color coding explanation
    console.print("🎨 Step 5: Color Coding System", style="bold green")
    console.print("=" * 50)
    
    color_table = Table(title="Color Coding Guide", show_header=True, header_style="bold magenta")
    color_table.add_column("Element", style="cyan")
    color_table.add_column("Color", style="white")
    color_table.add_column("Description", style="yellow")
    
    color_table.add_row("Legal Terms", "Yellow (Bold)", "Important legal terminology")
    color_table.add_row("Article References", "Green (Bold)", "Article numbers and references")
    color_table.add_row("Law References", "Blue (Bold)", "Law names and codes")
    color_table.add_row("Court Names", "Yellow (Bold)", "Court and tribunal names")
    color_table.add_row("Dates", "Cyan", "Important dates and deadlines")
    color_table.add_row("Source Types", "Various", "Color-coded by document type")
    color_table.add_row("Jurisdictions", "Various", "Color-coded by jurisdiction")
    
    console.print(color_table)
    console.print()
    
    # Step 6: Show formatting features summary
    console.print("✨ Step 6: Formatting Features Summary", style="bold green")
    console.print("=" * 50)
    
    features_table = Table(show_header=False, box=None)
    features_table.add_column("Feature", style="cyan")
    features_table.add_column("Description", style="white")
    
    features_table.add_row("🔤 Bold Legal Terms", "Important legal terminology highlighted in bold yellow")
    features_table.add_row("📋 Bullet Points", "Lists formatted with professional bullet points")
    features_table.add_row("📑 Section Headers", "Complex answers organized with clear section headers")
    features_table.add_row("🔗 Key Citations", "Legal citations highlighted with special formatting")
    features_table.add_row("🎨 Color-coded Sources", "Source types and jurisdictions color-coded for easy identification")
    features_table.add_row("📊 Professional Tables", "Source documents displayed in organized tables")
    features_table.add_row("📖 Legal Glossary", "Automatic legal terms glossary with definitions")
    features_table.add_row("⚡ Progress Indicators", "Animated progress indicators for long operations")
    features_table.add_row("💬 Enhanced Messages", "Error and success messages with appropriate styling")
    features_table.add_row("📄 Document Layout", "Professional legal document layout with headers and footers")
    
    console.print(features_table)
    console.print()
    
    # Final summary
    console.print(Panel.fit(
        "🎉 Rich text formatting provides professional, readable, and visually appealing "
        "presentation of legal answers with enhanced usability for legal professionals.",
        title="Summary",
        border_style="green"
    ))


if __name__ == "__main__":
    demonstrate_rich_formatting() 