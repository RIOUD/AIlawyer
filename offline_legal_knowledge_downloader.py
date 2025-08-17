#!/usr/bin/env python3
"""
Offline Legal Knowledge Base Downloader
Downloads and stores all Belgian legal codes from Justel database for offline use
"""

import os
import sys
import json
import time
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
import PyPDF2
import io
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from datetime import datetime
import sqlite3
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('offline_legal_download.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class LegalCode:
    """Data class for legal code information"""
    name: str
    english: str
    french: str
    german: str
    url: str
    category: str
    pdf_url: Optional[str] = None
    content: Optional[str] = None
    last_updated: Optional[str] = None
    file_path: Optional[str] = None
    hash: Optional[str] = None

class OfflineLegalKnowledgeDownloader:
    """Downloads and stores Belgian legal codes for offline use"""
    
    def __init__(self, base_url: str = "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac="):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create directories
        self.data_dir = Path("offline_legal_knowledge")
        self.pdfs_dir = self.data_dir / "pdfs"
        self.content_dir = self.data_dir / "content"
        self.metadata_dir = self.data_dir / "metadata"
        self.database_path = self.data_dir / "legal_knowledge.db"
        
        for dir_path in [self.data_dir, self.pdfs_dir, self.content_dir, self.metadata_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Rate limiting
        self.request_delay = 1.0  # seconds between requests
        
    def _init_database(self):
        """Initialize SQLite database for storing legal knowledge"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS legal_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                english TEXT,
                french TEXT,
                german TEXT,
                url TEXT NOT NULL,
                category TEXT NOT NULL,
                pdf_url TEXT,
                content TEXT,
                last_updated TEXT,
                file_path TEXT,
                hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                legal_code_id INTEGER,
                status TEXT NOT NULL,
                error_message TEXT,
                download_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (legal_code_id) REFERENCES legal_codes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def get_legal_codes_from_justel(self) -> List[LegalCode]:
        """Scrape legal codes from the Justel website"""
        logger.info("Starting to scrape legal codes from Justel...")
        
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            legal_codes = []
            
            # Find all sections (Federal, Regional, Community codes)
            sections = soup.find_all(['h2', 'h3'])
            
            for section in sections:
                section_text = section.get_text(strip=True)
                
                # Determine category based on section
                if 'federale' in section_text.lower() or 'federal' in section_text.lower():
                    category = "Federal"
                elif 'regionale' in section_text.lower() or 'regional' in section_text.lower():
                    category = "Regional"
                elif 'gemeenschap' in section_text.lower() or 'community' in section_text.lower():
                    category = "Community"
                else:
                    continue
                
                # Find legal codes in this section
                next_element = section.find_next_sibling()
                while next_element and next_element.name not in ['h2', 'h3']:
                    if next_element.name == 'ul':
                        for li in next_element.find_all('li'):
                            code_info = self._extract_legal_code_info(li, category)
                            if code_info:
                                legal_codes.append(code_info)
                    next_element = next_element.find_next_sibling()
            
            logger.info(f"Found {len(legal_codes)} legal codes")
            return legal_codes
            
        except Exception as e:
            logger.error(f"Error scraping Justel website: {e}")
            return []
    
    def _extract_legal_code_info(self, li_element, category: str) -> Optional[LegalCode]:
        """Extract legal code information from a list item"""
        try:
            # Get the main text (name)
            name_text = li_element.get_text(strip=True)
            
            # Remove "pdf" and other metadata
            name = re.sub(r'\s*\([^)]*\)\s*$', '', name_text)
            name = re.sub(r'\s*pdf\s*$', '', name, flags=re.IGNORECASE)
            
            # Find PDF link
            pdf_link = li_element.find('a', href=True)
            pdf_url = None
            if pdf_link:
                pdf_url = urljoin(self.base_url, pdf_link['href'])
            
            # Create multilingual names (basic mapping)
            english = self._translate_name(name, 'en')
            french = self._translate_name(name, 'fr')
            german = self._translate_name(name, 'de')
            
            # Generate URL for the legal code
            code_url = self._generate_code_url(name)
            
            return LegalCode(
                name=name,
                english=english,
                french=french,
                german=german,
                url=code_url,
                category=category,
                pdf_url=pdf_url
            )
            
        except Exception as e:
            logger.error(f"Error extracting legal code info: {e}")
            return None
    
    def _translate_name(self, name: str, language: str) -> str:
        """Basic name translation (can be enhanced with proper translation service)"""
        translations = {
            'en': {
                'Burgerlijk Wetboek': 'Civil Code',
                'Strafwetboek': 'Criminal Code',
                'Gerechtelijk Wetboek': 'Judicial Code',
                'Wetboek van Koophandel': 'Commercial Code',
                'Wetboek van Strafvordering': 'Code of Criminal Procedure',
                'Sociaal Strafwetboek': 'Social Criminal Code',
                'Vlaamse Codex Fiscaliteit': 'Flemish Tax Code',
                'Vlaamse Codex ruimtelijke ordening': 'Flemish Spatial Planning Code',
                'Waals Wetboek van Sociale Actie en Gezondheid': 'Walloon Code of Social Action and Health',
                'Brussels Wetboek van Ruimtelijke Ordening': 'Brussels Spatial Planning Code'
            },
            'fr': {
                'Burgerlijk Wetboek': 'Code Civil',
                'Strafwetboek': 'Code Pénal',
                'Gerechtelijk Wetboek': 'Code Judiciaire',
                'Wetboek van Koophandel': 'Code de Commerce',
                'Wetboek van Strafvordering': 'Code d\'Instruction Criminelle',
                'Sociaal Strafwetboek': 'Code Pénal Social',
                'Vlaamse Codex Fiscaliteit': 'Code Fiscal Flamand',
                'Vlaamse Codex ruimtelijke ordening': 'Code Flamand de l\'Aménagement du Territoire',
                'Waals Wetboek van Sociale Actie en Gezondheid': 'Code Wallon de l\'Action Sociale et de la Santé',
                'Brussels Wetboek van Ruimtelijke Ordening': 'Code Bruxellois de l\'Aménagement du Territoire'
            },
            'de': {
                'Burgerlijk Wetboek': 'Bürgerliches Gesetzbuch',
                'Strafwetboek': 'Strafgesetzbuch',
                'Gerechtelijk Wetboek': 'Gerichtsgesetzbuch',
                'Wetboek van Koophandel': 'Handelsgesetzbuch',
                'Wetboek van Strafvordering': 'Strafprozessordnung',
                'Sociaal Strafwetboek': 'Sozialstrafgesetzbuch',
                'Vlaamse Codex Fiscaliteit': 'Flämisches Steuergesetzbuch',
                'Vlaamse Codex ruimtelijke ordening': 'Flämisches Raumordnungsgesetzbuch',
                'Waals Wetboek van Sociale Actie en Gezondheid': 'Wallonisches Gesetzbuch für Soziale Aktion und Gesundheit',
                'Brussels Wetboek van Ruimtelijke Ordening': 'Brüsseler Raumordnungsgesetzbuch'
            }
        }
        
        return translations.get(language, {}).get(name, name)
    
    def _generate_code_url(self, name: str) -> str:
        """Generate URL for a legal code"""
        # This is a simplified approach - in reality, you'd need to map to actual NUMAC codes
        base_url = "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac="
        
        # Common NUMAC codes (this would need to be expanded)
        numac_codes = {
            'Burgerlijk Wetboek': '1804050150',
            'Strafwetboek': '1867060850',
            'Gerechtelijk Wetboek': '1967101050',
            'Wetboek van Koophandel': '1807071750',
            'Wetboek van Strafvordering': '1878061550',
            'Sociaal Strafwetboek': '2010060150',
            'Vlaamse Codex Fiscaliteit': '2013035070',
            'Vlaamse Codex ruimtelijke ordening': '2014035070',
            'Waals Wetboek van Sociale Actie en Gezondheid': '2014035070',
            'Brussels Wetboek van Ruimtelijke Ordening': '2014035070'
        }
        
        numac = numac_codes.get(name, '')
        return f"{base_url}{numac}" if numac else base_url
    
    def download_pdf(self, legal_code: LegalCode) -> bool:
        """Download PDF for a legal code"""
        if not legal_code.pdf_url:
            logger.warning(f"No PDF URL for {legal_code.name}")
            return False
        
        try:
            logger.info(f"Downloading PDF for {legal_code.name}")
            
            # Create filename
            safe_name = re.sub(r'[^\w\s-]', '', legal_code.name).strip()
            safe_name = re.sub(r'[-\s]+', '-', safe_name)
            filename = f"{safe_name}_{legal_code.category.lower()}.pdf"
            file_path = self.pdfs_dir / filename
            
            # Download PDF
            response = self.session.get(legal_code.pdf_url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Calculate hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Update legal code
            legal_code.file_path = str(file_path)
            legal_code.hash = file_hash
            
            logger.info(f"Successfully downloaded PDF for {legal_code.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading PDF for {legal_code.name}: {e}")
            return False
    
    def extract_text_from_pdf(self, legal_code: LegalCode) -> bool:
        """Extract text content from PDF"""
        if not legal_code.file_path or not os.path.exists(legal_code.file_path):
            logger.warning(f"No PDF file found for {legal_code.name}")
            return False
        
        try:
            logger.info(f"Extracting text from PDF for {legal_code.name}")
            
            with open(legal_code.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- Page {page_num + 1} ---\n"
                            text_content += page_text
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                        continue
            
            # Save extracted text
            safe_name = re.sub(r'[^\w\s-]', '', legal_code.name).strip()
            safe_name = re.sub(r'[-\s]+', '-', safe_name)
            text_filename = f"{safe_name}_{legal_code.category.lower()}.txt"
            text_path = self.content_dir / text_filename
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            legal_code.content = text_content
            logger.info(f"Successfully extracted text from PDF for {legal_code.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF for {legal_code.name}: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def save_to_database(self, legal_codes: List[LegalCode]):
        """Save legal codes to database"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        for legal_code in legal_codes:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO legal_codes 
                    (name, english, french, german, url, category, pdf_url, content, last_updated, file_path, hash, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    legal_code.name,
                    legal_code.english,
                    legal_code.french,
                    legal_code.german,
                    legal_code.url,
                    legal_code.category,
                    legal_code.pdf_url,
                    legal_code.content,
                    legal_code.last_updated,
                    legal_code.file_path,
                    legal_code.hash
                ))
                
                # Log successful save
                legal_code_id = cursor.lastrowid
                cursor.execute('''
                    INSERT INTO download_log (legal_code_id, status)
                    VALUES (?, ?)
                ''', (legal_code_id, 'success'))
                
            except Exception as e:
                logger.error(f"Error saving {legal_code.name} to database: {e}")
                cursor.execute('''
                    INSERT INTO download_log (legal_code_id, status, error_message)
                    VALUES (?, ?, ?)
                ''', (None, 'error', str(e)))
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {len(legal_codes)} legal codes to database")
    
    def save_metadata(self, legal_codes: List[LegalCode]):
        """Save metadata to JSON file"""
        metadata = {
            'download_date': datetime.now().isoformat(),
            'total_codes': len(legal_codes),
            'categories': {},
            'legal_codes': [asdict(code) for code in legal_codes]
        }
        
        # Count by category
        for code in legal_codes:
            category = code.category
            if category not in metadata['categories']:
                metadata['categories'][category] = 0
            metadata['categories'][category] += 1
        
        metadata_path = self.metadata_dir / 'legal_codes_metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved metadata to {metadata_path}")
    
    def download_all_legal_codes(self, max_workers: int = 4):
        """Download all legal codes with parallel processing"""
        logger.info("Starting comprehensive legal knowledge base download...")
        
        # Step 1: Scrape legal codes from Justel
        legal_codes = self.get_legal_codes_from_justel()
        
        if not legal_codes:
            logger.error("No legal codes found. Exiting.")
            return
        
        logger.info(f"Found {len(legal_codes)} legal codes to download")
        
        # Step 2: Download PDFs in parallel
        logger.info("Downloading PDFs...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_code = {
                executor.submit(self.download_pdf, code): code 
                for code in legal_codes if code.pdf_url
            }
            
            for future in as_completed(future_to_code):
                code = future_to_code[future]
                try:
                    success = future.result()
                    if success:
                        logger.info(f"✓ Downloaded PDF for {code.name}")
                    else:
                        logger.warning(f"✗ Failed to download PDF for {code.name}")
                except Exception as e:
                    logger.error(f"Error downloading PDF for {code.name}: {e}")
        
        # Step 3: Extract text from PDFs
        logger.info("Extracting text from PDFs...")
        for code in legal_codes:
            if code.file_path:
                success = self.extract_text_from_pdf(code)
                if success:
                    logger.info(f"✓ Extracted text from {code.name}")
                else:
                    logger.warning(f"✗ Failed to extract text from {code.name}")
        
        # Step 4: Save to database and metadata
        logger.info("Saving to database and metadata...")
        self.save_to_database(legal_codes)
        self.save_metadata(legal_codes)
        
        # Step 5: Generate summary
        self._generate_summary(legal_codes)
        
        logger.info("Legal knowledge base download completed!")
    
    def _generate_summary(self, legal_codes: List[LegalCode]):
        """Generate a summary report"""
        summary = {
            'download_date': datetime.now().isoformat(),
            'total_codes': len(legal_codes),
            'categories': {},
            'successful_downloads': 0,
            'successful_extractions': 0,
            'total_size_mb': 0
        }
        
        for code in legal_codes:
            # Count by category
            category = code.category
            if category not in summary['categories']:
                summary['categories'][category] = 0
            summary['categories'][category] += 1
            
            # Count successful operations
            if code.file_path:
                summary['successful_downloads'] += 1
                if os.path.exists(code.file_path):
                    summary['total_size_mb'] += os.path.getsize(code.file_path) / (1024 * 1024)
            
            if code.content:
                summary['successful_extractions'] += 1
        
        summary_path = self.data_dir / 'download_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Download Summary:")
        logger.info(f"  Total codes: {summary['total_codes']}")
        logger.info(f"  Successful downloads: {summary['successful_downloads']}")
        logger.info(f"  Successful extractions: {summary['successful_extractions']}")
        logger.info(f"  Total size: {summary['total_size_mb']:.2f} MB")
        logger.info(f"  Categories: {summary['categories']}")

def main():
    """Main function to run the downloader"""
    print("🔍 Belgian Legal Knowledge Base Downloader")
    print("=" * 50)
    
    downloader = OfflineLegalKnowledgeDownloader()
    
    try:
        downloader.download_all_legal_codes()
        print("\n✅ Legal knowledge base download completed successfully!")
        print(f"📁 Data stored in: {downloader.data_dir}")
        print(f"🗄️  Database: {downloader.database_path}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Download interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during download: {e}")
        logger.error(f"Download failed: {e}")

if __name__ == "__main__":
    main() 