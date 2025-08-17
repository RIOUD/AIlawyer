#!/usr/bin/env python3
"""
Analyze Download Size Requirements
Calculate the exact size needed to download the complete Belgian legal knowledge base
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DownloadSizeAnalyzer:
    """Analyze download size requirements for offline legal knowledge base"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def load_legal_codes(self) -> List[Dict[str, Any]]:
        """Load legal codes from the scraped data"""
        try:
            with open('justel_legal_codes.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('legal_codes', [])
        except FileNotFoundError:
            logger.error("justel_legal_codes.json not found. Run justel_scraper.py first.")
            return []
    
    def analyze_pdf_sizes(self, legal_codes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze PDF file sizes for all legal codes"""
        logger.info("Analyzing PDF file sizes...")
        
        total_size = 0
        successful_checks = 0
        failed_checks = 0
        size_breakdown = {
            'federal': {'count': 0, 'size': 0},
            'regional': {'count': 0, 'size': 0},
            'community': {'count': 0, 'size': 0}
        }
        
        for i, code in enumerate(legal_codes, 1):
            pdf_url = code.get('pdf_url')
            category = code.get('category', '').lower()
            name = code.get('name', 'Unknown')
            
            if not pdf_url:
                logger.warning(f"No PDF URL for {name}")
                failed_checks += 1
                continue
            
            try:
                logger.info(f"Checking {i}/{len(legal_codes)}: {name}")
                
                # Send HEAD request to get file size
                response = self.session.head(pdf_url, timeout=10)
                response.raise_for_status()
                
                # Get content length
                content_length = response.headers.get('content-length')
                if content_length:
                    file_size = int(content_length)
                    total_size += file_size
                    successful_checks += 1
                    
                    # Update category breakdown
                    if category in size_breakdown:
                        size_breakdown[category]['count'] += 1
                        size_breakdown[category]['size'] += file_size
                    
                    logger.info(f"  ✓ {name}: {self.format_size(file_size)}")
                else:
                    logger.warning(f"  ⚠ {name}: Could not determine size")
                    failed_checks += 1
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"  ✗ {name}: Error checking size - {e}")
                failed_checks += 1
        
        return {
            'total_size': total_size,
            'successful_checks': successful_checks,
            'failed_checks': failed_checks,
            'size_breakdown': size_breakdown,
            'total_codes': len(legal_codes)
        }
    
    def estimate_processing_overhead(self, pdf_size: int) -> Dict[str, int]:
        """Estimate additional storage needed for processing"""
        # Text extraction typically reduces size by 80-90%
        extracted_text_size = int(pdf_size * 0.1)  # 10% of original size
        
        # Search indexes and metadata
        index_size = int(extracted_text_size * 0.2)  # 20% of text size
        
        # Database storage
        database_size = int(extracted_text_size * 0.1)  # 10% of text size
        
        # Metadata files
        metadata_size = int(extracted_text_size * 0.05)  # 5% of text size
        
        total_overhead = extracted_text_size + index_size + database_size + metadata_size
        
        return {
            'extracted_text': extracted_text_size,
            'search_indexes': index_size,
            'database': database_size,
            'metadata': metadata_size,
            'total_overhead': total_overhead
        }
    
    def format_size(self, bytes_size: int) -> str:
        """Format bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    def generate_download_report(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive download report"""
        pdf_size = analysis['total_size']
        overhead = self.estimate_processing_overhead(pdf_size)
        
        total_storage_needed = pdf_size + overhead['total_overhead']
        
        # Estimate download time (assuming 10 Mbps connection)
        download_speed_mbps = 10
        download_speed_bytes = download_speed_mbps * 1024 * 1024 / 8
        estimated_download_time = pdf_size / download_speed_bytes
        
        # Estimate processing time (assuming 1 second per PDF)
        processing_time = analysis['successful_checks'] * 1  # seconds per PDF
        
        report = {
            'summary': {
                'total_legal_codes': analysis['total_codes'],
                'pdf_files_to_download': analysis['successful_checks'],
                'failed_checks': analysis['failed_checks'],
                'success_rate': f"{(analysis['successful_checks'] / analysis['total_codes'] * 100):.1f}%"
            },
            'storage_requirements': {
                'pdf_files': {
                    'size': pdf_size,
                    'formatted_size': self.format_size(pdf_size)
                },
                'processing_overhead': {
                    'extracted_text': overhead['extracted_text'],
                    'search_indexes': overhead['search_indexes'],
                    'database': overhead['database'],
                    'metadata': overhead['metadata'],
                    'total_overhead': overhead['total_overhead']
                },
                'total_storage_needed': {
                    'size': total_storage_needed,
                    'formatted_size': self.format_size(total_storage_needed)
                }
            },
            'category_breakdown': analysis['size_breakdown'],
            'time_estimates': {
                'download_time_minutes': int(estimated_download_time / 60),
                'processing_time_minutes': int(processing_time / 60),
                'total_time_minutes': int((estimated_download_time + processing_time) / 60)
            },
            'recommendations': {
                'minimum_disk_space': self.format_size(total_storage_needed * 1.5),  # 50% buffer
                'recommended_connection': f"{download_speed_mbps} Mbps or higher",
                'estimated_total_time': f"{int((estimated_download_time + processing_time) / 60)} minutes"
            }
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print formatted download report"""
        print("\n" + "=" * 80)
        print("📊 BELGIAN LEGAL KNOWLEDGE BASE - DOWNLOAD SIZE ANALYSIS")
        print("=" * 80)
        
        # Summary
        summary = report['summary']
        print(f"\n📋 SUMMARY:")
        print(f"   • Total Legal Codes: {summary['total_legal_codes']}")
        print(f"   • PDF Files to Download: {summary['pdf_files_to_download']}")
        print(f"   • Failed Checks: {summary['failed_checks']}")
        print(f"   • Success Rate: {summary['success_rate']}")
        
        # Storage Requirements
        storage = report['storage_requirements']
        print(f"\n💾 STORAGE REQUIREMENTS:")
        print(f"   • PDF Files: {storage['pdf_files']['formatted_size']}")
        print(f"   • Processing Overhead: {self.format_size(storage['processing_overhead']['total_overhead'])}")
        print(f"   • Total Storage Needed: {storage['total_storage_needed']['formatted_size']}")
        
        # Category Breakdown
        breakdown = report['category_breakdown']
        print(f"\n📂 CATEGORY BREAKDOWN:")
        for category, data in breakdown.items():
            if data['count'] > 0:
                print(f"   • {category.title()}: {data['count']} files, {self.format_size(data['size'])}")
        
        # Time Estimates
        time_est = report['time_estimates']
        print(f"\n⏱️  TIME ESTIMATES:")
        print(f"   • Download Time: {time_est['download_time_minutes']} minutes")
        print(f"   • Processing Time: {time_est['processing_time_minutes']} minutes")
        print(f"   • Total Time: {time_est['total_time_minutes']} minutes")
        
        # Recommendations
        rec = report['recommendations']
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"   • Minimum Disk Space: {rec['minimum_disk_space']}")
        print(f"   • Recommended Connection: {rec['recommended_connection']}")
        print(f"   • Estimated Total Time: {rec['estimated_total_time']}")
        
        print("\n" + "=" * 80)
        
        # Detailed breakdown
        print(f"\n🔍 DETAILED BREAKDOWN:")
        overhead = storage['processing_overhead']
        print(f"   • Extracted Text: {self.format_size(overhead['extracted_text'])}")
        print(f"   • Search Indexes: {self.format_size(overhead['search_indexes'])}")
        print(f"   • Database: {self.format_size(overhead['database'])}")
        print(f"   • Metadata: {self.format_size(overhead['metadata'])}")
        
        print("\n" + "=" * 80)
    
    def save_report(self, report: Dict[str, Any], filename: str = "download_size_analysis.json"):
        """Save the analysis report to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"Analysis report saved to {filename}")
    
    def run_analysis(self):
        """Run complete download size analysis"""
        logger.info("Starting download size analysis...")
        
        # Load legal codes
        legal_codes = self.load_legal_codes()
        if not legal_codes:
            logger.error("No legal codes found. Cannot proceed with analysis.")
            return None
        
        # Analyze PDF sizes
        analysis = self.analyze_pdf_sizes(legal_codes)
        
        # Generate report
        report = self.generate_download_report(analysis)
        
        # Print and save report
        self.print_report(report)
        self.save_report(report)
        
        return report

def main():
    """Main function"""
    print("🔍 Belgian Legal Knowledge Base - Download Size Analysis")
    print("=" * 60)
    print("This will analyze the exact size requirements for downloading")
    print("the complete Belgian legal knowledge base.")
    print("=" * 60)
    
    analyzer = DownloadSizeAnalyzer()
    
    try:
        report = analyzer.run_analysis()
        
        if report:
            print("\n✅ Analysis completed successfully!")
            print("📁 Report saved to: download_size_analysis.json")
            
            # Ask for confirmation
            print("\n" + "=" * 60)
            print("⚠️  DOWNLOAD CONFIRMATION REQUIRED")
            print("=" * 60)
            print(f"Total storage needed: {report['storage_requirements']['total_storage_needed']['formatted_size']}")
            print(f"Estimated time: {report['time_estimates']['total_time_minutes']} minutes")
            print("\nTo proceed with the download, run:")
            print("python3 setup_offline_legal_knowledge.py")
            
        else:
            print("\n❌ Analysis failed. Check the logs for details.")
            
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed with error: {e}")
        logger.error(f"Analysis failed: {e}")

if __name__ == "__main__":
    main() 