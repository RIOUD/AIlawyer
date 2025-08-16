#!/usr/bin/env python3
"""
Sample Legal Document Generator

This script creates a sample legal document PDF for testing the
Secure Offline Legal Assistant system.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_sample_legal_document():
    """Creates a sample legal document PDF."""
    
    # Create the PDF file
    filename = "source_documents/sample_legal_document.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Story to hold the content
    story = []
    
    # Title
    title = Paragraph("SAMPLE LEGAL DOCUMENT: MOTION TO DISMISS", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Content sections
    sections = [
        ("INTRODUCTION", """
        This document outlines the legal requirements and procedures for filing a motion to dismiss in civil court proceedings. 
        A motion to dismiss is a request made by a defendant asking the court to dismiss the case without a trial.
        """),
        
        ("GROUNDS FOR MOTION TO DISMISS", """
        Common grounds for filing a motion to dismiss include:
        1. Lack of subject matter jurisdiction
        2. Lack of personal jurisdiction
        3. Improper venue
        4. Insufficient process or service of process
        5. Failure to state a claim upon which relief can be granted
        6. Statute of limitations has expired
        7. Res judicata or collateral estoppel
        """),
        
        ("FILING REQUIREMENTS", """
        To file a motion to dismiss, the following requirements must be met:
        - The motion must be filed in writing
        - It must be filed with the appropriate court
        - It must be served on all parties
        - It must include a memorandum of law supporting the motion
        - It must be filed within the time limits set by court rules
        """),
        
        ("PROCEDURAL TIMELINE", """
        The typical timeline for a motion to dismiss is as follows:
        1. Defendant files motion to dismiss
        2. Plaintiff has opportunity to respond (usually 14-21 days)
        3. Defendant may file a reply brief
        4. Court schedules hearing (if required)
        5. Court issues ruling on the motion
        """),
        
        ("LEGAL STANDARDS", """
        The court will evaluate the motion using the following standards:
        - For failure to state a claim: All allegations in the complaint are assumed to be true
        - For lack of jurisdiction: Court must determine if it has authority to hear the case
        - For improper venue: Court must determine if the case is filed in the correct location
        """),
        
        ("CONSEQUENCES OF GRANTING", """
        If a motion to dismiss is granted:
        - The case is dismissed without prejudice (can be refiled) or with prejudice (cannot be refiled)
        - The plaintiff may appeal the decision
        - The defendant is relieved of the obligation to defend the case
        - Court costs and attorney fees may be awarded to the prevailing party
        """)
    ]
    
    # Add sections to the story
    for section_title, content in sections:
        # Section header
        header = Paragraph(section_title, styles['Heading2'])
        story.append(header)
        story.append(Spacer(1, 6))
        
        # Section content
        paragraph = Paragraph(content, styles['Normal'])
        story.append(paragraph)
        story.append(Spacer(1, 12))
    
    # Build the PDF
    doc.build(story)
    print(f"✅ Created sample legal document: {filename}")


if __name__ == "__main__":
    # Ensure source_documents directory exists
    os.makedirs("source_documents", exist_ok=True)
    
    # Create the sample document
    create_sample_legal_document()
    
    print("\n📋 Sample legal document created successfully!")
    print("You can now test the system with:")
    print("1. python ingest.py")
    print("2. python app.py") 