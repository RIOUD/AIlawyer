#!/usr/bin/env python3
"""
Update Recent Legal Changes
Scrapes recent legal consolidations and amendments from Justel and updates the offline database
"""

import requests
import json
import sqlite3
import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RecentLegalChangesUpdater:
    """Update offline legal database with recent changes from Justel"""
    
    def __init__(self, offline_data_dir: str = "offline_legal_knowledge"):
        self.offline_data_dir = Path(offline_data_dir)
        self.database_path = self.offline_data_dir / "database" / "legal_codes.db"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Justel URLs
        self.base_url = "https://www.ejustice.just.fgov.be"
        self.recent_consolidations_url = "https://www.ejustice.just.fgov.be/cgi_wet/summary.pl?language=nl&type=cons&sort=date_upd&view_numac="
        self.recent_legislation_url = "https://www.ejustice.just.fgov.be/cgi_wet/summary.pl?language=nl&type=leg&sort=date_upd&view_numac="
        self.recent_abrogations_url = "https://www.ejustice.just.fgov.be/cgi_wet/summary.pl?language=nl&type=abrog&sort=date_upd&view_numac="
        
    def scrape_recent_changes(self) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape recent legal changes from all Justel summary pages"""
        logger.info("Scraping recent legal changes from Justel...")
        
        changes = {
            'consolidations': [],
            'legislation': [],
            'abrogations': []
        }
        
        # Scrape recent consolidations
        logger.info("Scraping recent consolidations...")
        changes['consolidations'] = self._scrape_summary_page(self.recent_consolidations_url, 'consolidation')
        
        # Scrape recent legislation
        logger.info("Scraping recent legislation...")
        changes['legislation'] = self._scrape_summary_page(self.recent_legislation_url, 'legislation')
        
        # Scrape recent abrogations
        logger.info("Scraping recent abrogations...")
        changes['abrogations'] = self._scrape_summary_page(self.recent_abrogations_url, 'abrogation')
        
        logger.info(f"Found {len(changes['consolidations'])} consolidations, {len(changes['legislation'])} legislation, {len(changes['abrogations'])} abrogations")
        return changes
    
    def _scrape_summary_page(self, url: str, change_type: str) -> List[Dict[str, Any]]:
        """Scrape a specific summary page for recent changes"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            changes = []
            
            # Find all list items (the actual legal entries)
            list_items = soup.find_all('div', class_='list-item')
            
            for item in list_items:
                try:
                    # Extract title and link
                    title_element = item.find('a', class_='list-item--title')
                    if not title_element:
                        continue
                        
                    title = title_element.get_text(strip=True)
                    link = title_element.get('href')
                    
                    # Extract numac from button
                    button_element = item.find('a', class_='button')
                    numac = button_element.get_text(strip=True) if button_element else ""
                    
                    # Extract date from the title (it's usually at the beginning)
                    date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', title)
                    date_text = date_match.group(1) if date_match else ""
                    
                    if title and link:
                        # Fix URL construction - convert article.pl to codex.pl format
                        if 'article.pl' in link:
                            # Extract the numac from the URL
                            numac_match = re.search(r'cn_search=(\d+)', link)
                            if numac_match:
                                numac_id = numac_match.group(1)
                                full_url = f"{self.base_url}/cgi_wet/codex.pl?language=nl&view_numac={numac_id}"
                            else:
                                full_url = link
                        elif link.startswith('/'):
                            full_url = self.base_url + link
                        elif link.startswith('http'):
                            full_url = link
                        else:
                            full_url = self.base_url + '/' + link
                            
                        change = {
                            'date': date_text,
                            'title': title,
                            'numac': numac,
                            'url': full_url,
                            'type': change_type,
                            'scraped_at': datetime.now().isoformat()
                        }
                        changes.append(change)
                        
                except Exception as e:
                    logger.warning(f"Error parsing list item: {e}")
                    continue
            
            return changes
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return []
    
    def download_updated_content(self, changes: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Download updated content for recent changes"""
        logger.info("Downloading updated content for recent changes...")
        
        downloaded_content = []
        
        # Process consolidations and legislation (these contain actual content)
        for change_type in ['consolidations', 'legislation']:
            for change in changes[change_type]:
                try:
                    logger.info(f"Downloading: {change['title']}")
                    
                    # Download the content
                    content = self._download_legal_content(change['url'])
                    if content:
                        change['content'] = content
                        change['content_downloaded'] = True
                        downloaded_content.append(change)
                        
                        # Rate limiting
                        time.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Error downloading {change['title']}: {e}")
                    change['content_downloaded'] = False
                    continue
        
        logger.info(f"Successfully downloaded {len(downloaded_content)} updated legal contents")
        return downloaded_content
    
    def _download_legal_content(self, url: str) -> Optional[str]:
        """Download legal content from a specific URL"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract the main content
            content_div = soup.find('div', {'class': 'content'}) or soup.find('div', {'id': 'content'})
            if content_div:
                # Clean up the content
                content = content_div.get_text(separator='\n', strip=True)
                return content
            
            # Fallback: get all text
            return soup.get_text(separator='\n', strip=True)
            
        except Exception as e:
            logger.error(f"Error downloading content from {url}: {e}")
            return None
    
    def update_database(self, downloaded_content: List[Dict[str, Any]]):
        """Update the SQLite database with recent changes"""
        logger.info("Updating database with recent changes...")
        
        if not self.database_path.exists():
            logger.error("Database not found. Please run the initial setup first.")
            return
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Create table for recent changes if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recent_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    title TEXT,
                    numac TEXT,
                    url TEXT,
                    type TEXT,
                    content TEXT,
                    scraped_at TEXT,
                    processed_at TEXT
                )
            ''')
            
            # Insert recent changes
            for change in downloaded_content:
                cursor.execute('''
                    INSERT OR REPLACE INTO recent_changes 
                    (date, title, numac, url, type, content, scraped_at, processed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    change['date'],
                    change['title'],
                    change['numac'],
                    change['url'],
                    change['type'],
                    change.get('content', ''),
                    change['scraped_at'],
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            logger.info(f"Updated database with {len(downloaded_content)} recent changes")
            
        except Exception as e:
            logger.error(f"Error updating database: {e}")
        finally:
            conn.close()
    
    def update_search_index(self, downloaded_content: List[Dict[str, Any]]):
        """Update the search index with recent changes"""
        logger.info("Updating search index with recent changes...")
        
        search_index_path = self.offline_data_dir / "metadata" / "search_index.json"
        
        if not search_index_path.exists():
            logger.warning("Search index not found. Creating new one...")
            search_index = {
                'recent_changes': [],
                'last_updated': datetime.now().isoformat()
            }
        else:
            try:
                with open(search_index_path, 'r', encoding='utf-8') as f:
                    search_index = json.load(f)
            except Exception as e:
                logger.error(f"Error loading search index: {e}")
                search_index = {
                    'recent_changes': [],
                    'last_updated': datetime.now().isoformat()
                }
        
        # Add recent changes to search index
        for change in downloaded_content:
            if change.get('content'):
                search_entry = {
                    'title': change['title'],
                    'type': change['type'],
                    'date': change['date'],
                    'numac': change['numac'],
                    'url': change['url'],
                    'content_preview': change['content'][:500] + '...' if len(change['content']) > 500 else change['content'],
                    'keywords': self._extract_keywords(change['content']),
                    'added_at': datetime.now().isoformat()
                }
                search_index['recent_changes'].append(search_entry)
        
        search_index['last_updated'] = datetime.now().isoformat()
        
        # Save updated search index
        try:
            with open(search_index_path, 'w', encoding='utf-8') as f:
                json.dump(search_index, f, indent=2, ensure_ascii=False)
            logger.info("Search index updated successfully")
        except Exception as e:
            logger.error(f"Error saving search index: {e}")
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from legal content"""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b\w{4,}\b', content.lower())
        word_freq = {}
        
        for word in words:
            if word not in ['this', 'that', 'with', 'have', 'will', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'when', 'come', 'just', 'into', 'than', 'more', 'other', 'about', 'many', 'then', 'them', 'these', 'people', 'only', 'well', 'over', 'think', 'also', 'back', 'after', 'work', 'first', 'should', 'because', 'through', 'never', 'become', 'really', 'another', 'family', 'around', 'often', 'however', 'always', 'those', 'both', 'each', 'might', 'being', 'under', 'while', 'during', 'before', 'against', 'between', 'without', 'something', 'everything', 'anything', 'nothing', 'someone', 'everyone', 'anyone', 'noone', 'somewhere', 'everywhere', 'anywhere', 'nowhere']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top 10 keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def generate_update_report(self, changes: Dict[str, List[Dict[str, Any]]], downloaded_content: List[Dict[str, Any]]):
        """Generate a report of the update process"""
        report = {
            'update_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_consolidations': len(changes['consolidations']),
                'total_legislation': len(changes['legislation']),
                'total_abrogations': len(changes['abrogations']),
                'successfully_downloaded': len(downloaded_content),
                'failed_downloads': sum(len(changes[t]) for t in ['consolidations', 'legislation']) - len(downloaded_content)
            },
            'recent_changes': {
                'consolidations': changes['consolidations'],
                'legislation': changes['legislation'],
                'abrogations': changes['abrogations']
            },
            'downloaded_content': [
                {
                    'title': item['title'],
                    'type': item['type'],
                    'date': item['date'],
                    'numac': item['numac'],
                    'content_length': len(item.get('content', ''))
                }
                for item in downloaded_content
            ]
        }
        
        # Save report
        report_path = self.offline_data_dir / "metadata" / "recent_changes_report.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Update report saved to {report_path}")
        except Exception as e:
            logger.error(f"Error saving update report: {e}")
        
        return report
    
    def run_update(self):
        """Run the complete update process"""
        logger.info("Starting recent legal changes update process...")
        
        # Check if offline database exists
        if not self.offline_data_dir.exists():
            logger.error("Offline legal knowledge base not found. Please run setup_offline_legal_knowledge.py first.")
            return
        
        try:
            # Step 1: Scrape recent changes
            changes = self.scrape_recent_changes()
            
            if not any(changes.values()):
                logger.warning("No recent changes found. Database is already up to date.")
                return
            
            # Step 2: Download updated content
            downloaded_content = self.download_updated_content(changes)
            
            if not downloaded_content:
                logger.warning("No content could be downloaded. Check network connection.")
                return
            
            # Step 3: Update database
            self.update_database(downloaded_content)
            
            # Step 4: Update search index
            self.update_search_index(downloaded_content)
            
            # Step 5: Generate report
            report = self.generate_update_report(changes, downloaded_content)
            
            logger.info("Recent legal changes update completed successfully!")
            logger.info(f"Summary: {report['summary']}")
            
        except Exception as e:
            logger.error(f"Error during update process: {e}")

def main():
    """Main function"""
    updater = RecentLegalChangesUpdater()
    updater.run_update()

if __name__ == "__main__":
    main() 