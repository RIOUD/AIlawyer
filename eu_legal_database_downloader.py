#!/usr/bin/env python3
"""
EU Legal Database Downloader

Specialized downloader for EU legal databases including:
- EUR-Lex (EU treaties, regulations, directives)
- European Court of Justice (ECJ judgments)
- European Commission legal acts
- European Parliament documents
- Council of the EU documents

This downloader handles EU-specific access patterns and authentication.
"""

import os
import sys
import requests
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse, parse_qs
import logging
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eu_legal_download.log'),
        logging.StreamHandler()
    ]
)

class EULegalDatabaseDownloader:
    """
    Specialized EU legal database downloader.
    """
    
    def __init__(self, base_dir: str = "./eu_legal_databases"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Session with EU-specific headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # EU legal sources with proper endpoints
        self.eu_sources = {
            "eur_lex": {
                "name": "EUR-Lex Database",
                "base_url": "https://eur-lex.europa.eu/",
                "search_url": "https://eur-lex.europa.eu/search.html",
                "api_url": "https://eur-lex.europa.eu/api/",
                "description": "EU treaties, regulations, directives, case law",
                "expected_documents": 100000,
                "date_range": "1950-2024"
            },
            "ecj": {
                "name": "European Court of Justice",
                "base_url": "https://curia.europa.eu/",
                "search_url": "https://curia.europa.eu/juris/",
                "api_url": "https://curia.europa.eu/juris/",
                "description": "ECJ judgments, opinions, orders",
                "expected_documents": 20000,
                "date_range": "1950-2024"
            },
            "commission": {
                "name": "European Commission",
                "base_url": "https://ec.europa.eu/info/law/",
                "search_url": "https://ec.europa.eu/info/law/legal-content",
                "api_url": "https://ec.europa.eu/info/law/",
                "description": "Commission decisions and regulations",
                "expected_documents": 30000,
                "date_range": "1990-2024"
            },
            "parliament": {
                "name": "European Parliament",
                "base_url": "https://www.europarl.europa.eu/",
                "search_url": "https://www.europarl.europa.eu/legislative-procedure/",
                "api_url": "https://www.europarl.europa.eu/",
                "description": "European Parliament documents",
                "expected_documents": 25000,
                "date_range": "1990-2024"
            },
            "council": {
                "name": "Council of the EU",
                "base_url": "https://www.consilium.europa.eu/",
                "search_url": "https://www.consilium.europa.eu/en/documents-publications/",
                "api_url": "https://www.consilium.europa.eu/",
                "description": "Council of the EU documents",
                "expected_documents": 20000,
                "date_range": "1990-2024"
            }
        }
        
        # Download statistics
        self.stats = {
            'total_downloaded': 0,
            'total_size': 0,
            'failed_downloads': 0,
            'start_time': datetime.now()
        }

    def create_eu_database_structure(self):
        """Creates directory structure for EU legal databases."""
        logging.info("Creating EU legal database structure...")
        
        for source_name in self.eu_sources.keys():
            source_dir = self.base_dir / source_name
            source_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            (source_dir / "pdfs").mkdir(exist_ok=True)
            (source_dir / "html").mkdir(exist_ok=True)
            (source_dir / "xml").mkdir(exist_ok=True)
            (source_dir / "metadata").mkdir(exist_ok=True)
        
        # Create utility directories
        (self.base_dir / "temp").mkdir(exist_ok=True)
        (self.base_dir / "logs").mkdir(exist_ok=True)
        (self.base_dir / "backups").mkdir(exist_ok=True)
        
        logging.info("EU database structure created successfully")

    def download_eur_lex_documents(self, target_dir: Path) -> List[Dict]:
        """
        Downloads documents from EUR-Lex using their API and search interface.
        
        Args:
            target_dir: Directory to save EUR-Lex documents
            
        Returns:
            List of downloaded document metadata
        """
        documents = []
        
        try:
            logging.info("Downloading EUR-Lex documents...")
            
            # EUR-Lex CELEX identifiers for major treaties and regulations
            celex_identifiers = [
                # Founding Treaties
                "12012E/TXT",  # Treaty on European Union
                "12012M/TXT",  # Treaty on the Functioning of the European Union
                "12012A/TXT",  # Treaty establishing the European Atomic Energy Community
                "12008E/TXT",  # Treaty of Lisbon
                "12006E/TXT",  # Treaty establishing a Constitution for Europe
                
                # Major Regulations
                "32016R0679",   # GDPR
                "32018R1725",   # Data Protection Regulation
                "32014R0596",   # Market Abuse Regulation
                "32013R0575",   # Banking Union
                "32012R0648",   # Common Agricultural Policy
                
                # Major Directives
                "32002L0058",   # E-commerce Directive
                "32000L0031",   # E-signatures Directive
                "32015L2366",   # Payment Services Directive 2
                "32014L0092",   # Payment Services Directive
                "32013L0034",   # Bank Recovery and Resolution Directive
            ]
            
            for celex_id in celex_identifiers:
                try:
                    # Try different EUR-Lex endpoints
                    urls_to_try = [
                        f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex_id}",
                        f"https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:{celex_id}",
                        f"https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:{celex_id}",
                        f"https://eur-lex.europa.eu/eli/reg/{celex_id}/oj",
                        f"https://eur-lex.europa.eu/eli/dir/{celex_id}/oj"
                    ]
                    
                    for url in urls_to_try:
                        try:
                            response = self.session.get(url, timeout=30)
                            if response.status_code == 200:
                                # Determine file type and extension
                                content_type = response.headers.get('content-type', '')
                                if 'pdf' in content_type.lower():
                                    ext = '.pdf'
                                    filename = f"eur_lex_{celex_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                                elif 'html' in content_type.lower():
                                    ext = '.html'
                                    filename = f"eur_lex_{celex_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                                else:
                                    ext = '.txt'
                                    filename = f"eur_lex_{celex_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                                
                                file_path = target_dir / "pdfs" / filename
                                
                                with open(file_path, 'wb') as f:
                                    f.write(response.content)
                                
                                # Create metadata
                                metadata = {
                                    "filename": filename,
                                    "url": url,
                                    "celex_id": celex_id,
                                    "title": f"EUR-Lex Document {celex_id}",
                                    "document_type": "eu_legal",
                                    "source": "eur_lex",
                                    "download_date": datetime.now().isoformat(),
                                    "file_size": file_path.stat().st_size,
                                    "language": "en"
                                }
                                
                                # Save metadata
                                metadata_file = target_dir / "metadata" / f"{file_path.stem}_metadata.json"
                                with open(metadata_file, 'w', encoding='utf-8') as f:
                                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                                
                                documents.append(metadata)
                                logging.info(f"Downloaded EUR-Lex document: {celex_id}")
                                break  # Success, move to next document
                                
                        except Exception as e:
                            logging.warning(f"Failed to download {celex_id} from {url}: {e}")
                            continue
                    
                    # Rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    logging.error(f"Failed to process CELEX ID {celex_id}: {e}")
                    continue
            
            return documents
            
        except Exception as e:
            logging.error(f"Failed to download EUR-Lex documents: {e}")
            return documents

    def download_ecj_documents(self, target_dir: Path) -> List[Dict]:
        """
        Downloads documents from European Court of Justice.
        
        Args:
            target_dir: Directory to save ECJ documents
            
        Returns:
            List of downloaded document metadata
        """
        documents = []
        
        try:
            logging.info("Downloading ECJ documents...")
            
            # ECJ case numbers for major judgments
            ecj_cases = [
                "C-131/12",  # Google Spain (Right to be forgotten)
                "C-362/14",  # Schrems I
                "C-311/18",  # Schrems II
                "C-40/17",   # Fashion ID
                "C-673/17",  # Planet49
                "C-136/17",  # GC and Others
                "C-507/17",  # Google LLC
                "C-210/16",  # Wirtschaftsakademie
                "C-25/17",   # Jehovan todistajat
                "C-61/19",   # Orange România
            ]
            
            for case in ecj_cases:
                try:
                    # Try different ECJ endpoints
                    urls_to_try = [
                        f"https://curia.europa.eu/juris/document/document.jsf?text=&docid={case}&pageIndex=0&doclang=EN&mode=req&dir=&occ=first&part=1&cid=",
                        f"https://curia.europa.eu/juris/liste.jsf?num={case}",
                        f"https://curia.europa.eu/juris/document/document.jsf?text=&docid={case}&pageIndex=0&doclang=EN&mode=lst&dir=&occ=first&part=1&cid="
                    ]
                    
                    for url in urls_to_try:
                        try:
                            response = self.session.get(url, timeout=30)
                            if response.status_code == 200:
                                # Save as HTML
                                filename = f"ecj_{case.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                                file_path = target_dir / "html" / filename
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(response.text)
                                
                                # Create metadata
                                metadata = {
                                    "filename": filename,
                                    "url": url,
                                    "case_number": case,
                                    "title": f"ECJ Case {case}",
                                    "document_type": "jurisprudence",
                                    "source": "ecj",
                                    "download_date": datetime.now().isoformat(),
                                    "file_size": file_path.stat().st_size,
                                    "language": "en"
                                }
                                
                                # Save metadata
                                metadata_file = target_dir / "metadata" / f"{file_path.stem}_metadata.json"
                                with open(metadata_file, 'w', encoding='utf-8') as f:
                                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                                
                                documents.append(metadata)
                                logging.info(f"Downloaded ECJ case: {case}")
                                break
                                
                        except Exception as e:
                            logging.warning(f"Failed to download {case} from {url}: {e}")
                            continue
                    
                    # Rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    logging.error(f"Failed to process ECJ case {case}: {e}")
                    continue
            
            return documents
            
        except Exception as e:
            logging.error(f"Failed to download ECJ documents: {e}")
            return documents

    def download_commission_documents(self, target_dir: Path) -> List[Dict]:
        """
        Downloads documents from European Commission.
        
        Args:
            target_dir: Directory to save Commission documents
            
        Returns:
            List of downloaded document metadata
        """
        documents = []
        
        try:
            logging.info("Downloading European Commission documents...")
            
            # Commission decision numbers
            commission_decisions = [
                "C(2023)1234",  # Example decision
                "C(2023)5678",  # Example decision
                "C(2022)9012",  # Example decision
            ]
            
            # Try to access Commission legal portal
            base_url = "https://ec.europa.eu/info/law/"
            
            try:
                response = self.session.get(base_url, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find document links
                    doc_links = soup.find_all('a', href=re.compile(r'\.(pdf|html|doc)$', re.I))
                    
                    for i, link in enumerate(doc_links[:20]):  # Limit to first 20
                        try:
                            href = link.get('href')
                            if not href:
                                continue
                            
                            # Make URL absolute
                            if href.startswith('/'):
                                doc_url = urljoin(base_url, href)
                            elif href.startswith('http'):
                                doc_url = href
                            else:
                                doc_url = urljoin(base_url, href)
                            
                            # Download document
                            doc_response = self.session.get(doc_url, timeout=30)
                            if doc_response.status_code == 200:
                                # Determine file extension
                                parsed_url = urlparse(doc_url)
                                ext = Path(parsed_url.path).suffix
                                if not ext:
                                    ext = '.html'
                                
                                filename = f"commission_doc_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                                file_path = target_dir / "pdfs" / filename
                                
                                with open(file_path, 'wb') as f:
                                    f.write(doc_response.content)
                                
                                # Create metadata
                                metadata = {
                                    "filename": filename,
                                    "url": doc_url,
                                    "title": link.get_text().strip() or f"Commission Document {i}",
                                    "document_type": "commission_decision",
                                    "source": "commission",
                                    "download_date": datetime.now().isoformat(),
                                    "file_size": file_path.stat().st_size,
                                    "language": "en"
                                }
                                
                                # Save metadata
                                metadata_file = target_dir / "metadata" / f"{file_path.stem}_metadata.json"
                                with open(metadata_file, 'w', encoding='utf-8') as f:
                                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                                
                                documents.append(metadata)
                                logging.info(f"Downloaded Commission document: {filename}")
                            
                            # Rate limiting
                            time.sleep(1)
                            
                        except Exception as e:
                            logging.warning(f"Failed to download Commission document: {e}")
                            continue
                            
            except Exception as e:
                logging.error(f"Failed to access Commission portal: {e}")
            
            return documents
            
        except Exception as e:
            logging.error(f"Failed to download Commission documents: {e}")
            return documents

    def download_comprehensive_eu_databases(self) -> Dict:
        """
        Downloads comprehensive EU legal databases from all sources.
        
        Returns:
            Dictionary containing download statistics
        """
        logging.info("Starting comprehensive EU legal database download...")
        
        all_documents = {}
        
        # Create database structure
        self.create_eu_database_structure()
        
        # Download from each EU source
        for source_name, source_config in self.eu_sources.items():
            logging.info(f"Processing {source_config['name']}...")
            
            target_dir = self.base_dir / source_name
            
            # Download based on source type
            if source_name == "eur_lex":
                documents = self.download_eur_lex_documents(target_dir)
            elif source_name == "ecj":
                documents = self.download_ecj_documents(target_dir)
            elif source_name == "commission":
                documents = self.download_commission_documents(target_dir)
            else:
                # For other sources, try basic scraping
                documents = self.scrape_eu_documents(source_config, target_dir)
            
            all_documents[source_name] = documents
            logging.info(f"Downloaded {len(documents)} documents from {source_name}")
            
            # Rate limiting between sources
            time.sleep(5)
        
        # Create comprehensive index
        self.create_eu_comprehensive_index(all_documents)
        
        # Generate final report
        self.generate_eu_comprehensive_report(all_documents)
        
        return all_documents

    def scrape_eu_documents(self, source_config: Dict, target_dir: Path) -> List[Dict]:
        """
        Basic scraping for EU documents.
        
        Args:
            source_config: Configuration for the EU source
            target_dir: Directory to save documents
            
        Returns:
            List of downloaded document metadata
        """
        documents = []
        
        try:
            base_url = source_config["base_url"]
            logging.info(f"Scraping documents from {base_url}")
            
            response = self.session.get(base_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find document links
                doc_links = soup.find_all('a', href=re.compile(r'\.(pdf|html|doc)$', re.I))
                
                for i, link in enumerate(doc_links[:10]):  # Limit to first 10
                    try:
                        href = link.get('href')
                        if not href:
                            continue
                        
                        # Make URL absolute
                        if href.startswith('/'):
                            doc_url = urljoin(base_url, href)
                        elif href.startswith('http'):
                            doc_url = href
                        else:
                            doc_url = urljoin(base_url, href)
                        
                        # Download document
                        doc_response = self.session.get(doc_url, timeout=30)
                        if doc_response.status_code == 200:
                            # Determine file extension
                            parsed_url = urlparse(doc_url)
                            ext = Path(parsed_url.path).suffix
                            if not ext:
                                ext = '.html'
                            
                            filename = f"{source_config['name'].lower().replace(' ', '_')}_doc_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                            file_path = target_dir / "pdfs" / filename
                            
                            with open(file_path, 'wb') as f:
                                f.write(doc_response.content)
                            
                            # Create metadata
                            metadata = {
                                "filename": filename,
                                "url": doc_url,
                                "title": link.get_text().strip() or f"{source_config['name']} Document {i}",
                                "document_type": "eu_legal",
                                "source": source_config['name'].lower().replace(' ', '_'),
                                "download_date": datetime.now().isoformat(),
                                "file_size": file_path.stat().st_size,
                                "language": "en"
                            }
                            
                            # Save metadata
                            metadata_file = target_dir / "metadata" / f"{file_path.stem}_metadata.json"
                            with open(metadata_file, 'w', encoding='utf-8') as f:
                                json.dump(metadata, f, indent=2, ensure_ascii=False)
                            
                            documents.append(metadata)
                            logging.info(f"Downloaded {source_config['name']} document: {filename}")
                        
                        # Rate limiting
                        time.sleep(1)
                        
                    except Exception as e:
                        logging.warning(f"Failed to download {source_config['name']} document: {e}")
                        continue
                        
        except Exception as e:
            logging.error(f"Failed to scrape {source_config['name']}: {e}")
        
        return documents

    def create_eu_comprehensive_index(self, all_documents: Dict):
        """Creates a comprehensive index of all downloaded EU documents."""
        logging.info("Creating comprehensive EU document index...")
        
        index = {
            "created_date": datetime.now().isoformat(),
            "total_documents": 0,
            "total_size": 0,
            "sources": {},
            "document_types": {},
            "languages": {}
        }
        
        # Process all documents
        for source_name, documents in all_documents.items():
            source_total = len(documents)
            source_size = sum(doc.get('file_size', 0) for doc in documents)
            
            index["total_documents"] += source_total
            index["total_size"] += source_size
            
            index["sources"][source_name] = {
                "documents": source_total,
                "size": source_size
            }
        
        # Save index
        index_file = self.base_dir / "eu_comprehensive_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        logging.info(f"EU comprehensive index created: {index['total_documents']} documents")

    def generate_eu_comprehensive_report(self, all_documents: Dict):
        """Generates a comprehensive EU download report."""
        logging.info("Generating comprehensive EU download report...")
        
        total_docs = sum(len(docs) for docs in all_documents.values())
        total_size = sum(
            sum(doc.get('file_size', 0) for doc in docs)
            for docs in all_documents.values()
        )
        
        report = f"""
# EU Legal Database Download Report

## Download Summary
- **Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Total Documents**: {total_docs:,}
- **Total Size**: {total_size / (1024*1024):.2f} MB
- **Download Duration**: {datetime.now() - self.stats['start_time']}
- **Success Rate**: {(total_docs - self.stats['failed_downloads']) / total_docs * 100 if total_docs > 0 else 0.0:.1f}%

## EU Database Breakdown
"""
        
        for source_name, documents in all_documents.items():
            report += f"\n### {self.eu_sources[source_name]['name']}\n"
            report += f"- **Total Documents**: {len(documents):,}\n"
            report += f"- **Description**: {self.eu_sources[source_name]['description']}\n"
        
        report += f"""
## Download Statistics
- **Successfully Downloaded**: {total_docs - self.stats['failed_downloads']:,}
- **Failed Downloads**: {self.stats['failed_downloads']:,}
- **Total Data Size**: {total_size / (1024*1024):.2f} MB

## Next Steps
1. Run document processing: `python3 ingest.py`
2. Start legal assistant: `python3 app.py`
3. Begin comprehensive offline legal research

## Usage Instructions
- All documents are stored in: {self.base_dir}
- Use the legal assistant with filters for specific jurisdictions
- Search in Dutch, French, or English
- All research is 100% offline and confidential
"""
        
        # Save report
        report_file = self.base_dir / "eu_comprehensive_download_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logging.info(f"EU comprehensive report saved to {report_file}")
        print(report)

    def run_eu_comprehensive_download(self):
        """Runs the complete EU legal database download."""
        print("🏛️  EU Legal Database Download System")
        print("=" * 50)
        print("This will download comprehensive EU legal databases.")
        print("The process may take several minutes depending on your internet connection.")
        print()
        
        # Confirm with user
        response = input("Do you want to proceed with downloading EU legal databases? (y/N): ")
        if response.lower() != 'y':
            print("Download cancelled.")
            return
        
        try:
            # Start comprehensive download
            all_documents = self.download_comprehensive_eu_databases()
            
            print("\n🎉 EU legal database download completed!")
            print("=" * 50)
            print(f"Total documents downloaded: {sum(len(docs) for docs in all_documents.values()):,}")
            print(f"Database location: {self.base_dir}")
            print("\nYou can now integrate these EU databases with your legal assistant system.")
            
        except Exception as e:
            logging.error(f"EU comprehensive download failed: {e}")
            print(f"\n❌ Download failed: {e}")


def main():
    """Main function to run EU legal database download."""
    downloader = EULegalDatabaseDownloader()
    downloader.run_eu_comprehensive_download()


if __name__ == "__main__":
    main() 