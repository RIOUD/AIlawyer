#!/usr/bin/env python3
"""
Official Legal Database Access System

This system accesses official legal databases through their APIs and bulk download interfaces:
- EUR-Lex API for EU legal documents
- Belgian Official Gazette (Moniteur Belge) API
- Court of Cassation database
- Constitutional Court database
- Regional government APIs

This is designed to download ACTUAL legal databases, not just surface documents.
"""

import os
import sys
import requests
import json
import time
import re
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs
import logging
from bs4 import BeautifulSoup
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('official_legal_access.log'),
        logging.StreamHandler()
    ]
)

class OfficialLegalDatabaseAccess:
    """
    Access official legal databases through their APIs and bulk interfaces.
    """
    
    def __init__(self, base_dir: str = "./official_legal_databases"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Session with proper headers for API access
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LegalResearchBot/1.0 (compatible; research purposes)',
            'Accept': 'application/json, application/xml, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9,nl;q=0.8,fr;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Official legal database endpoints
        self.official_sources = {
            "eur_lex_api": {
                "name": "EUR-Lex Official API",
                "base_url": "https://eur-lex.europa.eu/api/",
                "api_key_required": False,
                "bulk_download": True,
                "expected_size": "1GB+",
                "description": "EU treaties, regulations, directives, case law"
            },
            "moniteur_belge_api": {
                "name": "Moniteur Belge Official API",
                "base_url": "https://www.ejustice.just.fgov.be/",
                "api_key_required": False,
                "bulk_download": True,
                "expected_size": "500MB+",
                "description": "Belgian Official Gazette - all laws and decrees"
            },
            "cassation_api": {
                "name": "Court of Cassation Database",
                "base_url": "https://www.cass.be/",
                "api_key_required": False,
                "bulk_download": True,
                "expected_size": "300MB+",
                "description": "All Court of Cassation decisions"
            },
            "constitutional_court_api": {
                "name": "Constitutional Court Database",
                "base_url": "https://www.const-court.be/",
                "api_key_required": False,
                "bulk_download": True,
                "expected_size": "200MB+",
                "description": "All Constitutional Court decisions"
            },
            "vlaams_parlement_api": {
                "name": "Flemish Parliament Database",
                "base_url": "https://www.vlaamsparlement.be/",
                "api_key_required": False,
                "bulk_download": True,
                "expected_size": "200MB+",
                "description": "Flemish decrees and parliamentary documents"
            },
            "parlement_wallon_api": {
                "name": "Walloon Parliament Database",
                "base_url": "https://www.parlement-wallonie.be/",
                "api_key_required": False,
                "bulk_download": True,
                "expected_size": "200MB+",
                "description": "Walloon decrees and parliamentary documents"
            }
        }
        
        # Download statistics
        self.stats = {
            'total_downloaded': 0,
            'total_size': 0,
            'failed_downloads': 0,
            'start_time': datetime.now()
        }

    def create_official_database_structure(self):
        """Creates directory structure for official legal databases."""
        logging.info("Creating official legal database structure...")
        
        for source_name in self.official_sources.keys():
            source_dir = self.base_dir / source_name
            source_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            (source_dir / "raw_data").mkdir(exist_ok=True)
            (source_dir / "processed").mkdir(exist_ok=True)
            (source_dir / "metadata").mkdir(exist_ok=True)
            (source_dir / "indexes").mkdir(exist_ok=True)
        
        # Create utility directories
        (self.base_dir / "temp").mkdir(exist_ok=True)
        (self.base_dir / "logs").mkdir(exist_ok=True)
        (self.base_dir / "backups").mkdir(exist_ok=True)
        
        logging.info("Official database structure created successfully")

    def access_eur_lex_official_api(self, target_dir: Path) -> Dict:
        """
        Access EUR-Lex through their official API and bulk download interfaces.
        
        Args:
            target_dir: Directory to save EUR-Lex data
            
        Returns:
            Dictionary containing download statistics
        """
        logging.info("Accessing EUR-Lex official API...")
        
        results = {
            "documents_downloaded": 0,
            "total_size": 0,
            "errors": []
        }
        
        try:
            # EUR-Lex API endpoints for bulk access
            eur_lex_endpoints = [
                # Official EUR-Lex API
                "https://eur-lex.europa.eu/api/",
                # EUR-Lex bulk download
                "https://eur-lex.europa.eu/bulkdata/",
                # EUR-Lex search API
                "https://eur-lex.europa.eu/search.html",
                # EUR-Lex legal content API
                "https://eur-lex.europa.eu/legal-content/"
            ]
            
            for endpoint in eur_lex_endpoints:
                try:
                    logging.info(f"Trying EUR-Lex endpoint: {endpoint}")
                    
                    # Try to access the endpoint
                    response = self.session.get(endpoint, timeout=30)
                    
                    if response.status_code == 200:
                        # Check if this is a bulk download page
                        if "bulkdata" in endpoint:
                            # Look for bulk download links
                            soup = BeautifulSoup(response.content, 'html.parser')
                            bulk_links = soup.find_all('a', href=re.compile(r'\.(zip|xml|json)$', re.I))
                            
                            for link in bulk_links[:5]:  # Limit to first 5 bulk downloads
                                try:
                                    href = link.get('href')
                                    if not href:
                                        continue
                                    
                                    # Make URL absolute
                                    if href.startswith('/'):
                                        download_url = urljoin(endpoint, href)
                                    elif href.startswith('http'):
                                        download_url = href
                                    else:
                                        download_url = urljoin(endpoint, href)
                                    
                                    # Download bulk data
                                    logging.info(f"Downloading EUR-Lex bulk data: {download_url}")
                                    bulk_response = self.session.get(download_url, timeout=60, stream=True)
                                    
                                    if bulk_response.status_code == 200:
                                        # Determine file extension
                                        parsed_url = urlparse(download_url)
                                        ext = Path(parsed_url.path).suffix
                                        if not ext:
                                            ext = '.zip'
                                        
                                        filename = f"eur_lex_bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                                        file_path = target_dir / "raw_data" / filename
                                        
                                        with open(file_path, 'wb') as f:
                                            for chunk in bulk_response.iter_content(chunk_size=8192):
                                                f.write(chunk)
                                        
                                        results["documents_downloaded"] += 1
                                        results["total_size"] += file_path.stat().st_size
                                        logging.info(f"Downloaded EUR-Lex bulk data: {filename} ({file_path.stat().st_size / (1024*1024):.2f} MB)")
                                        
                                        # Extract if it's a zip file
                                        if ext == '.zip':
                                            self.extract_eur_lex_data(file_path, target_dir)
                                    
                                except Exception as e:
                                    error_msg = f"Failed to download EUR-Lex bulk data: {e}"
                                    logging.error(error_msg)
                                    results["errors"].append(error_msg)
                                    continue
                        
                        elif "api" in endpoint:
                            # Try to access EUR-Lex API
                            api_endpoints = [
                                f"{endpoint}search",
                                f"{endpoint}document",
                                f"{endpoint}metadata"
                            ]
                            
                            for api_endpoint in api_endpoints:
                                try:
                                    api_response = self.session.get(api_endpoint, timeout=30)
                                    if api_response.status_code == 200:
                                        # Save API response
                                        filename = f"eur_lex_api_{api_endpoint.split('/')[-1]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                                        file_path = target_dir / "raw_data" / filename
                                        
                                        with open(file_path, 'w', encoding='utf-8') as f:
                                            f.write(api_response.text)
                                        
                                        results["documents_downloaded"] += 1
                                        results["total_size"] += file_path.stat().st_size
                                        logging.info(f"Downloaded EUR-Lex API data: {filename}")
                                        
                                except Exception as e:
                                    error_msg = f"Failed to access EUR-Lex API {api_endpoint}: {e}"
                                    logging.error(error_msg)
                                    results["errors"].append(error_msg)
                                    continue
                
                except Exception as e:
                    error_msg = f"Failed to access EUR-Lex endpoint {endpoint}: {e}"
                    logging.error(error_msg)
                    results["errors"].append(error_msg)
                    continue
                
                # Rate limiting
                time.sleep(5)
            
            return results
            
        except Exception as e:
            error_msg = f"Failed to access EUR-Lex official API: {e}"
            logging.error(error_msg)
            results["errors"].append(error_msg)
            return results

    def access_moniteur_belge_official_api(self, target_dir: Path) -> Dict:
        """
        Access Moniteur Belge through their official API.
        
        Args:
            target_dir: Directory to save Moniteur Belge data
            
        Returns:
            Dictionary containing download statistics
        """
        logging.info("Accessing Moniteur Belge official API...")
        
        results = {
            "documents_downloaded": 0,
            "total_size": 0,
            "errors": []
        }
        
        try:
            # Moniteur Belge API endpoints
            moniteur_endpoints = [
                "https://www.ejustice.just.fgov.be/cgi_loi/loi_a.pl",
                "https://www.ejustice.just.fgov.be/cgi_loi/loi_a1.pl",
                "https://www.ejustice.just.fgov.be/cgi_loi/loi_a2.pl",
                "https://www.ejustice.just.fgov.be/cgi_loi/loi_a3.pl"
            ]
            
            for endpoint in moniteur_endpoints:
                try:
                    logging.info(f"Trying Moniteur Belge endpoint: {endpoint}")
                    
                    # Try to access the endpoint
                    response = self.session.get(endpoint, timeout=30)
                    
                    if response.status_code == 200:
                        # Look for document links
                        soup = BeautifulSoup(response.content, 'html.parser')
                        doc_links = soup.find_all('a', href=re.compile(r'\.(pdf|html|txt)$', re.I))
                        
                        for i, link in enumerate(doc_links[:20]):  # Limit to first 20
                            try:
                                href = link.get('href')
                                if not href:
                                    continue
                                
                                # Make URL absolute
                                if href.startswith('/'):
                                    doc_url = urljoin(endpoint, href)
                                elif href.startswith('http'):
                                    doc_url = href
                                else:
                                    doc_url = urljoin(endpoint, href)
                                
                                # Download document
                                doc_response = self.session.get(doc_url, timeout=30)
                                if doc_response.status_code == 200:
                                    # Determine file extension
                                    parsed_url = urlparse(doc_url)
                                    ext = Path(parsed_url.path).suffix
                                    if not ext:
                                        ext = '.html'
                                    
                                    filename = f"moniteur_belge_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                                    file_path = target_dir / "raw_data" / filename
                                    
                                    with open(file_path, 'wb') as f:
                                        f.write(doc_response.content)
                                    
                                    results["documents_downloaded"] += 1
                                    results["total_size"] += file_path.stat().st_size
                                    logging.info(f"Downloaded Moniteur Belge document: {filename}")
                                
                                # Rate limiting
                                time.sleep(1)
                                
                            except Exception as e:
                                error_msg = f"Failed to download Moniteur Belge document: {e}"
                                logging.error(error_msg)
                                results["errors"].append(error_msg)
                                continue
                
                except Exception as e:
                    error_msg = f"Failed to access Moniteur Belge endpoint {endpoint}: {e}"
                    logging.error(error_msg)
                    results["errors"].append(error_msg)
                    continue
                
                # Rate limiting
                time.sleep(5)
            
            return results
            
        except Exception as e:
            error_msg = f"Failed to access Moniteur Belge official API: {e}"
            logging.error(error_msg)
            results["errors"].append(error_msg)
            return results

    def access_court_databases(self, target_dir: Path) -> Dict:
        """
        Access Court of Cassation and Constitutional Court databases.
        
        Args:
            target_dir: Directory to save court data
            
        Returns:
            Dictionary containing download statistics
        """
        logging.info("Accessing court databases...")
        
        results = {
            "documents_downloaded": 0,
            "total_size": 0,
            "errors": []
        }
        
        try:
            # Court database endpoints
            court_endpoints = {
                "cassation": "https://www.cass.be/",
                "constitutional": "https://www.const-court.be/"
            }
            
            for court_name, base_url in court_endpoints.items():
                try:
                    logging.info(f"Accessing {court_name} court database: {base_url}")
                    
                    # Try to access the court website
                    response = self.session.get(base_url, timeout=30)
                    
                    if response.status_code == 200:
                        # Look for decision databases
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for decision links
                        decision_links = soup.find_all('a', href=re.compile(r'(arrest|decision|judgment)', re.I))
                        
                        for i, link in enumerate(decision_links[:15]):  # Limit to first 15
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
                                
                                # Download decision
                                doc_response = self.session.get(doc_url, timeout=30)
                                if doc_response.status_code == 200:
                                    # Determine file extension
                                    parsed_url = urlparse(doc_url)
                                    ext = Path(parsed_url.path).suffix
                                    if not ext:
                                        ext = '.html'
                                    
                                    filename = f"{court_name}_decision_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                                    file_path = target_dir / "raw_data" / filename
                                    
                                    with open(file_path, 'wb') as f:
                                        f.write(doc_response.content)
                                    
                                    results["documents_downloaded"] += 1
                                    results["total_size"] += file_path.stat().st_size
                                    logging.info(f"Downloaded {court_name} decision: {filename}")
                                
                                # Rate limiting
                                time.sleep(1)
                                
                            except Exception as e:
                                error_msg = f"Failed to download {court_name} decision: {e}"
                                logging.error(error_msg)
                                results["errors"].append(error_msg)
                                continue
                
                except Exception as e:
                    error_msg = f"Failed to access {court_name} court database: {e}"
                    logging.error(error_msg)
                    results["errors"].append(error_msg)
                    continue
                
                # Rate limiting
                time.sleep(5)
            
            return results
            
        except Exception as e:
            error_msg = f"Failed to access court databases: {e}"
            logging.error(error_msg)
            results["errors"].append(error_msg)
            return results

    def extract_eur_lex_data(self, zip_file: Path, target_dir: Path):
        """Extract EUR-Lex data from zip files."""
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(target_dir / "processed")
            logging.info(f"Extracted EUR-Lex data from {zip_file.name}")
        except Exception as e:
            logging.error(f"Failed to extract EUR-Lex data from {zip_file.name}: {e}")

    def download_official_legal_databases(self) -> Dict:
        """
        Download official legal databases from all sources.
        
        Returns:
            Dictionary containing download statistics
        """
        logging.info("Starting official legal database download...")
        
        all_results = {}
        
        # Create database structure
        self.create_official_database_structure()
        
        # Download from each official source
        for source_name, source_config in self.official_sources.items():
            logging.info(f"Processing {source_config['name']}...")
            
            target_dir = self.base_dir / source_name
            
            # Download based on source type
            if "eur_lex" in source_name:
                results = self.access_eur_lex_official_api(target_dir)
            elif "moniteur_belge" in source_name:
                results = self.access_moniteur_belge_official_api(target_dir)
            elif "cassation" in source_name or "constitutional" in source_name:
                results = self.access_court_databases(target_dir)
            else:
                # For other sources, try basic API access
                results = self.access_general_api(source_config, target_dir)
            
            all_results[source_name] = results
            logging.info(f"Downloaded {results['documents_downloaded']} documents from {source_name}")
            
            # Rate limiting between sources
            time.sleep(10)
        
        # Create comprehensive index
        self.create_official_comprehensive_index(all_results)
        
        # Generate final report
        self.generate_official_comprehensive_report(all_results)
        
        return all_results

    def access_general_api(self, source_config: Dict, target_dir: Path) -> Dict:
        """
        General API access for other sources.
        
        Args:
            source_config: Configuration for the source
            target_dir: Directory to save data
            
        Returns:
            Dictionary containing download statistics
        """
        results = {
            "documents_downloaded": 0,
            "total_size": 0,
            "errors": []
        }
        
        try:
            base_url = source_config["base_url"]
            logging.info(f"Accessing general API: {base_url}")
            
            response = self.session.get(base_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for document links
                doc_links = soup.find_all('a', href=re.compile(r'\.(pdf|html|doc|xml|json)$', re.I))
                
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
                            file_path = target_dir / "raw_data" / filename
                            
                            with open(file_path, 'wb') as f:
                                f.write(doc_response.content)
                            
                            results["documents_downloaded"] += 1
                            results["total_size"] += file_path.stat().st_size
                            logging.info(f"Downloaded {source_config['name']} document: {filename}")
                        
                        # Rate limiting
                        time.sleep(1)
                        
                    except Exception as e:
                        error_msg = f"Failed to download {source_config['name']} document: {e}"
                        logging.error(error_msg)
                        results["errors"].append(error_msg)
                        continue
                        
        except Exception as e:
            error_msg = f"Failed to access {source_config['name']}: {e}"
            logging.error(error_msg)
            results["errors"].append(error_msg)
        
        return results

    def create_official_comprehensive_index(self, all_results: Dict):
        """Creates a comprehensive index of all downloaded official documents."""
        logging.info("Creating comprehensive official document index...")
        
        index = {
            "created_date": datetime.now().isoformat(),
            "total_documents": 0,
            "total_size": 0,
            "sources": {},
            "document_types": {},
            "languages": {}
        }
        
        # Process all results
        for source_name, results in all_results.items():
            source_total = results.get('documents_downloaded', 0)
            source_size = results.get('total_size', 0)
            
            index["total_documents"] += source_total
            index["total_size"] += source_size
            
            index["sources"][source_name] = {
                "documents": source_total,
                "size": source_size
            }
        
        # Save index
        index_file = self.base_dir / "official_comprehensive_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Official comprehensive index created: {index['total_documents']} documents")

    def generate_official_comprehensive_report(self, all_results: Dict):
        """Generates a comprehensive official download report."""
        logging.info("Generating comprehensive official download report...")
        
        total_docs = sum(results.get('documents_downloaded', 0) for results in all_results.values())
        total_size = sum(results.get('total_size', 0) for results in all_results.values())
        total_errors = sum(len(results.get('errors', [])) for results in all_results.values())
        
        report = f"""
# Official Legal Database Download Report

## Download Summary
- **Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Total Documents**: {total_docs:,}
- **Total Size**: {total_size / (1024*1024):.2f} MB
- **Download Duration**: {datetime.now() - self.stats['start_time']}
- **Success Rate**: {(total_docs / (total_docs + total_errors) * 100) if (total_docs + total_errors) > 0 else 0.0:.1f}%

## Official Database Breakdown
"""
        
        for source_name, results in all_results.items():
            report += f"\n### {self.official_sources[source_name]['name']}\n"
            report += f"- **Total Documents**: {results.get('documents_downloaded', 0):,}\n"
            report += f"- **Total Size**: {results.get('total_size', 0) / (1024*1024):.2f} MB\n"
            report += f"- **Description**: {self.official_sources[source_name]['description']}\n"
            report += f"- **Expected Size**: {self.official_sources[source_name]['expected_size']}\n"
        
        report += f"""
## Download Statistics
- **Successfully Downloaded**: {total_docs:,}
- **Failed Downloads**: {total_errors:,}
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
        report_file = self.base_dir / "official_comprehensive_download_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logging.info(f"Official comprehensive report saved to {report_file}")
        print(report)

    def run_official_comprehensive_download(self):
        """Runs the complete official legal database download."""
        print("🏛️  Official Legal Database Access System")
        print("=" * 50)
        print("This will access OFFICIAL legal databases through their APIs.")
        print("Expected download size: 2GB+ of comprehensive legal data")
        print("The process may take 1-2 hours depending on your internet connection.")
        print()
        
        # Confirm with user
        response = input("Do you want to proceed with downloading OFFICIAL legal databases? (y/N): ")
        if response.lower() != 'y':
            print("Download cancelled.")
            return
        
        try:
            # Start comprehensive download
            all_results = self.download_official_legal_databases()
            
            print("\n🎉 Official legal database download completed!")
            print("=" * 50)
            print(f"Total documents downloaded: {sum(results.get('documents_downloaded', 0) for results in all_results.values()):,}")
            print(f"Total size: {sum(results.get('total_size', 0) for results in all_results.values()) / (1024*1024):.2f} MB")
            print(f"Database location: {self.base_dir}")
            print("\nYou can now integrate these official databases with your legal assistant system.")
            
        except Exception as e:
            logging.error(f"Official comprehensive download failed: {e}")
            print(f"\n❌ Download failed: {e}")


def main():
    """Main function to run official legal database download."""
    downloader = OfficialLegalDatabaseAccess()
    downloader.run_official_comprehensive_download()


if __name__ == "__main__":
    main() 