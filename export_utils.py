#!/usr/bin/env python3
"""
Export utilities for Secure Offline Legal Assistant

Handles PDF export of conversation history and session data.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


class ConversationExporter:
    """
    Handles export of conversation history to PDF format.
    """
    
    def __init__(self):
        """Initialize the exporter with default styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the export."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkgreen
        )
        
        # Question style
        self.question_style = ParagraphStyle(
            'Question',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            spaceBefore=12,
            leftIndent=20,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        )
        
        # Answer style
        self.answer_style = ParagraphStyle(
            'Answer',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            leftIndent=30,
            alignment=TA_JUSTIFY
        )
        
        # Source style
        self.source_style = ParagraphStyle(
            'Source',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=8,
            leftIndent=40,
            textColor=colors.grey,
            fontName='Helvetica-Oblique'
        )
        
        # Metadata style
        self.metadata_style = ParagraphStyle(
            'Metadata',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            textColor=colors.darkgrey
        )
    
    def export_session_to_pdf(self, session_data: Dict, queries: List[Dict], 
                             output_path: str) -> bool:
        """
        Export a complete session to PDF.
        
        Args:
            session_data: Session metadata
            queries: List of queries in the session
            output_path: Path for the output PDF file
            
        Returns:
            True if export successful
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # Add title
            title = Paragraph("Legal Assistant Conversation History", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Add session metadata
            story.extend(self._create_session_metadata(session_data))
            story.append(Spacer(1, 20))
            
            # Add queries
            story.extend(self._create_queries_section(queries))
            
            # Build the PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error exporting session to PDF: {e}")
            return False
    
    def export_search_results_to_pdf(self, search_term: str, results: List[Dict], 
                                    output_path: str) -> bool:
        """
        Export search results to PDF.
        
        Args:
            search_term: The search term used
            results: List of matching queries
            output_path: Path for the output PDF file
            
        Returns:
            True if export successful
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # Add title
            title = Paragraph("Legal Assistant Search Results", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Add search metadata
            search_info = f"Search Term: '{search_term}'"
            search_info += f"<br/>Results Found: {len(results)}"
            search_info += f"<br/>Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            search_para = Paragraph(search_info, self.metadata_style)
            story.append(search_para)
            story.append(Spacer(1, 20))
            
            # Add results
            story.extend(self._create_queries_section(results, show_session_info=True))
            
            # Build the PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error exporting search results to PDF: {e}")
            return False
    
    def export_statistics_to_pdf(self, stats: Dict[str, Any], output_path: str) -> bool:
        """
        Export query statistics to PDF.
        
        Args:
            stats: Statistics dictionary
            output_path: Path for the output PDF file
            
        Returns:
            True if export successful
        """
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # Add title
            title = Paragraph("Legal Assistant Usage Statistics", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Add statistics table
            stats_data = [
                ["Metric", "Value"],
                ["Total Queries", str(stats.get('total_queries', 0))],
                ["Total Sessions", str(stats.get('total_sessions', 0))],
                ["Avg Queries per Session", str(stats.get('avg_queries_per_session', 0))],
            ]
            
            # Add common filters if available
            common_filters = stats.get('common_filters', [])
            if common_filters:
                stats_data.append(["", ""])  # Empty row
                stats_data.append(["Most Common Filters", ""])
                for filter_info, count in common_filters[:5]:
                    try:
                        filter_dict = json.loads(filter_info) if filter_info else {}
                        filter_str = ", ".join([f"{k}: {v}" for k, v in filter_dict.items() if v])
                        stats_data.append([filter_str, str(count)])
                    except:
                        stats_data.append([str(filter_info), str(count)])
            
            # Create table
            table = Table(stats_data, colWidths=[4*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Add export timestamp
            timestamp = f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            timestamp_para = Paragraph(timestamp, self.metadata_style)
            story.append(timestamp_para)
            
            # Build the PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"Error exporting statistics to PDF: {e}")
            return False
    
    def _create_session_metadata(self, session_data: Dict) -> List:
        """Create session metadata section."""
        elements = []
        
        # Session header
        session_header = Paragraph("Session Information", self.section_style)
        elements.append(session_header)
        
        # Create metadata table
        metadata_data = [
            ["Session ID", session_data.get('session_id', 'Unknown')],
            ["Start Time", session_data.get('start_time', 'Unknown')],
            ["End Time", session_data.get('end_time', 'Active')],
            ["Total Queries", str(session_data.get('total_queries', 0))],
            ["Status", session_data.get('status', 'Unknown')]
        ]
        
        # Add filters if available
        filters_used = session_data.get('filters_used')
        if filters_used:
            try:
                filters_dict = json.loads(filters_used)
                filter_str = ", ".join([f"{k}: {v}" for k, v in filters_dict.items() if v])
                metadata_data.append(["Filters Used", filter_str])
            except:
                metadata_data.append(["Filters Used", str(filters_used)])
        
        # Create table
        table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        return elements
    
    def _create_queries_section(self, queries: List[Dict], 
                               show_session_info: bool = False) -> List:
        """Create queries section for PDF."""
        elements = []
        
        # Queries header
        queries_header = Paragraph("Conversation History", self.section_style)
        elements.append(queries_header)
        
        for i, query in enumerate(queries, 1):
            # Query number and timestamp
            timestamp = query.get('query_time', 'Unknown')
            query_header = f"Query #{i} - {timestamp}"
            if show_session_info:
                session_id = query.get('session_id', 'Unknown')
                query_header += f" (Session: {session_id})"
            
            query_header_para = Paragraph(query_header, self.metadata_style)
            elements.append(query_header_para)
            
            # Question
            question_text = f"<b>Question:</b> {query.get('question', 'No question')}"
            question_para = Paragraph(question_text, self.question_style)
            elements.append(question_para)
            
            # Answer
            answer_text = f"<b>Answer:</b> {query.get('answer', 'No answer')}"
            answer_para = Paragraph(answer_text, self.answer_style)
            elements.append(answer_para)
            
            # Sources
            sources = query.get('sources')
            if sources:
                try:
                    sources_list = json.loads(sources) if isinstance(sources, str) else sources
                    if sources_list:
                        sources_text = "<b>Sources:</b><br/>"
                        for j, source in enumerate(sources_list, 1):
                            if isinstance(source, dict):
                                source_name = source.get('source', 'Unknown')
                                page = source.get('page', 'Unknown page')
                                sources_text += f"{j}. {source_name} (Page {page})<br/>"
                            else:
                                sources_text += f"{j}. {str(source)}<br/>"
                        
                        sources_para = Paragraph(sources_text, self.source_style)
                        elements.append(sources_para)
                except:
                    pass
            
            # Processing time if available
            processing_time = query.get('processing_time')
            if processing_time:
                time_text = f"Processing time: {processing_time:.2f} seconds"
                time_para = Paragraph(time_text, self.metadata_style)
                elements.append(time_para)
            
            elements.append(Spacer(1, 10))
        
        return elements
    
    def get_export_filename(self, session_id: str = None, search_term: str = None, 
                           export_type: str = "session") -> str:
        """
        Generate a filename for export.
        
        Args:
            session_id: Session identifier
            search_term: Search term used
            export_type: Type of export (session, search, stats)
            
        Returns:
            Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_type == "session" and session_id:
            return f"legal_assistant_session_{session_id}_{timestamp}.pdf"
        elif export_type == "search" and search_term:
            safe_term = "".join(c for c in search_term if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_term = safe_term.replace(' ', '_')[:20]
            return f"legal_assistant_search_{safe_term}_{timestamp}.pdf"
        elif export_type == "stats":
            return f"legal_assistant_statistics_{timestamp}.pdf"
        else:
            return f"legal_assistant_export_{timestamp}.pdf" 