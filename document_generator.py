#!/usr/bin/env python3
"""
Document Generator for Legal Assistant

Generates legal documents from templates and provides PDF export capabilities.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

from template_manager import TemplateManager


class DocumentGenerator:
    """
    Generates legal documents from templates with PDF export.
    """
    
    def __init__(self, template_manager: TemplateManager):
        """
        Initialize the document generator.
        
        Args:
            template_manager: Template manager instance
        """
        self.template_manager = template_manager
        self.styles = self._setup_styles()
    
    def _setup_styles(self) -> Dict[str, ParagraphStyle]:
        """
        Setup document styles for PDF generation.
        
        Returns:
            Dictionary of paragraph styles
        """
        styles = getSampleStyleSheet()
        
        # Custom styles for legal documents
        styles.add(ParagraphStyle(
            name='LegalTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='LegalHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='LegalBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='LegalSignature',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=20,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
        
        return styles
    
    def generate_document(self, category: str, template_id: str, 
                         variables: Dict[str, str], use_custom: bool = True) -> Dict[str, Any]:
        """
        Generate a document from a template.
        
        Args:
            category: Template category
            template_id: Template identifier
            variables: Template variables
            use_custom: Whether to use custom templates
            
        Returns:
            Dictionary with generated document and metadata
        """
        return self.template_manager.generate_document(category, template_id, variables, use_custom)
    
    def export_to_pdf(self, document_data: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        Export a generated document to PDF.
        
        Args:
            document_data: Document data from generate_document
            output_path: Output PDF file path
            
        Returns:
            Export result
        """
        try:
            if 'error' in document_data:
                return {'error': document_data['error']}
            
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # Add title
            template_info = document_data['template_info']
            title = f"{template_info['name']}"
            story.append(Paragraph(title, self.styles['LegalTitle']))
            story.append(Spacer(1, 20))
            
            # Add template description
            if template_info.get('description'):
                story.append(Paragraph(f"<b>Beschrijving:</b> {template_info['description']}", 
                                     self.styles['LegalBody']))
                story.append(Spacer(1, 12))
            
            # Add metadata table
            metadata_data = [
                ['Categorie', template_info.get('category', 'N/A')],
                ['Taal', template_info.get('language', 'N/A')],
                ['Jurisdictie', template_info.get('jurisdiction', 'N/A')],
                ['Gegenereerd op', document_data.get('generated_at', 'N/A')]
            ]
            
            if template_info.get('is_custom'):
                metadata_data.append(['Type', 'Aangepaste template'])
            else:
                metadata_data.append(['Type', 'Standaard template'])
            
            metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
            metadata_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(metadata_table)
            story.append(Spacer(1, 20))
            
            # Add variables used
            if document_data.get('variables_used'):
                story.append(Paragraph("<b>Gebruikte variabelen:</b>", self.styles['LegalHeading']))
                
                variables_data = []
                for key, value in document_data['variables_used'].items():
                    variables_data.append([key, str(value)])
                
                variables_table = Table(variables_data, colWidths=[2*inch, 4*inch])
                variables_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(variables_table)
                story.append(Spacer(1, 20))
            
            # Add generated document content
            story.append(Paragraph("<b>Gegenereerd document:</b>", self.styles['LegalHeading']))
            story.append(Spacer(1, 12))
            
            # Split document into paragraphs and add to story
            document_text = document_data['document']
            paragraphs = document_text.split('\n\n')
            
            for paragraph in paragraphs:
                if paragraph.strip():
                    # Handle different paragraph types
                    if paragraph.strip().isupper() and len(paragraph.strip()) < 100:
                        # Title/heading
                        story.append(Paragraph(paragraph.strip(), self.styles['LegalHeading']))
                    elif paragraph.strip().startswith('ARTIKEL') or paragraph.strip().startswith('ARTICLE'):
                        # Article heading
                        story.append(Paragraph(paragraph.strip(), self.styles['LegalHeading']))
                    else:
                        # Regular paragraph
                        story.append(Paragraph(paragraph.strip(), self.styles['LegalBody']))
                    story.append(Spacer(1, 6))
            
            # Build PDF
            doc.build(story)
            
            return {
                'success': True,
                'output_path': output_path,
                'file_size': os.path.getsize(output_path)
            }
        
        except Exception as e:
            return {'error': f'Error generating PDF: {e}'}
    
    def generate_and_export(self, category: str, template_id: str, 
                           variables: Dict[str, str], output_path: str,
                           use_custom: bool = True) -> Dict[str, Any]:
        """
        Generate a document and export it to PDF in one step.
        
        Args:
            category: Template category
            template_id: Template identifier
            variables: Template variables
            output_path: Output PDF file path
            use_custom: Whether to use custom templates
            
        Returns:
            Combined result
        """
        # Generate document
        document_result = self.generate_document(category, template_id, variables, use_custom)
        
        if 'error' in document_result:
            return document_result
        
        # Export to PDF
        pdf_result = self.export_to_pdf(document_result, output_path)
        
        if 'error' in pdf_result:
            return pdf_result
        
        # Combine results
        return {
            'success': True,
            'document': document_result,
            'pdf': pdf_result,
            'output_path': output_path
        }
    
    def create_template_preview(self, category: str, template_id: str,
                               use_custom: bool = True) -> Dict[str, Any]:
        """
        Create a preview of a template with sample variables.
        
        Args:
            category: Template category
            template_id: Template identifier
            use_custom: Whether to use custom templates
            
        Returns:
            Preview result
        """
        template = self.template_manager.get_template(category, template_id, use_custom)
        if not template:
            return {'error': 'Template not found'}
        
        # Generate sample variables
        sample_variables = self._generate_sample_variables(template.get('variables', []))
        
        # Generate preview document
        preview_result = self.generate_document(category, template_id, sample_variables, use_custom)
        
        if 'error' in preview_result:
            return preview_result
        
        return {
            'success': True,
            'template_info': template,
            'sample_variables': sample_variables,
            'preview_document': preview_result['document']
        }
    
    def _generate_sample_variables(self, variables: List[str]) -> Dict[str, str]:
        """
        Generate sample values for template variables.
        
        Args:
            variables: List of variable names
            
        Returns:
            Dictionary of sample values
        """
        sample_values = {
            # Names
            'advocaat_naam': 'Jan Janssens',
            'eiser_naam': 'Maria Maes',
            'gedaagde_naam': 'Peter Peeters',
            'werkgever_naam': 'Bedrijf BVBA',
            'werknemer_naam': 'Anna Andersen',
            'verhuurder_naam': 'Eigenaar NV',
            'huurder_naam': 'Huurder Huis',
            'ontvanger_naam': 'Ontvanger Ontvangst',
            'cliënt_naam': 'Cliënt Client',
            
            # Addresses
            'adres': 'Kerkstraat 1, 1000 Brussel',
            'eiser_adres': 'Hoofdstraat 10, 2000 Antwerpen',
            'gedaagde_adres': 'Zijstraat 5, 3000 Leuven',
            'werkgever_adres': 'Industrieweg 15, 9000 Gent',
            'werknemer_adres': 'Werknemerstraat 20, 3500 Hasselt',
            'verhuurder_adres': 'Verhuurderlaan 25, 4000 Luik',
            'huurder_adres': 'Huurderweg 30, 5000 Namen',
            'ontvanger_adres': 'Ontvangerplein 35, 6000 Charleroi',
            'advocaat_adres': 'Advocatenlaan 40, 7000 Bergen',
            
            # Places
            'plaats': 'Brussel',
            'rechtbank_plaats': 'Antwerpen',
            'werkplaats': 'Gent',
            
            # Dates
            'datum': '15 januari 2024',
            'date': '15 janvier 2024',
            
            # Times
            'tijd': '14:00',
            'heure': '14:00',
            
            # Courts and institutions
            'rechtbank_naam': 'Rechtbank van eerste aanleg',
            'afdeling': 'Burgerlijke',
            'tribunal_nom': 'Tribunal de première instance',
            'section': 'Civile',
            
            # Legal content
            'specifieke_vorderingen': 'Betaling van €5.000 aan schadevergoeding',
            'gronden': 'Contractuele aansprakelijkheid wegens niet-nakoming van overeenkomst',
            'demandes_specifiques': 'Paiement de €5.000 de dommages et intérêts',
            'moyens': 'Responsabilité contractuelle pour inexécution de contrat',
            
            # Contract details
            'functie': 'Advocaat',
            'afdeling': 'Burgerlijk Recht',
            'brutoloon': '3.500',
            'loondatum': '25',
            'vakantiedagen': '20',
            'werkuren': '38',
            'werkdagen': '5',
            'proeftijd': '3',
            'opzegtermijn': '3',
            
            # Rental details
            'gehuurde_ruimte': 'Appartement gelegen te Brussel, Kerkstraat 1',
            'huurprijs': '1.200',
            'betaaldatum': '1',
            'waarborg': '2.400',
            'waarborg_rekening': 'BE12 3456 7890 1234',
            'huurperiode': '3',
            
            # Letter content
            'ontvanger_titel': 'heer',
            'feiten': 'U heeft de overeenkomst niet nagekomen door niet te betalen',
            'rechtsgrond': 'artikel 1234 van het Burgerlijk Wetboek',
            'termijn': '14',
            'gevraagde_maatregelen': 'Betaling van het openstaande bedrag van €5.000',
            'destinataire_titre': 'Monsieur',
            'faits': 'Vous n\'avez pas respecté l\'accord en ne payant pas',
            'base_juridique': 'article 1234 du Code civil',
            'délai': '14',
            'mesures_demandées': 'Paiement du montant impayé de €5.000',
            
            # Citation details
            'rechtbank': 'Hof van Cassatie',
            'zaaknummer': 'C.23.0123.F',
            'rechtsleer': 'Aansprakelijkheid',
            'court': 'Court of Justice',
            'case_number': 'C-123/23',
            'legal_doctrine': 'Liability',
            
            # Clause details
            'artikelnummer': '15',
            'partij_naam': 'Partij A',
            'andere_partij': 'Partij B',
            'duur': '5',
            'article_number': '15',
            
            # Form details
            'klager_naam': 'Klager Klaag',
            'klager_adres': 'Klagerstraat 1, 1000 Brussel',
            'klager_telefoon': '+32 2 123 45 67',
            'klager_email': 'klager@example.com',
            'klacht_beschrijving': 'De service was niet naar behoren',
            'gewenste_oplossing': 'Terugbetaling van het betaalde bedrag',
            'handtekening': '_________________'
        }
        
        result = {}
        for var in variables:
            result[var] = sample_values.get(var, f"[{var}]")
        
        return result
    
    def batch_generate_documents(self, template_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate multiple documents in batch.
        
        Args:
            template_requests: List of template generation requests
            
        Returns:
            List of generation results
        """
        results = []
        
        for request in template_requests:
            category = request.get('category')
            template_id = request.get('template_id')
            variables = request.get('variables', {})
            use_custom = request.get('use_custom', True)
            
            if not category or not template_id:
                results.append({'error': 'Missing category or template_id'})
                continue
            
            result = self.generate_document(category, template_id, variables, use_custom)
            results.append(result)
        
        return results
    
    def export_batch_to_pdf(self, documents: List[Dict[str, Any]], 
                           output_dir: str) -> List[Dict[str, Any]]:
        """
        Export multiple documents to PDF.
        
        Args:
            documents: List of document data
            output_dir: Output directory for PDFs
            
        Returns:
            List of export results
        """
        results = []
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for i, document in enumerate(documents):
            if 'error' in document:
                results.append({'error': document['error']})
                continue
            
            template_info = document['template_info']
            filename = f"{template_info['name']}_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path = output_path / filename
            
            result = self.export_to_pdf(document, str(file_path))
            results.append(result)
        
        return results 