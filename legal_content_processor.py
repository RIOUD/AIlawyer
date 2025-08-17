#!/usr/bin/env python3
"""
Legal Content Processor
Processes downloaded legal content and integrates it with the vector database for offline search
"""

import os
import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
from datetime import datetime
import re

# Import existing components
try:
    from legal_content_database import LegalContentDatabase
    from semantic_analyzer import SemanticAnalyzer
    from config import VECTOR_STORE_PATH, EMBEDDING_MODEL_NAME
except ImportError:
    print("Warning: Some components not available, using fallback configuration")
    VECTOR_STORE_PATH = "./chroma_db"
    EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LegalContentProcessor:
    """Processes legal content and integrates it with the vector database"""
    
    def __init__(self, offline_data_dir: str = "offline_legal_knowledge"):
        self.offline_data_dir = Path(offline_data_dir)
        self.database_path = self.offline_data_dir / "legal_knowledge.db"
        self.content_dir = self.offline_data_dir / "content"
        self.pdfs_dir = self.offline_data_dir / "pdfs"
        self.metadata_dir = self.offline_data_dir / "metadata"
        
        # Initialize components
        self._init_components()
    
    def _init_components(self):
        """Initialize processing components"""
        try:
            # Initialize legal content database
            self.legal_db = LegalContentDatabase()
            
            # Initialize semantic analyzer
            self.semantic_analyzer = SemanticAnalyzer()
            
            logger.info("Components initialized successfully")
            
        except Exception as e:
            logger.warning(f"Some components not available: {e}")
            self.legal_db = None
            self.semantic_analyzer = None
    
    def load_offline_legal_codes(self) -> List[Dict[str, Any]]:
        """Load legal codes from the offline database"""
        if not self.database_path.exists():
            logger.error(f"Database not found: {self.database_path}")
            return []
        
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, english, french, german, url, category, pdf_url, content, 
                       last_updated, file_path, hash, created_at
                FROM legal_codes
                ORDER BY category, name
            ''')
            
            rows = cursor.fetchall()
            legal_codes = []
            
            for row in rows:
                legal_code = {
                    'name': row[0],
                    'english': row[1],
                    'french': row[2],
                    'german': row[3],
                    'url': row[4],
                    'category': row[5],
                    'pdf_url': row[6],
                    'content': row[7],
                    'last_updated': row[8],
                    'file_path': row[9],
                    'hash': row[10],
                    'created_at': row[11]
                }
                legal_codes.append(legal_code)
            
            conn.close()
            logger.info(f"Loaded {len(legal_codes)} legal codes from database")
            return legal_codes
            
        except Exception as e:
            logger.error(f"Error loading legal codes: {e}")
            return []
    
    def process_legal_content(self, legal_codes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process legal content for better search and analysis"""
        processed_codes = []
        
        for code in legal_codes:
            try:
                processed_code = self._process_single_code(code)
                if processed_code:
                    processed_codes.append(processed_code)
                    
            except Exception as e:
                logger.error(f"Error processing {code.get('name', 'Unknown')}: {e}")
        
        logger.info(f"Processed {len(processed_codes)} legal codes")
        return processed_codes
    
    def _process_single_code(self, code: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single legal code"""
        if not code.get('content'):
            return None
        
        content = code['content']
        
        # Extract structured information
        processed_code = {
            **code,
            'processed_content': content,
            'articles': self._extract_articles(content),
            'sections': self._extract_sections(content),
            'keywords': self._extract_keywords(content),
            'summary': self._generate_summary(content),
            'legal_topics': self._identify_legal_topics(content),
            'processed_at': datetime.now().isoformat()
        }
        
        return processed_code
    
    def _extract_articles(self, content: str) -> List[Dict[str, Any]]:
        """Extract articles from legal content"""
        articles = []
        
        # Look for article patterns
        article_patterns = [
            r'Artikel\s+(\d+[a-z]?)[\s\n]*([^\n]+)',
            r'Article\s+(\d+[a-z]?)[\s\n]*([^\n]+)',
            r'Art\.\s*(\d+[a-z]?)[\s\n]*([^\n]+)'
        ]
        
        for pattern in article_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                article_num = match.group(1)
                article_text = match.group(2).strip()
                
                articles.append({
                    'number': article_num,
                    'title': article_text,
                    'content': self._extract_article_content(content, match.start())
                })
        
        return articles
    
    def _extract_article_content(self, content: str, start_pos: int) -> str:
        """Extract content for a specific article"""
        # Find the end of the article (next article or section)
        end_patterns = [
            r'\nArtikel\s+\d+',
            r'\nArticle\s+\d+',
            r'\nArt\.\s*\d+',
            r'\n[A-Z][A-Z\s]+\n'
        ]
        
        end_pos = len(content)
        for pattern in end_patterns:
            match = re.search(pattern, content[start_pos + 100:], re.IGNORECASE)
            if match:
                end_pos = min(end_pos, start_pos + 100 + match.start())
        
        return content[start_pos:end_pos].strip()
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract sections from legal content"""
        sections = []
        
        # Look for section patterns
        section_patterns = [
            r'(TITEL|TITLE|HOOFDSTUK|CHAPTER)\s+([IVX]+)[\s\n]*([^\n]+)',
            r'(AFDELING|SECTION)\s+([IVX]+)[\s\n]*([^\n]+)',
            r'(BOEK|BOOK)\s+([IVX]+)[\s\n]*([^\n]+)'
        ]
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                section_type = match.group(1)
                section_num = match.group(2)
                section_title = match.group(3).strip()
                
                sections.append({
                    'type': section_type,
                    'number': section_num,
                    'title': section_title
                })
        
        return sections
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from legal content"""
        # Common legal keywords in multiple languages
        legal_keywords = [
            'recht', 'wet', 'code', 'artikel', 'bepaling', 'regeling',
            'law', 'code', 'article', 'provision', 'regulation',
            'loi', 'code', 'article', 'disposition', 'règlement',
            'gesetz', 'kodex', 'artikel', 'bestimmung', 'verordnung'
        ]
        
        # Extract words that match legal patterns
        words = re.findall(r'\b[A-Za-zÀ-ÿ]{4,}\b', content.lower())
        
        # Filter for legal keywords and frequent terms
        word_freq = {}
        for word in words:
            if word in legal_keywords or len(word) > 6:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:20]]
    
    def _generate_summary(self, content: str) -> str:
        """Generate a summary of the legal content"""
        # Take first few paragraphs as summary
        paragraphs = content.split('\n\n')
        summary_paragraphs = paragraphs[:3]
        
        summary = '\n\n'.join(summary_paragraphs)
        
        # Truncate if too long
        if len(summary) > 500:
            summary = summary[:500] + "..."
        
        return summary
    
    def _identify_legal_topics(self, content: str) -> List[str]:
        """Identify legal topics in the content"""
        topics = []
        
        # Topic patterns
        topic_patterns = {
            'Civil Law': [r'burgerlijk', r'civil', r'civil', r'personenrecht', r'family law'],
            'Criminal Law': [r'straf', r'criminal', r'pénal', r'strafrecht'],
            'Commercial Law': [r'koophandel', r'commercial', r'commercial', r'handelsrecht'],
            'Administrative Law': [r'bestuursrecht', r'administrative', r'administratif'],
            'Constitutional Law': [r'grondwet', r'constitutional', r'constitutionnel'],
            'Labor Law': [r'arbeidsrecht', r'labor', r'travail', r'employment'],
            'Tax Law': [r'fiscaal', r'tax', r'fiscal', r'steuer'],
            'Environmental Law': [r'milieu', r'environmental', r'environnement'],
            'Property Law': [r'goederenrecht', r'property', r'propriété'],
            'Contract Law': [r'overeenkomst', r'contract', r'contrat']
        }
        
        content_lower = content.lower()
        for topic, patterns in topic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    topics.append(topic)
                    break
        
        return list(set(topics))
    
    def integrate_with_vector_database(self, processed_codes: List[Dict[str, Any]]):
        """Integrate processed legal codes with the vector database"""
        if not self.legal_db:
            logger.warning("Legal database not available, skipping vector integration")
            return
        
        try:
            logger.info("Integrating legal codes with vector database...")
            
            for code in processed_codes:
                if code.get('processed_content'):
                    # Add to vector database
                    self.legal_db.add_legal_content(
                        title=code['name'],
                        content=code['processed_content'],
                        category=code['category'],
                        metadata={
                            'url': code.get('url'),
                            'pdf_url': code.get('pdf_url'),
                            'last_updated': code.get('last_updated'),
                            'topics': code.get('legal_topics', []),
                            'keywords': code.get('keywords', []),
                            'articles_count': len(code.get('articles', [])),
                            'sections_count': len(code.get('sections', []))
                        }
                    )
            
            logger.info(f"Integrated {len(processed_codes)} legal codes with vector database")
            
        except Exception as e:
            logger.error(f"Error integrating with vector database: {e}")
    
    def create_search_index(self, processed_codes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a search index for offline legal research"""
        search_index = {
            'created_at': datetime.now().isoformat(),
            'total_codes': len(processed_codes),
            'categories': {},
            'topics': {},
            'keywords': {},
            'articles': {},
            'search_data': []
        }
        
        for code in processed_codes:
            # Index by category
            category = code['category']
            if category not in search_index['categories']:
                search_index['categories'][category] = []
            search_index['categories'][category].append(code['name'])
            
            # Index by topics
            for topic in code.get('legal_topics', []):
                if topic not in search_index['topics']:
                    search_index['topics'][topic] = []
                search_index['topics'][topic].append(code['name'])
            
            # Index by keywords
            for keyword in code.get('keywords', []):
                if keyword not in search_index['keywords']:
                    search_index['keywords'][keyword] = []
                search_index['keywords'][keyword].append(code['name'])
            
            # Index articles
            for article in code.get('articles', []):
                article_key = f"{code['name']} - Article {article['number']}"
                search_index['articles'][article_key] = {
                    'code': code['name'],
                    'article_number': article['number'],
                    'title': article['title'],
                    'content': article['content'][:200] + "..." if len(article['content']) > 200 else article['content']
                }
            
            # Add to search data
            search_data = {
                'name': code['name'],
                'category': code['category'],
                'summary': code.get('summary', ''),
                'topics': code.get('legal_topics', []),
                'keywords': code.get('keywords', []),
                'articles_count': len(code.get('articles', [])),
                'url': code.get('url'),
                'pdf_url': code.get('pdf_url')
            }
            search_index['search_data'].append(search_data)
        
        return search_index
    
    def save_processed_data(self, processed_codes: List[Dict[str, Any]], search_index: Dict[str, Any]):
        """Save processed data to files"""
        try:
            # Save processed codes
            processed_file = self.metadata_dir / 'processed_legal_codes.json'
            with open(processed_file, 'w', encoding='utf-8') as f:
                json.dump(processed_codes, f, indent=2, ensure_ascii=False)
            
            # Save search index
            index_file = self.metadata_dir / 'search_index.json'
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(search_index, f, indent=2, ensure_ascii=False)
            
            # Save summary
            summary = {
                'processed_at': datetime.now().isoformat(),
                'total_codes': len(processed_codes),
                'categories': search_index['categories'],
                'topics': list(search_index['topics'].keys()),
                'total_articles': len(search_index['articles']),
                'total_keywords': len(search_index['keywords'])
            }
            
            summary_file = self.metadata_dir / 'processing_summary.json'
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved processed data to {self.metadata_dir}")
            
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
    
    def process_all_offline_content(self):
        """Process all offline legal content"""
        logger.info("Starting comprehensive offline legal content processing...")
        
        # Step 1: Load legal codes from database
        legal_codes = self.load_offline_legal_codes()
        
        if not legal_codes:
            logger.error("No legal codes found in database")
            return
        
        # Step 2: Process legal content
        processed_codes = self.process_legal_content(legal_codes)
        
        if not processed_codes:
            logger.error("No legal codes could be processed")
            return
        
        # Step 3: Create search index
        search_index = self.create_search_index(processed_codes)
        
        # Step 4: Integrate with vector database
        self.integrate_with_vector_database(processed_codes)
        
        # Step 5: Save processed data
        self.save_processed_data(processed_codes, search_index)
        
        # Step 6: Generate final report
        self._generate_processing_report(processed_codes, search_index)
        
        logger.info("Offline legal content processing completed!")
    
    def _generate_processing_report(self, processed_codes: List[Dict[str, Any]], search_index: Dict[str, Any]):
        """Generate a processing report"""
        report = {
            'processing_date': datetime.now().isoformat(),
            'total_codes_processed': len(processed_codes),
            'categories_processed': len(search_index['categories']),
            'topics_identified': len(search_index['topics']),
            'articles_extracted': len(search_index['articles']),
            'keywords_extracted': len(search_index['keywords']),
            'category_breakdown': search_index['categories'],
            'topic_breakdown': {topic: len(codes) for topic, codes in search_index['topics'].items()},
            'processing_stats': {
                'avg_articles_per_code': sum(len(code.get('articles', [])) for code in processed_codes) / len(processed_codes),
                'avg_sections_per_code': sum(len(code.get('sections', [])) for code in processed_codes) / len(processed_codes),
                'avg_keywords_per_code': sum(len(code.get('keywords', [])) for code in processed_codes) / len(processed_codes)
            }
        }
        
        report_file = self.metadata_dir / 'processing_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info("Processing report generated:")
        logger.info(f"  Total codes processed: {report['total_codes_processed']}")
        logger.info(f"  Categories: {report['categories_processed']}")
        logger.info(f"  Topics identified: {report['topics_identified']}")
        logger.info(f"  Articles extracted: {report['articles_extracted']}")
        logger.info(f"  Keywords extracted: {report['keywords_extracted']}")

def main():
    """Main function to run the content processor"""
    print("🔧 Legal Content Processor")
    print("=" * 30)
    
    processor = LegalContentProcessor()
    
    try:
        processor.process_all_offline_content()
        print("\n✅ Legal content processing completed successfully!")
        print(f"📁 Processed data stored in: {processor.offline_data_dir}")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        logger.error(f"Processing failed: {e}")

if __name__ == "__main__":
    main() 