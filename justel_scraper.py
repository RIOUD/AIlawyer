#!/usr/bin/env python3
"""
Justel Database Scraper
Specialized scraper for extracting Belgian legal codes from Justel database
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import time
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JustelLegalCode:
    """Data structure for Justel legal code"""
    name: str
    category: str
    pdf_url: Optional[str] = None
    numac_code: Optional[str] = None
    last_updated: Optional[str] = None
    description: Optional[str] = None

class JustelScraper:
    """Scraper for Justel Belgian legal database"""
    
    def __init__(self):
        self.base_url = "https://www.ejustice.just.fgov.be/cgi_wet/codex.pl?language=nl&view_numac="
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Known NUMAC codes for major legal codes
        self.known_numac_codes = {
            'Burgerlijk Wetboek': '1804050150',
            'Strafwetboek': '1867060850',
            'Gerechtelijk Wetboek': '1967101050',
            'Wetboek van Koophandel': '1807071750',
            'Wetboek van Strafvordering': '1878061550',
            'Sociaal Strafwetboek': '2010060150',
            'Kieswetboek': '1989031550',
            'Consulair Wetboek': '1999122250',
            'Veldwetboek': '2007122750',
            'Wetboek diverse rechten en taksen': '1939091250',
            'Wetboek van de Belgische nationaliteit': '1984062850',
            'Wetboek van de minnelijke en gedwongen invordering van fiscale en niet-fiscale schuldvorderingen': '1992122250',
            'Wetboek van economisch recht': '2013032850',
            'Wetboek van internationaal privaatrecht': '2004071650',
            'Wetboek van strafrechtspleging voor het leger': '2003122250',
            'Vlaamse Codex Fiscaliteit': '2013035070',
            'Vlaamse Codex ruimtelijke ordening': '2014035070',
            'Vlaamse Wooncode': '2014035070',
            'Brussels Wetboek van Ruimtelijke Ordening': '2014035070',
            'Brussels Gemeentelijk Kieswetboek': '2014035070',
            'Brussels Wetboek van Lucht, Klimaat en Energiebeheersing': '2014035070',
            'Brusselse Huisvestingscode': '2014035070',
            'Waals Wetboek van Sociale Actie en Gezondheid': '2014035070',
            'Waalse Ambtenarencode': '2014035070',
            'Waalse Erfgoedwetboek': '2014035070',
            'Waalse Landbouwwetboek': '2014035070',
            'Waalse Milieuwetboek': '2014035070',
            'Waalse Wetboek van Duurzaam Wonen': '2014035070',
            'Waalse Wetboek van Ruimtelijke Ontwikkeling': '2014035070',
            'Wetboek van de plaatselijke democratie en decentralisatie': '2014035070',
            'Codex hoger onderwijs': '2014035070',
            'Vlaamse Codex Overheidsfinanciën': '2014035070',
            'Vlaamse codex secundair onderwijs': '2014035070',
            'Wetboek voor het basis- en secundair onderwijs': '2014035070',
            'Boswetboek': '1854121950',
            'Belgisch Scheepvaartwetboek': '2010032950',
            'Toerismewetboek': '2014035070'
        }
    
    def scrape_legal_codes(self) -> List[JustelLegalCode]:
        """Scrape all legal codes from Justel website"""
        logger.info("Starting Justel legal codes scraping...")
        
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            legal_codes = []
            
            # Find all sections
            sections = soup.find_all(['h2', 'h3'])
            
            for section in sections:
                section_text = section.get_text(strip=True)
                category = self._determine_category(section_text)
                
                if not category:
                    continue
                
                logger.info(f"Processing section: {section_text} (Category: {category})")
                
                # Find legal codes in this section
                codes = self._extract_codes_from_section(section, category)
                legal_codes.extend(codes)
            
            logger.info(f"Total legal codes found: {len(legal_codes)}")
            return legal_codes
            
        except Exception as e:
            logger.error(f"Error scraping Justel: {e}")
            return []
    
    def _determine_category(self, section_text: str) -> Optional[str]:
        """Determine category from section text"""
        text_lower = section_text.lower()
        
        if any(word in text_lower for word in ['federale', 'federal']):
            return "Federal"
        elif any(word in text_lower for word in ['regionale', 'regional']):
            return "Regional"
        elif any(word in text_lower for word in ['gemeenschap', 'community']):
            return "Community"
        
        return None
    
    def _extract_codes_from_section(self, section, category: str) -> List[JustelLegalCode]:
        """Extract legal codes from a section"""
        codes = []
        
        # Find the next element after the section header
        current = section.find_next_sibling()
        
        while current and current.name not in ['h2', 'h3']:
            if current.name == 'ul':
                for li in current.find_all('li'):
                    code = self._extract_code_from_list_item(li, category)
                    if code:
                        codes.append(code)
            current = current.find_next_sibling()
        
        return codes
    
    def _extract_code_from_list_item(self, li_element, category: str) -> Optional[JustelLegalCode]:
        """Extract legal code information from a list item"""
        try:
            # Get the main text
            text = li_element.get_text(strip=True)
            
            # Clean the name
            name = self._clean_code_name(text)
            
            # Extract PDF URL
            pdf_url = self._extract_pdf_url(li_element)
            
            # Extract last updated info
            last_updated = self._extract_last_updated(text)
            
            # Get NUMAC code
            numac_code = self.known_numac_codes.get(name)
            
            # Create description
            description = self._create_description(name, category)
            
            return JustelLegalCode(
                name=name,
                category=category,
                pdf_url=pdf_url,
                numac_code=numac_code,
                last_updated=last_updated,
                description=description
            )
            
        except Exception as e:
            logger.error(f"Error extracting code from list item: {e}")
            return None
    
    def _clean_code_name(self, text: str) -> str:
        """Clean the legal code name"""
        # Remove PDF indicator
        name = re.sub(r'\s*pdf\s*$', '', text, flags=re.IGNORECASE)
        
        # Remove parentheses content (like "minder dan 1 maand geleden bijgewerkt")
        name = re.sub(r'\s*\([^)]*\)\s*$', '', name)
        
        # Clean up whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _extract_pdf_url(self, li_element) -> Optional[str]:
        """Extract PDF URL from list item"""
        link = li_element.find('a', href=True)
        if link:
            href = link['href']
            if href.endswith('.pdf') or 'pdf' in href.lower():
                return urljoin(self.base_url, href)
        return None
    
    def _extract_last_updated(self, text: str) -> Optional[str]:
        """Extract last updated information"""
        # Look for patterns like "minder dan 1 maand geleden bijgewerkt"
        patterns = [
            r'minder dan (\d+) (maand|maanden) geleden bijgewerkt',
            r'(\d+) (maand|maanden) geleden bijgewerkt',
            r'(\d+) (dag|dagen) geleden bijgewerkt',
            r'(\d+) (week|weken) geleden bijgewerkt'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _create_description(self, name: str, category: str) -> str:
        """Create a description for the legal code"""
        descriptions = {
            'Burgerlijk Wetboek': 'The Belgian Civil Code containing fundamental civil law principles',
            'Strafwetboek': 'The Belgian Criminal Code defining criminal offenses and penalties',
            'Gerechtelijk Wetboek': 'The Belgian Judicial Code governing court procedures and organization',
            'Wetboek van Koophandel': 'The Belgian Commercial Code regulating business and commercial activities',
            'Wetboek van Strafvordering': 'The Belgian Code of Criminal Procedure governing criminal proceedings',
            'Sociaal Strafwetboek': 'The Belgian Social Criminal Code for social security violations',
            'Vlaamse Codex Fiscaliteit': 'The Flemish Tax Code regulating tax matters in Flanders',
            'Vlaamse Codex ruimtelijke ordening': 'The Flemish Spatial Planning Code for urban development',
            'Waals Wetboek van Sociale Actie en Gezondheid': 'The Walloon Code of Social Action and Health',
            'Brussels Wetboek van Ruimtelijke Ordening': 'The Brussels Spatial Planning Code for urban development'
        }
        
        return descriptions.get(name, f"Belgian legal code in the {category} category")
    
    def get_detailed_code_info(self, numac_code: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific legal code"""
        if not numac_code:
            return None
        
        try:
            url = f"{self.base_url}{numac_code}"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract detailed information
            info = {
                'numac_code': numac_code,
                'url': url,
                'title': '',
                'articles': [],
                'last_updated': '',
                'pdf_links': []
            }
            
            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                info['title'] = title_elem.get_text(strip=True)
            
            # Extract PDF links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.pdf') or 'pdf' in href.lower():
                    info['pdf_links'].append(urljoin(url, href))
            
            # Extract articles (basic structure)
            articles = soup.find_all(['h2', 'h3', 'h4'])
            for article in articles:
                article_text = article.get_text(strip=True)
                if re.match(r'^Artikel\s+\d+', article_text, re.IGNORECASE):
                    info['articles'].append(article_text)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting detailed info for {numac_code}: {e}")
            return None
    
    def save_to_json(self, legal_codes: List[JustelLegalCode], filename: str = "justel_legal_codes.json"):
        """Save legal codes to JSON file"""
        data = {
            'scrape_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_codes': len(legal_codes),
            'categories': {},
            'legal_codes': []
        }
        
        # Count by category and prepare data
        for code in legal_codes:
            category = code.category
            if category not in data['categories']:
                data['categories'][category] = 0
            data['categories'][category] += 1
            
            data['legal_codes'].append({
                'name': code.name,
                'category': code.category,
                'pdf_url': code.pdf_url,
                'numac_code': code.numac_code,
                'last_updated': code.last_updated,
                'description': code.description
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(legal_codes)} legal codes to {filename}")
        return filename

def main():
    """Main function to run the Justel scraper"""
    print("🔍 Justel Legal Database Scraper")
    print("=" * 40)
    
    scraper = JustelScraper()
    
    try:
        # Scrape legal codes
        legal_codes = scraper.scrape_legal_codes()
        
        if legal_codes:
            # Save to JSON
            filename = scraper.save_to_json(legal_codes)
            
            print(f"\n✅ Successfully scraped {len(legal_codes)} legal codes")
            print(f"📁 Results saved to: {filename}")
            
            # Show summary by category
            categories = {}
            for code in legal_codes:
                if code.category not in categories:
                    categories[code.category] = 0
                categories[code.category] += 1
            
            print("\n📊 Summary by category:")
            for category, count in categories.items():
                print(f"  {category}: {count} codes")
            
            # Show some examples
            print("\n📋 Sample legal codes:")
            for i, code in enumerate(legal_codes[:5]):
                print(f"  {i+1}. {code.name} ({code.category})")
                if code.pdf_url:
                    print(f"     PDF: {code.pdf_url}")
            
        else:
            print("❌ No legal codes found")
            
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        logger.error(f"Scraping failed: {e}")

if __name__ == "__main__":
    main() 