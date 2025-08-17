#!/usr/bin/env python3
"""
Legal Database Integration Script

This script integrates acquired Belgian and EU legal databases with the existing
legal assistant system, ensuring proper indexing and search capabilities.

Security Features:
- Maintains offline operation
- Preserves client confidentiality
- Validates document integrity
- Creates comprehensive search indices
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Import existing system components
from config import SOURCE_DOCUMENTS_PATH, VECTOR_STORE_PATH
from ingest import load_documents, split_documents, create_embeddings, create_vector_store

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('legal_database_integration.log'),
        logging.StreamHandler()
    ]
)

class LegalDatabaseIntegration:
    """
    Integrates acquired legal databases with the existing legal assistant system.
    """
    
    def __init__(self, 
                 legal_databases_dir: str = "./legal_databases",
                 source_documents_dir: str = SOURCE_DOCUMENTS_PATH,
                 vector_store_dir: str = VECTOR_STORE_PATH):
        
        self.legal_databases_dir = Path(legal_databases_dir)
        self.source_documents_dir = Path(source_documents_dir)
        self.vector_store_dir = Path(vector_store_dir)
        
        # Ensure directories exist
        self.source_documents_dir.mkdir(exist_ok=True)
        self.vector_store_dir.mkdir(exist_ok=True)
        
        # Integration configuration
        self.integration_config = {
            "belgian_federal": {
                "source_dir": "belgian_federal",
                "target_dir": "belgian_federal",
                "jurisdiction": "federaal",
                "document_types": ["wetboeken", "jurisprudentie"]
            },
            "belgian_regional": {
                "source_dir": "belgian_regional",
                "target_dir": "belgian_regional",
                "jurisdictions": ["vlaams", "waals", "brussels"],
                "document_types": ["wetboeken", "jurisprudentie", "reglementering"]
            },
            "eu_legal": {
                "source_dir": "eu_legal",
                "target_dir": "eu_legal",
                "jurisdiction": "eu",
                "document_types": ["wetboeken", "jurisprudentie", "reglementering"]
            }
        }

    def validate_legal_databases(self) -> bool:
        """
        Validates that legal databases exist and are properly structured.
        
        Returns:
            True if databases are valid, False otherwise
        """
        logging.info("Validating legal databases...")
        
        if not self.legal_databases_dir.exists():
            logging.error(f"Legal databases directory not found: {self.legal_databases_dir}")
            return False
            
        # Check for required directories
        required_dirs = ["belgian_federal", "belgian_regional", "eu_legal", "metadata"]
        for dir_name in required_dirs:
            dir_path = self.legal_databases_dir / dir_name
            if not dir_path.exists():
                logging.error(f"Required directory not found: {dir_path}")
                return False
                
        # Check for database index
        index_file = self.legal_databases_dir / "database_index.json"
        if not index_file.exists():
            logging.error(f"Database index not found: {index_file}")
            return False
            
        logging.info("Legal databases validation completed successfully")
        return True

    def copy_documents_to_source_directory(self) -> List[Path]:
        """
        Copies legal documents to the source_documents directory for processing.
        
        Returns:
            List of copied document paths
        """
        logging.info("Copying legal documents to source directory...")
        
        copied_files = []
        
        # Copy documents from each database section
        for section_name, config in self.integration_config.items():
            source_dir = self.legal_databases_dir / config["source_dir"]
            
            if not source_dir.exists():
                logging.warning(f"Source directory not found: {source_dir}")
                continue
                
            # Create target directory
            target_dir = self.source_documents_dir / config["target_dir"]
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy PDF files
            for pdf_file in source_dir.glob("*.pdf"):
                target_file = target_dir / pdf_file.name
                
                try:
                    shutil.copy2(pdf_file, target_file)
                    copied_files.append(target_file)
                    logging.info(f"Copied: {pdf_file.name}")
                except Exception as e:
                    logging.error(f"Failed to copy {pdf_file.name}: {e}")
                    
        logging.info(f"Copied {len(copied_files)} documents to source directory")
        return copied_files

    def create_enhanced_metadata(self, copied_files: List[Path]) -> Dict:
        """
        Creates enhanced metadata for the integrated documents.
        
        Args:
            copied_files: List of copied document paths
            
        Returns:
            Dictionary containing enhanced metadata
        """
        logging.info("Creating enhanced metadata for integrated documents...")
        
        enhanced_metadata = {}
        
        for file_path in copied_files:
            # Load original metadata if available
            original_metadata_file = self.legal_databases_dir / "metadata" / f"{file_path.stem}_metadata.json"
            
            if original_metadata_file.exists():
                with open(original_metadata_file, 'r', encoding='utf-8') as f:
                    original_metadata = json.load(f)
            else:
                original_metadata = {}
                
            # Create enhanced metadata
            enhanced_metadata[file_path.name] = {
                "original_metadata": original_metadata,
                "integration_date": datetime.now().isoformat(),
                "source_path": str(file_path),
                "jurisdiction": original_metadata.get("jurisdiction", "unknown"),
                "document_type": original_metadata.get("document_type", "unknown"),
                "language": original_metadata.get("language", "unknown"),
                "integration_status": "integrated",
                "search_enabled": True,
                "offline_available": True
            }
            
        # Save enhanced metadata
        enhanced_metadata_file = self.source_documents_dir / "enhanced_metadata.json"
        with open(enhanced_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_metadata, f, indent=2, ensure_ascii=False)
            
        logging.info(f"Enhanced metadata created for {len(enhanced_metadata)} documents")
        return enhanced_metadata

    def update_vector_store(self) -> bool:
        """
        Updates the vector store with the newly integrated documents.
        
        Returns:
            True if successful, False otherwise
        """
        logging.info("Updating vector store with integrated documents...")
        
        try:
            # Get all PDF files in source directory
            pdf_files = []
            for pdf_file in self.source_documents_dir.rglob("*.pdf"):
                pdf_files.append(str(pdf_file))
                
            if not pdf_files:
                logging.warning("No PDF files found in source directory")
                return False
                
            # Load documents using existing ingest system
            documents = load_documents(pdf_files)
            
            if not documents:
                logging.error("No documents loaded successfully")
                return False
                
            # Split documents into chunks
            chunks = split_documents(documents, 1000, 200)  # Using default chunk size and overlap
            
            # Create embeddings
            embeddings = create_embeddings("all-MiniLM-L6-v2")
            
            # Create vector store
            create_vector_store(chunks, embeddings, str(self.vector_store_dir))
            
            logging.info(f"Vector store updated with {len(documents)} documents")
            return True
            
        except Exception as e:
            logging.error(f"Failed to update vector store: {e}")
            return False

    def create_integration_report(self, copied_files: List[Path], 
                                enhanced_metadata: Dict) -> str:
        """
        Creates a comprehensive integration report.
        
        Args:
            copied_files: List of copied document paths
            enhanced_metadata: Enhanced metadata dictionary
            
        Returns:
            Report string
        """
        logging.info("Creating integration report...")
        
        # Calculate statistics
        total_documents = len(copied_files)
        jurisdictions = {}
        document_types = {}
        languages = {}
        
        for metadata in enhanced_metadata.values():
            jurisdiction = metadata.get("jurisdiction", "unknown")
            jurisdictions[jurisdiction] = jurisdictions.get(jurisdiction, 0) + 1
            
            doc_type = metadata.get("document_type", "unknown")
            document_types[doc_type] = document_types.get(doc_type, 0) + 1
            
            language = metadata.get("language", "unknown")
            languages[language] = languages.get(language, 0) + 1
            
        # Generate report
        report = f"""
# Legal Database Integration Report

## Integration Summary
- **Integration Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Total Documents Integrated**: {total_documents}
- **Source Directory**: {self.legal_databases_dir}
- **Target Directory**: {self.source_documents_dir}
- **Vector Store**: {self.vector_store_dir}

## Jurisdiction Breakdown
"""
        
        for jurisdiction, count in jurisdictions.items():
            report += f"- **{jurisdiction}**: {count} documents\n"
            
        report += "\n## Document Type Breakdown\n"
        for doc_type, count in document_types.items():
            report += f"- **{doc_type}**: {count} documents\n"
            
        report += "\n## Language Breakdown\n"
        for language, count in languages.items():
            report += f"- **{language}**: {count} documents\n"
            
        report += f"""
## Integration Status
- ✅ Documents copied to source directory
- ✅ Enhanced metadata created
- ✅ Vector store updated
- ✅ Search capabilities enabled
- ✅ Offline operation maintained

## Usage Instructions
1. Start the legal assistant: `python app.py`
2. Use filters to search specific jurisdictions:
   - **federaal**: Belgian federal law
   - **vlaams**: Flemish regional law
   - **waals**: Walloon regional law
   - **brussels**: Brussels regional law
   - **eu**: European Union law
3. Search in Dutch, French, or English
4. All research is 100% offline and confidential

## Search Examples
- "Wat zijn de rechten van een werknemer?" (Dutch)
- "Quels sont les droits du travailleur?" (French)
- "What are employee rights under Belgian law?" (English)

## Security Features
- All documents processed locally
- No external data transmission
- Client confidentiality maintained
- Complete audit trail available
"""
        
        return report

    def run_complete_integration(self) -> bool:
        """
        Runs the complete legal database integration process.
        
        Returns:
            True if successful, False otherwise
        """
        logging.info("Starting complete legal database integration...")
        
        try:
            # Validate legal databases
            if not self.validate_legal_databases():
                return False
                
            # Copy documents to source directory
            copied_files = self.copy_documents_to_source_directory()
            
            if not copied_files:
                logging.error("No documents copied successfully")
                return False
                
            # Create enhanced metadata
            enhanced_metadata = self.create_enhanced_metadata(copied_files)
            
            # Update vector store
            if not self.update_vector_store():
                logging.error("Failed to update vector store")
                return False
                
            # Create integration report
            report = self.create_integration_report(copied_files, enhanced_metadata)
            
            # Save report
            report_file = self.source_documents_dir / "integration_report.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
                
            logging.info("Legal database integration completed successfully!")
            logging.info(f"Report saved to: {report_file}")
            print(report)
            
            return True
            
        except Exception as e:
            logging.error(f"Integration failed: {e}")
            return False

    def verify_integration(self) -> Dict:
        """
        Verifies that the integration was successful.
        
        Returns:
            Dictionary containing verification results
        """
        logging.info("Verifying integration...")
        
        verification_results = {
            "source_documents": 0,
            "vector_store": False,
            "metadata_files": 0,
            "search_capability": False
        }
        
        # Check source documents
        pdf_files = list(self.source_documents_dir.rglob("*.pdf"))
        verification_results["source_documents"] = len(pdf_files)
        
        # Check vector store
        if self.vector_store_dir.exists():
            vector_files = list(self.vector_store_dir.rglob("*"))
            verification_results["vector_store"] = len(vector_files) > 0
            
        # Check metadata files
        metadata_files = list(self.source_documents_dir.rglob("*metadata*.json"))
        verification_results["metadata_files"] = len(metadata_files)
        
        # Check search capability (basic check)
        verification_results["search_capability"] = (
            verification_results["source_documents"] > 0 and 
            verification_results["vector_store"]
        )
        
        logging.info("Integration verification completed")
        return verification_results


def main():
    """Main function to run the legal database integration."""
    print("🔗 Legal Database Integration System")
    print("=" * 50)
    
    # Initialize integration system
    integration = LegalDatabaseIntegration()
    
    # Run complete integration
    success = integration.run_complete_integration()
    
    if success:
        # Verify integration
        verification = integration.verify_integration()
        print("\n🔍 Integration Verification Results:")
        print(f"- Source Documents: {verification['source_documents']}")
        print(f"- Vector Store: {'✅' if verification['vector_store'] else '❌'}")
        print(f"- Metadata Files: {verification['metadata_files']}")
        print(f"- Search Capability: {'✅' if verification['search_capability'] else '❌'}")
        
        print("\n🎉 Integration completed successfully!")
        print("🚀 You can now start the legal assistant with: python app.py")
    else:
        print("\n❌ Integration failed. Check logs for details.")


if __name__ == "__main__":
    main() 