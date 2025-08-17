#!/usr/bin/env python3
"""
Setup Offline Legal Knowledge Base
Comprehensive script to download and process Belgian legal knowledge for offline use
"""

import os
import sys
import subprocess
import time
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('offline_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class OfflineLegalKnowledgeSetup:
    """Setup class for offline legal knowledge base"""
    
    def __init__(self):
        self.scripts = [
            'justel_scraper.py',
            'offline_legal_knowledge_downloader.py',
            'legal_content_processor.py'
        ]
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        logger.info("Checking dependencies...")
        
        required_packages = [
            'requests',
            'bs4',
            'PyPDF2',
            'sqlite3',
            'pathlib'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✓ {package}")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"✗ {package} - not found")
        
        if missing_packages:
            logger.error(f"Missing packages: {missing_packages}")
            logger.info("Install missing packages with: pip install " + " ".join(missing_packages))
            return False
        
        logger.info("All dependencies available")
        return True
    
    def run_script(self, script_name: str, description: str):
        """Run a Python script and handle errors"""
        logger.info(f"Running {description}...")
        
        try:
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✓ {description} completed successfully")
                if result.stdout:
                    logger.info(f"Output: {result.stdout}")
                return True
            else:
                logger.error(f"✗ {description} failed")
                logger.error(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"✗ {description} timed out")
            return False
        except Exception as e:
            logger.error(f"✗ {description} failed with exception: {e}")
            return False
    
    def setup_offline_knowledge_base(self):
        """Run the complete offline knowledge base setup"""
        logger.info("🚀 Starting Offline Legal Knowledge Base Setup")
        logger.info("=" * 60)
        
        # Step 1: Check dependencies
        if not self.check_dependencies():
            logger.error("Dependency check failed. Please install missing packages.")
            return False
        
        # Step 2: Scrape Justel database
        logger.info("\n📋 Step 1: Scraping Justel Database")
        if not self.run_script('justel_scraper.py', 'Justel Database Scraper'):
            logger.error("Justel scraping failed. Stopping setup.")
            return False
        
        # Step 3: Download legal knowledge
        logger.info("\n📥 Step 2: Downloading Legal Knowledge")
        if not self.run_script('offline_legal_knowledge_downloader.py', 'Legal Knowledge Downloader'):
            logger.error("Legal knowledge download failed. Stopping setup.")
            return False
        
        # Step 4: Process content
        logger.info("\n🔧 Step 3: Processing Legal Content")
        if not self.run_script('legal_content_processor.py', 'Legal Content Processor'):
            logger.error("Content processing failed. Stopping setup.")
            return False
        
        # Step 5: Verify setup
        logger.info("\n✅ Step 4: Verifying Setup")
        if self.verify_setup():
            logger.info("🎉 Offline Legal Knowledge Base Setup Completed Successfully!")
            self.print_summary()
            return True
        else:
            logger.error("❌ Setup verification failed")
            return False
    
    def verify_setup(self):
        """Verify that the setup was successful"""
        logger.info("Verifying offline knowledge base setup...")
        
        offline_dir = Path("offline_legal_knowledge")
        if not offline_dir.exists():
            logger.error("Offline data directory not found")
            return False
        
        # Check required files and directories
        required_items = [
            offline_dir / "legal_knowledge.db",
            offline_dir / "pdfs",
            offline_dir / "content",
            offline_dir / "metadata"
        ]
        
        for item in required_items:
            if not item.exists():
                logger.error(f"Required item not found: {item}")
                return False
        
        # Check metadata files
        metadata_dir = offline_dir / "metadata"
        metadata_files = [
            "legal_codes_metadata.json",
            "search_index.json",
            "processing_summary.json",
            "processing_report.json"
        ]
        
        for file_name in metadata_files:
            file_path = metadata_dir / file_name
            if not file_path.exists():
                logger.warning(f"Metadata file not found: {file_name}")
        
        # Check database content
        try:
            import sqlite3
            conn = sqlite3.connect(offline_dir / "legal_knowledge.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM legal_codes")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                logger.error("No legal codes found in database")
                return False
            
            logger.info(f"✓ Found {count} legal codes in database")
            
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            return False
        
        logger.info("✓ Setup verification completed successfully")
        return True
    
    def print_summary(self):
        """Print a summary of the setup"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 OFFLINE LEGAL KNOWLEDGE BASE SUMMARY")
        logger.info("=" * 60)
        
        offline_dir = Path("offline_legal_knowledge")
        
        # Database info
        try:
            import sqlite3
            conn = sqlite3.connect(offline_dir / "legal_knowledge.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM legal_codes")
            total_codes = cursor.fetchone()[0]
            
            cursor.execute("SELECT category, COUNT(*) FROM legal_codes GROUP BY category")
            categories = cursor.fetchall()
            conn.close()
            
            logger.info(f"📚 Total Legal Codes: {total_codes}")
            logger.info("📂 Categories:")
            for category, count in categories:
                logger.info(f"   • {category}: {count} codes")
                
        except Exception as e:
            logger.error(f"Could not read database summary: {e}")
        
        # File sizes
        try:
            pdfs_dir = offline_dir / "pdfs"
            if pdfs_dir.exists():
                pdf_files = list(pdfs_dir.glob("*.pdf"))
                total_pdf_size = sum(f.stat().st_size for f in pdf_files)
                logger.info(f"📄 PDF Files: {len(pdf_files)} files, {total_pdf_size / (1024*1024):.1f} MB")
            
            content_dir = offline_dir / "content"
            if content_dir.exists():
                txt_files = list(content_dir.glob("*.txt"))
                total_txt_size = sum(f.stat().st_size for f in txt_files)
                logger.info(f"📝 Text Files: {len(txt_files)} files, {total_txt_size / (1024*1024):.1f} MB")
                
        except Exception as e:
            logger.error(f"Could not calculate file sizes: {e}")
        
        logger.info("\n🎯 Next Steps:")
        logger.info("1. Start the web application: python3 web_app.py")
        logger.info("2. Navigate to the Research page")
        logger.info("3. Use the 'Offline Search' functionality")
        logger.info("4. Access the complete Belgian legal knowledge base offline")
        
        logger.info("\n📁 Data Location:")
        logger.info(f"   • Database: {offline_dir / 'legal_knowledge.db'}")
        logger.info(f"   • PDFs: {offline_dir / 'pdfs'}")
        logger.info(f"   • Content: {offline_dir / 'content'}")
        logger.info(f"   • Metadata: {offline_dir / 'metadata'}")
        
        logger.info("=" * 60)

def main():
    """Main function"""
    print("🔍 Belgian Legal Knowledge Base - Offline Setup")
    print("=" * 50)
    print("This script will:")
    print("1. Scrape the Justel database for legal codes")
    print("2. Download all PDFs and extract content")
    print("3. Process and index the content for offline search")
    print("4. Integrate with the web application")
    print("=" * 50)
    
    setup = OfflineLegalKnowledgeSetup()
    
    try:
        success = setup.setup_offline_knowledge_base()
        
        if success:
            print("\n✅ Setup completed successfully!")
            print("🚀 You can now use the offline legal knowledge base in the web application.")
        else:
            print("\n❌ Setup failed. Check the logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 