#!/usr/bin/env python3
"""
Rich Text Formatter for Legal Assistant

Provides enhanced text formatting for legal answers including:
- Bold important legal terms
- Bullet points for lists
- Section headers for complex answers
- Highlight key citations
- Color-coded source types
- Professional legal document styling
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.rule import Rule


class LegalTextFormatter:
    """
    Rich text formatter for legal document presentation.
    
    Provides professional formatting for legal answers, citations,
    and document structure with color coding and typography.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the legal text formatter.
        
        Args:
            console: Rich console instance (creates new one if None)
        """
        self.console = console or Console()
        
        # Legal terminology patterns for highlighting
        self.legal_terms = [
            # Belgian legal terms
            r'\b(artikel|art\.)\s+\d+',  # Article references
            r'\b(wet|wetboek|code)\s+[A-Z]',  # Law/Code references
            r'\b(decreet|ordonnantie|besluit)\s+[A-Z]',  # Decrees/Ordinances
            r'\b(arrest|vonnis|beschikking)\s+[A-Z]',  # Court decisions
            r'\b(hof\s+van\s+cassatie|rechtbank|arbeidsrechtbank)',  # Courts
            r'\b(werkgever|werknemer|arbeidsovereenkomst)',  # Employment terms
            r'\b(huurovereenkomst|eigendom|bezit)',  # Property terms
            r'\b(schadevergoeding|onrechtmatige\s+daad)',  # Damages/Torts
            r'\b(erfrecht|testament|erfgenaam)',  # Inheritance
            r'\b(faillissement|insolventie)',  # Bankruptcy
            r'\b(handelsrecht|vennootschapsrecht)',  # Commercial law
            r'\b(privaatrecht|publiekrecht)',  # Private/Public law
            r'\b(grondwet|grondwettelijk\s+hof)',  # Constitutional law
            r'\b(europese\s+unie|eu\s+recht)',  # EU law
            r'\b(mensenrechten|discriminatie)',  # Human rights
            r'\b(privacy|gegevensbescherming)',  # Privacy/Data protection
            
            # General legal terms
            r'\b(plaintiff|defendant|appellant|respondent)',
            r'\b(contract|agreement|clause|provision)',
            r'\b(liability|damages|compensation)',
            r'\b(jurisdiction|venue|forum)',
            r'\b(evidence|testimony|witness)',
            r'\b(appeal|review|reversal)',
            r'\b(injunction|restraining\s+order)',
            r'\b(settlement|mediation|arbitration)',
            r'\b(statute|regulation|ordinance)',
            r'\b(precedent|case\s+law|common\s+law)',
        ]
        
        # Source type color mapping
        self.source_colors = {
            'wetboeken': 'blue',
            'jurisprudentie': 'green',
            'contracten': 'yellow',
            'advocatenstukken': 'magenta',
            'rechtsleer': 'cyan',
            'reglementering': 'red',
            'unknown': 'white'
        }
        
        # Jurisdiction color mapping
        self.jurisdiction_colors = {
            'federaal': 'red',
            'vlaams': 'yellow',
            'waals': 'green',
            'brussels': 'blue',
            'gemeentelijk': 'cyan',
            'provinciaal': 'magenta',
            'eu': 'bright_blue',
            'unknown': 'white'
        }
    
    def format_legal_answer(self, answer: str, sources: List[Dict] = None) -> str:
        """
        Format a legal answer with rich text formatting.
        
        Args:
            answer: The legal answer text
            sources: List of source documents
            
        Returns:
            Formatted answer string
        """
        # Create rich text object
        text = Text()
        
        # Split answer into sections
        sections = self._split_into_sections(answer)
        
        for section in sections:
            if section['type'] == 'header':
                text.append(f"\n{section['content']}\n", style="bold blue")
            elif section['type'] == 'list':
                text.append(self._format_list(section['content']), style="white")
            elif section['type'] == 'paragraph':
                text.append(self._format_paragraph(section['content']), style="white")
            elif section['type'] == 'citation':
                text.append(self._format_citation(section['content']), style="italic cyan")
        
        return str(text)
    
    def _split_into_sections(self, text: str) -> List[Dict]:
        """Split text into logical sections for formatting."""
        sections = []
        
        # Split by lines
        lines = text.split('\n')
        current_section = {'type': 'paragraph', 'content': []}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_section['content']:
                    sections.append(current_section)
                    current_section = {'type': 'paragraph', 'content': []}
                continue
            
            # Detect headers
            if re.match(r'^[A-Z][A-Z\s]+:$', line) or re.match(r'^[0-9]+\.\s+[A-Z]', line):
                if current_section['content']:
                    sections.append(current_section)
                sections.append({'type': 'header', 'content': line})
                current_section = {'type': 'paragraph', 'content': []}
                continue
            
            # Detect lists
            if re.match(r'^[-•*]\s+', line) or re.match(r'^[0-9]+\.\s+', line):
                if current_section['type'] != 'list':
                    if current_section['content']:
                        sections.append(current_section)
                    current_section = {'type': 'list', 'content': []}
                current_section['content'].append(line)
                continue
            
            # Detect citations
            if re.search(r'\([^)]*art\.\s*\d+[^)]*\)', line) or re.search(r'\([^)]*[A-Z][a-z]+\s+\d+[^)]*\)', line):
                if current_section['content']:
                    sections.append(current_section)
                sections.append({'type': 'citation', 'content': line})
                current_section = {'type': 'paragraph', 'content': []}
                continue
            
            # Regular paragraph content
            if current_section['type'] != 'paragraph':
                if current_section['content']:
                    sections.append(current_section)
                current_section = {'type': 'paragraph', 'content': []}
            current_section['content'].append(line)
        
        # Add final section
        if current_section['content']:
            sections.append(current_section)
        
        return sections
    
    def _format_paragraph(self, lines: List[str]) -> str:
        """Format paragraph text with legal term highlighting."""
        text = ' '.join(lines)
        
        # Highlight legal terms
        for pattern in self.legal_terms:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in reversed(list(matches)):
                start, end = match.span()
                term = text[start:end]
                text = text[:start] + f"[bold yellow]{term}[/bold yellow]" + text[end:]
        
        return text
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items with bullet points."""
        formatted_items = []
        for item in items:
            # Remove existing bullet points and add rich formatting
            clean_item = re.sub(r'^[-•*]\s+', '', item)
            clean_item = re.sub(r'^[0-9]+\.\s+', '', item)
            
            # Highlight legal terms in list items
            for pattern in self.legal_terms:
                matches = re.finditer(pattern, clean_item, re.IGNORECASE)
                for match in reversed(list(matches)):
                    start, end = match.span()
                    term = clean_item[start:end]
                    clean_item = clean_item[:start] + f"[bold yellow]{term}[/bold yellow]" + clean_item[end:]
            
            formatted_items.append(f"• {clean_item}")
        
        return '\n'.join(formatted_items)
    
    def _format_citation(self, citation: str) -> str:
        """Format legal citations with highlighting."""
        # Highlight article references
        citation = re.sub(r'(art\.\s*\d+)', r'[bold green]\1[/bold green]', citation)
        
        # Highlight law references
        citation = re.sub(r'([A-Z][a-z]+\s+\d+)', r'[bold blue]\1[/bold blue]', citation)
        
        return citation
    
    def create_sources_table(self, sources: List[Dict]) -> Table:
        """
        Create a rich table for displaying source documents.
        
        Args:
            sources: List of source document dictionaries
            
        Returns:
            Rich table object
        """
        table = Table(title="📚 Source Documents", show_header=True, header_style="bold magenta")
        
        # Add columns
        table.add_column("Document", style="cyan", no_wrap=True)
        table.add_column("Type", style="green")
        table.add_column("Jurisdiction", style="yellow")
        table.add_column("Date", style="blue")
        table.add_column("Relevance", style="red")
        
        # Add rows
        for source in sources:
            metadata = source.get('metadata', {})
            
            # Get document name
            doc_name = metadata.get('source', 'Unknown Document')
            if len(doc_name) > 40:
                doc_name = doc_name[:37] + "..."
            
            # Get document type with color
            doc_type = metadata.get('document_type', 'unknown')
            doc_type_color = self.source_colors.get(doc_type, 'white')
            
            # Get jurisdiction with color
            jurisdiction = metadata.get('jurisdiction', 'unknown')
            jurisdiction_color = self.jurisdiction_colors.get(jurisdiction, 'white')
            
            # Get date
            date = metadata.get('date', 'Unknown')
            
            # Get relevance score
            relevance = source.get('score', 0)
            relevance_str = f"{relevance:.2f}" if relevance else "N/A"
            
            table.add_row(
                doc_name,
                f"[{doc_type_color}]{doc_type}[/{doc_type_color}]",
                f"[{jurisdiction_color}]{jurisdiction}[/{jurisdiction_color}]",
                date,
                relevance_str
            )
        
        return table
    
    def create_answer_panel(self, answer: str, title: str = "📋 Legal Answer") -> Panel:
        """
        Create a rich panel for displaying the legal answer.
        
        Args:
            answer: The formatted answer text
            title: Panel title
            
        Returns:
            Rich panel object
        """
        # Create markdown for better formatting
        markdown_content = self._convert_to_markdown(answer)
        
        return Panel(
            Markdown(markdown_content),
            title=title,
            title_align="center",
            border_style="blue",
            padding=(1, 2)
        )
    
    def _convert_to_markdown(self, text: str) -> str:
        """Convert rich text to markdown format."""
        # Convert rich formatting to markdown
        text = re.sub(r'\[bold yellow\](.*?)\[/bold yellow\]', r'**\1**', text)
        text = re.sub(r'\[bold blue\](.*?)\[/bold blue\]', r'**\1**', text)
        text = re.sub(r'\[bold green\](.*?)\[/bold green\]', r'**\1**', text)
        text = re.sub(r'\[italic cyan\](.*?)\[/italic cyan\]', r'*\1*', text)
        
        return text
    
    def create_legal_document_layout(self, answer: str, sources: List[Dict]) -> Layout:
        """
        Create a professional legal document layout.
        
        Args:
            answer: The legal answer
            sources: List of source documents
            
        Returns:
            Rich layout object
        """
        # Create layout
        layout = Layout()
        
        # Split into sections
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=10)
        )
        
        # Header section
        header = Layout()
        header.split_row(
            Layout(Panel("⚖️ Legal Assistant", style="bold blue"), name="title"),
            Layout(Panel(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}", style="dim"), name="date")
        )
        layout["header"].update(header)
        
        # Main content section
        answer_panel = self.create_answer_panel(answer)
        layout["main"].update(answer_panel)
        
        # Footer section with sources
        if sources:
            sources_table = self.create_sources_table(sources)
            layout["footer"].update(Panel(sources_table, title="📚 Sources", border_style="green"))
        
        return layout
    
    def format_legal_terms_glossary(self, terms: List[str]) -> Table:
        """
        Create a glossary table for legal terms.
        
        Args:
            terms: List of legal terms to define
            
        Returns:
            Rich table object
        """
        table = Table(title="📖 Legal Terms Glossary", show_header=True, header_style="bold blue")
        
        table.add_column("Term", style="cyan", no_wrap=True)
        table.add_column("Definition", style="white")
        table.add_column("Category", style="green")
        
        # Legal term definitions (Belgian context)
        term_definitions = {
            'artikel': 'Article - A numbered section of a law or code',
            'wet': 'Law - A formal rule enacted by a legislative body',
            'wetboek': 'Code - A systematic collection of laws',
            'decreet': 'Decree - A law enacted by a regional parliament',
            'ordonnantie': 'Ordinance - A law enacted by the Brussels parliament',
            'arrest': 'Judgment - A decision of the Court of Cassation',
            'vonnis': 'Judgment - A decision of a court',
            'werkgever': 'Employer - The party that hires and pays workers',
            'werknemer': 'Employee - The party that provides labor',
            'arbeidsovereenkomst': 'Employment contract - Agreement between employer and employee',
            'huurovereenkomst': 'Lease agreement - Contract for renting property',
            'schadevergoeding': 'Compensation - Payment for damages suffered',
            'onrechtmatige daad': 'Tort - Civil wrong causing harm to another',
            'erfrecht': 'Inheritance law - Legal rules governing succession',
            'faillissement': 'Bankruptcy - Legal process for insolvent debtors',
            'handelsrecht': 'Commercial law - Legal rules for business transactions',
            'privaatrecht': 'Private law - Legal rules between private parties',
            'publiekrecht': 'Public law - Legal rules involving government',
            'grondwet': 'Constitution - Fundamental law of the state',
            'mensenrechten': 'Human rights - Fundamental rights of individuals',
            'privacy': 'Privacy - Right to personal data protection',
        }
        
        for term in terms:
            definition = term_definitions.get(term.lower(), 'Legal term requiring context')
            category = self._get_term_category(term)
            
            table.add_row(
                f"[bold yellow]{term}[/bold yellow]",
                definition,
                category
            )
        
        return table
    
    def _get_term_category(self, term: str) -> str:
        """Get the category for a legal term."""
        term_lower = term.lower()
        
        if any(word in term_lower for word in ['artikel', 'wet', 'wetboek', 'decreet']):
            return 'Legislation'
        elif any(word in term_lower for word in ['arrest', 'vonnis', 'beschikking']):
            return 'Case Law'
        elif any(word in term_lower for word in ['werkgever', 'werknemer', 'arbeid']):
            return 'Employment Law'
        elif any(word in term_lower for word in ['huur', 'eigendom', 'bezit']):
            return 'Property Law'
        elif any(word in term_lower for word in ['schade', 'onrechtmatig']):
            return 'Tort Law'
        elif any(word in term_lower for word in ['erf', 'testament']):
            return 'Inheritance Law'
        else:
            return 'General'
    
    def create_progress_display(self, message: str) -> Progress:
        """
        Create a progress display for long operations.
        
        Args:
            message: Progress message
            
        Returns:
            Rich progress object
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        )
        
        task = progress.add_task(message, total=None)
        return progress, task
    
    def format_error_message(self, error: str) -> Panel:
        """
        Format error messages with appropriate styling.
        
        Args:
            error: Error message
            
        Returns:
            Rich panel object
        """
        return Panel(
            f"[red]❌ {error}[/red]",
            title="Error",
            title_align="center",
            border_style="red",
            padding=(1, 2)
        )
    
    def format_success_message(self, message: str) -> Panel:
        """
        Format success messages with appropriate styling.
        
        Args:
            message: Success message
            
        Returns:
            Rich panel object
        """
        return Panel(
            f"[green]✅ {message}[/green]",
            title="Success",
            title_align="center",
            border_style="green",
            padding=(1, 2)
        )
    
    def create_legal_document_header(self, title: str, subtitle: str = None) -> Panel:
        """
        Create a professional legal document header.
        
        Args:
            title: Document title
            subtitle: Optional subtitle
            
        Returns:
            Rich panel object
        """
        content = f"[bold blue]{title}[/bold blue]"
        if subtitle:
            content += f"\n[dim]{subtitle}[/dim]"
        
        return Panel(
            Align.center(content),
            border_style="blue",
            padding=(1, 2)
        )
    
    def format_legal_citation(self, citation: str) -> Text:
        """
        Format a legal citation with proper styling.
        
        Args:
            citation: Citation text
            
        Returns:
            Rich text object
        """
        text = Text()
        
        # Highlight different parts of the citation
        # Article references
        citation = re.sub(r'(art\.\s*\d+)', r'[bold green]\1[/bold green]', citation)
        
        # Law references
        citation = re.sub(r'([A-Z][a-z]+\s+\d+)', r'[bold blue]\1[/bold blue]', citation)
        
        # Court names
        citation = re.sub(r'(Hof van Cassatie|Rechtbank|Arbeidsrechtbank)', r'[bold yellow]\1[/bold yellow]', citation)
        
        # Dates
        citation = re.sub(r'(\d{1,2}/\d{1,2}/\d{4})', r'[cyan]\1[/cyan]', citation)
        
        text.append(citation)
        return text


class ConsoleFormatter:
    """
    Console-specific formatter for terminal output.
    
    Provides methods for formatting output specifically for console display.
    """
    
    def __init__(self, console: Console):
        """
        Initialize console formatter.
        
        Args:
            console: Rich console instance
        """
        self.console = console
        self.legal_formatter = LegalTextFormatter(console)
    
    def print_legal_answer(self, answer: str, sources: List[Dict] = None):
        """
        Print a formatted legal answer to the console.
        
        Args:
            answer: The legal answer text
            sources: List of source documents
        """
        # Create layout
        layout = self.legal_formatter.create_legal_document_layout(answer, sources or [])
        
        # Print to console
        self.console.print(layout)
    
    def print_sources_only(self, sources: List[Dict]):
        """
        Print only the sources table.
        
        Args:
            sources: List of source documents
        """
        table = self.legal_formatter.create_sources_table(sources)
        self.console.print(table)
    
    def print_legal_terms(self, terms: List[str]):
        """
        Print a legal terms glossary.
        
        Args:
            terms: List of legal terms
        """
        table = self.legal_formatter.format_legal_terms_glossary(terms)
        self.console.print(table)
    
    def print_error(self, error: str):
        """Print an error message."""
        panel = self.legal_formatter.format_error_message(error)
        self.console.print(panel)
    
    def print_success(self, message: str):
        """Print a success message."""
        panel = self.legal_formatter.format_success_message(message)
        self.console.print(panel)
    
    def print_header(self, title: str, subtitle: str = None):
        """Print a document header."""
        panel = self.legal_formatter.create_legal_document_header(title, subtitle)
        self.console.print(panel)
    
    def print_citation(self, citation: str):
        """Print a formatted legal citation."""
        text = self.legal_formatter.format_legal_citation(citation)
        self.console.print(text) 