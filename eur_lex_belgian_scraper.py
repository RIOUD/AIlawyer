#!/usr/bin/env python3
"""
EUR-Lex Belgian Legal Database Scraper - Robust Version

This robust scraper accesses the EUR-Lex Belgian national transposition measures database
and downloads documents systematically using proper pagination and error handling.
"""

import os
import sys
import requests
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse, parse_qs
import logging
from bs4 import BeautifulSoup
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eur_lex_belgian_scraper.log'),
        logging.StreamHandler()
    ]
)

class EURLexBelgianScraper:
    """
    Robust EUR-Lex Belgian legal database scraper with systematic pagination.
    """
    
    def __init__(self, base_dir: str = "./eur_lex_belgian_databases"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # Session with EUR-Lex specific headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,nl;q=0.8,fr;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
        # EUR-Lex Belgian search URLs - focusing on working searches
        self.eur_lex_searches = {
            "belgian_national_transposition": {
                "name": "Belgian National Transposition Measures",
                "base_url": "https://eur-lex.europa.eu/search.html",
                "params": {
                    "SUBDOM_INIT": "MNE",
                    "DB_AUTHOR": "BEL",
                    "DTS_SUBDOM": "MNE",
                    "DTS_DOM": "NATIONAL_LAW",
                    "lang": "en",
                    "type": "advanced"
                },
                "expected_documents": 10083,
                "description": "Belgian national transposition measures of EU directives",
                "max_pages": 1000,  # Increased for comprehensive coverage
                "documents_per_page": 10
            }
        }
        
        # Download statistics
        self.stats = {
            'total_downloaded': 0,
            'total_size': 0,
            'failed_downloads': 0,
            'start_time': datetime.now(),
            'downloaded_celex_ids': set()  # Track downloaded documents to avoid duplicates
        }
        
        # Rate limiting configuration
        self.rate_limits = {
            'request_delay': (2, 4),  # Random delay between requests (2-4 seconds)
            'page_delay': (5, 8),     # Delay between pages (5-8 seconds)
            'search_delay': (15, 20), # Delay between searches (15-20 seconds)
            'max_retries': 3,         # Maximum retries for failed requests
            'retry_delay': (10, 15)   # Delay before retry (10-15 seconds)
        }

    def create_eur_lex_structure(self):
        """Creates directory structure for EUR-Lex Belgian databases."""
        logging.info("Creating EUR-Lex Belgian database structure...")
        
        for search_name in self.eur_lex_searches.keys():
            search_dir = self.base_dir / search_name
            search_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            (search_dir / "documents").mkdir(exist_ok=True)
            (search_dir / "metadata").mkdir(exist_ok=True)
            (search_dir / "indexes").mkdir(exist_ok=True)
        
        # Create utility directories
        (self.base_dir / "temp").mkdir(exist_ok=True)
        (self.base_dir / "logs").mkdir(exist_ok=True)
        
        logging.info("EUR-Lex Belgian database structure created successfully")

    def get_with_retry(self, url: str, max_retries: int = None) -> Optional[requests.Response]:
        """Makes HTTP request with retry logic and rate limiting."""
        if max_retries is None:
            max_retries = self.rate_limits['max_retries']
        
        for attempt in range(max_retries + 1):
            try:
                # Random delay to avoid detection
                delay = random.uniform(*self.rate_limits['request_delay'])
                time.sleep(delay)
                
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    retry_delay = random.uniform(*self.rate_limits['retry_delay'])
                    logging.warning(f"Rate limited, waiting {retry_delay:.1f} seconds...")
                    time.sleep(retry_delay)
                elif response.status_code == 500:  # Server error
                    logging.warning(f"Server error (500) for {url}, attempt {attempt + 1}")
                    if attempt < max_retries:
                        retry_delay = random.uniform(*self.rate_limits['retry_delay'])
                        time.sleep(retry_delay)
                else:
                    logging.warning(f"HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt < max_retries:
                    retry_delay = random.uniform(*self.rate_limits['retry_delay'])
                    time.sleep(retry_delay)
        
        logging.error(f"Failed to fetch {url} after {max_retries + 1} attempts")
        return None

    def extract_celex_id(self, href: str) -> Optional[str]:
        """Extracts CELEX ID from EUR-Lex URL."""
        # Multiple patterns for CELEX IDs
        patterns = [
            r'(\d{4}[A-Z]\d{4}[A-Z]*\d*)',  # Standard format: 72008L0099BEL_186318
            r'(\d{4}[A-Z]\d{4}[A-Z]*)',     # Without suffix: 72008L0099BEL
            r'CELEX:(\d{4}[A-Z]\d{4}[A-Z]*\d*)',  # With CELEX: prefix
        ]
        
        for pattern in patterns:
            match = re.search(pattern, href)
            if match:
                return match.group(1)
        
        return None

    def build_search_url(self, search_config: Dict, page: int = 1) -> str:
        """Builds EUR-Lex search URL with parameters."""
        base_url = search_config['base_url']
        params = search_config['params'].copy()
        params['page'] = page
        
        # Build query string
        query_parts = []
        for key, value in params.items():
            query_parts.append(f"{key}={value}")
        
        return f"{base_url}?{'&'.join(query_parts)}"

    def scrape_eur_lex_page(self, page_url: str, target_dir: Path, results: Dict, search_config: Dict) -> int:
        """
        Scrapes a single EUR-Lex page for documents.
        
        Returns:
            Number of documents downloaded from this page
        """
        documents_downloaded = 0
        
        try:
            logging.info(f"Scraping page: {page_url}")
            
            response = self.get_with_retry(page_url)
            if not response:
                return 0
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find document links - look for legal-content links with CELEX IDs
            document_links = soup.find_all('a', href=re.compile(r'legal-content.*CELEX.*BEL'))
            
            logging.info(f"Found {len(document_links)} document links on page")
            
            # Process each document link
            for link in document_links:
                try:
                    href = link.get('href')
                    if not href:
                        continue
                    
                    # Make URL absolute
                    if href.startswith('./'):
                        doc_url = urljoin("https://eur-lex.europa.eu/", href)
                    elif href.startswith('/'):
                        doc_url = urljoin("https://eur-lex.europa.eu/", href)
                    elif href.startswith('http'):
                        doc_url = href
                    else:
                        doc_url = urljoin("https://eur-lex.europa.eu/", href)
                    
                    # Extract CELEX ID
                    celex_id = self.extract_celex_id(href)
                    if not celex_id:
                        continue
                    
                    # Skip if already downloaded
                    if celex_id in self.stats['downloaded_celex_ids']:
                        continue
                    
                    # Download document
                    doc_response = self.get_with_retry(doc_url)
                    if doc_response and doc_response.status_code == 200:
                        # Determine file extension
                        content_type = doc_response.headers.get('content-type', '')
                        if 'pdf' in content_type.lower():
                            ext = '.pdf'
                        elif 'html' in content_type.lower():
                            ext = '.html'
                        else:
                            ext = '.html'
                        
                        filename = f"eur_lex_{celex_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                        file_path = target_dir / "documents" / filename
                        
                        with open(file_path, 'wb') as f:
                            f.write(doc_response.content)
                        
                        # Extract title from link text
                        title = link.get_text().strip()
                        if not title:
                            # Try to find title in span elements
                            title_span = link.find('span')
                            if title_span:
                                title = title_span.get_text().strip()
                        
                        if not title:
                            title = f"EUR-Lex Document {celex_id}"
                        
                        # Create metadata
                        metadata = {
                            "filename": filename,
                            "url": doc_url,
                            "celex_id": celex_id,
                            "title": title,
                            "document_type": search_config['name'].lower().replace(' ', '_'),
                            "source": "eur_lex",
                            "search_type": search_config['name'],
                            "download_date": datetime.now().isoformat(),
                            "file_size": file_path.stat().st_size,
                            "language": "en",
                            "page_url": page_url
                        }
                        
                        # Save metadata
                        metadata_file = target_dir / "metadata" / f"{file_path.stem}_metadata.json"
                        with open(metadata_file, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, indent=2, ensure_ascii=False)
                        
                        # Update statistics
                        results["documents_downloaded"] += 1
                        results["total_size"] += file_path.stat().st_size
                        self.stats['downloaded_celex_ids'].add(celex_id)
                        documents_downloaded += 1
                        
                        logging.info(f"Downloaded EUR-Lex document: {celex_id} ({file_path.stat().st_size / 1024:.1f} KB)")
                        
                        # Progress update
                        if documents_downloaded % 5 == 0:
                            logging.info(f"Progress: {documents_downloaded} documents downloaded from current page")
                    
                except Exception as e:
                    error_msg = f"Failed to download EUR-Lex document: {e}"
                    logging.error(error_msg)
                    results["errors"].append(error_msg)
                    continue
            
            return documents_downloaded
            
        except Exception as e:
            error_msg = f"Failed to scrape EUR-Lex page: {e}"
            logging.error(error_msg)
            results["errors"].append(error_msg)
            return 0

    def scrape_eur_lex_search_results(self, search_config: Dict, target_dir: Path) -> Dict:
        """
        Scrapes EUR-Lex search results for Belgian legal documents with systematic pagination.
        
        Args:
            search_config: Configuration for the EUR-Lex search
            target_dir: Directory to save documents
            
        Returns:
            Dictionary containing download statistics
        """
        logging.info(f"Scraping EUR-Lex search: {search_config['name']}")
        
        results = {
            "documents_downloaded": 0,
            "total_size": 0,
            "errors": [],
            "total_results": 0,
            "pages_processed": 0
        }
        
        try:
            max_pages = search_config.get('max_pages', 1000)
            consecutive_empty_pages = 0
            max_consecutive_empty = 3  # Stop after 3 consecutive empty pages
            
            # Process pages systematically
            for page_num in range(1, max_pages + 1):
                try:
                    # Build page URL
                    page_url = self.build_search_url(search_config, page_num)
                    
                    # Scrape this page
                    docs_from_page = self.scrape_eur_lex_page(page_url, target_dir, results, search_config)
                    results["pages_processed"] += 1
                    
                    logging.info(f"Page {page_num}: Downloaded {docs_from_page} documents")
                    
                    # Check if page is empty
                    if docs_from_page == 0:
                        consecutive_empty_pages += 1
                        logging.info(f"Empty page {page_num} (consecutive: {consecutive_empty_pages})")
                        
                        if consecutive_empty_pages >= max_consecutive_empty:
                            logging.info(f"Stopping after {max_consecutive_empty} consecutive empty pages")
                            break
                    else:
                        consecutive_empty_pages = 0  # Reset counter
                    
                    # Rate limiting between pages
                    page_delay = random.uniform(*self.rate_limits['page_delay'])
                    time.sleep(page_delay)
                    
                    # Progress update every 10 pages
                    if page_num % 10 == 0:
                        logging.info(f"Progress: {results['pages_processed']} pages processed, {results['documents_downloaded']} documents downloaded")
                    
                    # Safety check - stop if we've downloaded a reasonable amount
                    if results['documents_downloaded'] >= 1000:
                        logging.info(f"Reached 1000 documents, stopping for safety")
                        break
                    
                except Exception as e:
                    error_msg = f"Failed to process page {page_num}: {e}"
                    logging.error(error_msg)
                    results["errors"].append(error_msg)
                    consecutive_empty_pages += 1
                    
                    if consecutive_empty_pages >= max_consecutive_empty:
                        logging.info(f"Stopping after {max_consecutive_empty} consecutive errors")
                        break
                    
                    continue
            
            logging.info(f"Completed {search_config['name']}: {results['documents_downloaded']} documents from {results['pages_processed']} pages")
            return results
            
        except Exception as e:
            error_msg = f"Failed to scrape EUR-Lex search: {e}"
            logging.error(error_msg)
            results["errors"].append(error_msg)
            return results

    def download_eur_lex_belgian_databases(self) -> Dict:
        """
        Downloads EUR-Lex Belgian legal databases from all search types.
        
        Returns:
            Dictionary containing download statistics
        """
        logging.info("Starting robust EUR-Lex Belgian legal database download...")
        
        all_results = {}
        
        # Create database structure
        self.create_eur_lex_structure()
        
        # Download from each EUR-Lex search
        for search_name, search_config in self.eur_lex_searches.items():
            logging.info(f"Processing {search_config['name']}...")
            
            target_dir = self.base_dir / search_name
            
            # Scrape EUR-Lex search results
            results = self.scrape_eur_lex_search_results(search_config, target_dir)
            
            all_results[search_name] = results
            logging.info(f"Downloaded {results['documents_downloaded']} documents from {search_name}")
            
            # Rate limiting between searches
            search_delay = random.uniform(*self.rate_limits['search_delay'])
            time.sleep(search_delay)
        
        # Create comprehensive index
        self.create_eur_lex_comprehensive_index(all_results)
        
        # Generate final report
        self.generate_eur_lex_comprehensive_report(all_results)
        
        return all_results

    def create_eur_lex_comprehensive_index(self, all_results: Dict):
        """Creates a comprehensive index of all downloaded EUR-Lex documents."""
        logging.info("Creating comprehensive EUR-Lex document index...")
        
        index = {
            "created_date": datetime.now().isoformat(),
            "total_documents": 0,
            "total_size": 0,
            "total_results_available": 0,
            "total_pages_processed": 0,
            "sources": {},
            "document_types": {},
            "languages": {},
            "downloaded_celex_ids": list(self.stats['downloaded_celex_ids'])
        }
        
        # Process all results
        for search_name, results in all_results.items():
            search_total = results.get('documents_downloaded', 0)
            search_size = results.get('total_size', 0)
            search_available = results.get('total_results', 0)
            search_pages = results.get('pages_processed', 0)
            
            index["total_documents"] += search_total
            index["total_size"] += search_size
            index["total_results_available"] += search_available
            index["total_pages_processed"] += search_pages
            
            index["sources"][search_name] = {
                "documents": search_total,
                "size": search_size,
                "available": search_available,
                "pages_processed": search_pages
            }
        
        # Save index
        index_file = self.base_dir / "eur_lex_comprehensive_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
        
        logging.info(f"EUR-Lex comprehensive index created: {index['total_documents']} documents")

    def generate_eur_lex_comprehensive_report(self, all_results: Dict):
        """Generates a comprehensive EUR-Lex download report."""
        logging.info("Generating comprehensive EUR-Lex download report...")
        
        total_docs = sum(results.get('documents_downloaded', 0) for results in all_results.values())
        total_size = sum(results.get('total_size', 0) for results in all_results.values())
        total_available = sum(results.get('total_results', 0) for results in all_results.values())
        total_errors = sum(len(results.get('errors', [])) for results in all_results.values())
        total_pages = sum(results.get('pages_processed', 0) for results in all_results.values())
        
        duration = datetime.now() - self.stats['start_time']
        
        report = f"""
# EUR-Lex Belgian Legal Database Download Report - Robust Version

## Download Summary
- **Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Total Documents Downloaded**: {total_docs:,}
- **Total Documents Available**: {total_available:,}
- **Total Pages Processed**: {total_pages:,}
- **Total Size**: {total_size / (1024*1024):.2f} MB
- **Download Duration**: {duration}
- **Success Rate**: {(total_docs / (total_docs + total_errors) * 100) if (total_docs + total_errors) > 0 else 0.0:.1f}%
- **Unique CELEX IDs**: {len(self.stats['downloaded_celex_ids']):,}

## EUR-Lex Database Breakdown
"""
        
        for search_name, results in all_results.items():
            report += f"\n### {self.eur_lex_searches[search_name]['name']}\n"
            report += f"- **Documents Downloaded**: {results.get('documents_downloaded', 0):,}\n"
            report += f"- **Documents Available**: {results.get('total_results', 0):,}\n"
            report += f"- **Pages Processed**: {results.get('pages_processed', 0):,}\n"
            report += f"- **Total Size**: {results.get('total_size', 0) / (1024*1024):.2f} MB\n"
            report += f"- **Description**: {self.eur_lex_searches[search_name]['description']}\n"
            report += f"- **Expected Documents**: {self.eur_lex_searches[search_name]['expected_documents']:,}\n"
        
        report += f"""
## Download Statistics
- **Successfully Downloaded**: {total_docs:,}
- **Failed Downloads**: {total_errors:,}
- **Total Data Size**: {total_size / (1024*1024):.2f} MB
- **Total Available**: {total_available:,}
- **Coverage**: {(total_docs / total_available * 100) if total_available > 0 else 0:.1f}%

## Performance Metrics
- **Average Documents per Page**: {total_docs / total_pages if total_pages > 0 else 0:.1f}
- **Download Rate**: {total_docs / (duration.total_seconds() / 60) if duration.total_seconds() > 0 else 0:.1f} docs/minute
- **Data Rate**: {total_size / (1024*1024) / (duration.total_seconds() / 60) if duration.total_seconds() > 0 else 0:.1f} MB/minute

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
        report_file = self.base_dir / "eur_lex_comprehensive_download_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logging.info(f"EUR-Lex comprehensive report saved to {report_file}")
        print(report)

    def run_eur_lex_comprehensive_download(self):
        """Runs the complete EUR-Lex Belgian legal database download."""
        print("🏛️  Robust EUR-Lex Belgian Legal Database Scraper")
        print("=" * 60)
        print("This robust scraper will download EUR-Lex Belgian documents systematically.")
        print("Expected documents: 10,000+ Belgian legal documents")
        print("Features: Systematic pagination, retry logic, rate limiting, duplicate prevention")
        print("The process may take 3-6 hours depending on your internet connection.")
        print()
        
        # Confirm with user
        response = input("Do you want to proceed with downloading EUR-Lex Belgian documents? (y/N): ")
        if response.lower() != 'y':
            print("Download cancelled.")
            return
        
        try:
            # Start comprehensive download
            all_results = self.download_eur_lex_belgian_databases()
            
            print("\n🎉 Robust EUR-Lex Belgian legal database download completed!")
            print("=" * 60)
            print(f"Total documents downloaded: {sum(results.get('documents_downloaded', 0) for results in all_results.values()):,}")
            print(f"Total documents available: {sum(results.get('total_results', 0) for results in all_results.values()):,}")
            print(f"Total pages processed: {sum(results.get('pages_processed', 0) for results in all_results.values()):,}")
            print(f"Total size: {sum(results.get('total_size', 0) for results in all_results.values()) / (1024*1024):.2f} MB")
            print(f"Unique CELEX IDs: {len(self.stats['downloaded_celex_ids']):,}")
            print(f"Database location: {self.base_dir}")
            print("\nYou can now integrate these EUR-Lex databases with your legal assistant system.")
            
        except Exception as e:
            logging.error(f"EUR-Lex comprehensive download failed: {e}")
            print(f"\n❌ Download failed: {e}")


def main():
    """Main function to run EUR-Lex Belgian legal database download."""
    scraper = EURLexBelgianScraper()
    scraper.run_eur_lex_comprehensive_download()


if __name__ == "__main__":
    main() 