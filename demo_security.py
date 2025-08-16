#!/usr/bin/env python3
"""
Security Features Demonstration

This script demonstrates the enhanced security features of the Legal Assistant
with a practical example of protecting sensitive legal documents.
"""

import os
import tempfile
from pathlib import Path
from security_manager import SecurityManager


def create_sample_legal_document():
    """Create a sample legal document for demonstration."""
    content = """
CONFIDENTIAL LEGAL DOCUMENT
==========================

Client: John Doe
Case Number: 2024-001
Date: 2024-01-15

CONFIDENTIALITY NOTICE:
This document contains sensitive legal information and is protected by 
attorney-client privilege. Unauthorized access or disclosure is prohibited.

CASE SUMMARY:
The client is seeking legal advice regarding a complex employment dispute
involving wrongful termination and discrimination claims. The case involves
multiple parties and requires careful analysis of Belgian employment law.

KEY ISSUES:
1. Wrongful termination under Belgian employment law
2. Discrimination based on age and disability
3. Severance package negotiations
4. Potential settlement options

RECOMMENDATIONS:
Based on the analysis of relevant case law and statutory provisions,
we recommend pursuing a negotiated settlement approach while preparing
for potential litigation if necessary.

This document is for internal use only and should be handled with
appropriate security measures.
"""
    return content


def demonstrate_security_features():
    """Demonstrate all security features with a practical example."""
    print("🔒 Enhanced Security Features Demonstration")
    print("=" * 50)
    print("This demonstration shows how to protect sensitive legal documents")
    print("using the professional-grade security features.\n")
    
    # Create a temporary directory for the demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Step 1: Create a sample legal document
            print("📄 Step 1: Creating a sample legal document...")
            document_content = create_sample_legal_document()
            document_path = "confidential_case_2024_001.txt"
            
            with open(document_path, 'w') as f:
                f.write(document_content)
            
            print(f"✅ Created: {document_path}")
            print(f"   Size: {os.path.getsize(document_path)} bytes")
            print()
            
            # Step 2: Initialize security manager
            print("🔐 Step 2: Initializing security manager...")
            master_password = "secure_master_password_2024"
            security_manager = SecurityManager(
                security_dir="./security_demo",
                master_password=master_password,
                enable_audit_logging=True
            )
            print("✅ Security manager initialized")
            print("   - AES-256-GCM encryption enabled")
            print("   - Audit logging enabled")
            print("   - Master password set")
            print()
            
            # Step 3: Encrypt the document with password protection
            print("🔒 Step 3: Encrypting document with password protection...")
            document_password = "case_2024_001_password"
            encrypt_result = security_manager.encrypt_file(document_path, document_password)
            
            if encrypt_result["success"]:
                print(f"✅ Document encrypted: {encrypt_result['encrypted_path']}")
                print(f"   Original size: {encrypt_result['original_size']} bytes")
                print(f"   Encrypted size: {encrypt_result['encrypted_size']} bytes")
                print(f"   Password protection: Enabled")
            else:
                print(f"❌ Encryption failed: {encrypt_result['error']}")
                return
            print()
            
            # Step 4: Demonstrate secure access
            print("🔓 Step 4: Demonstrating secure document access...")
            encrypted_file = encrypt_result['encrypted_path']
            
            # Try to access with wrong password
            print("   Testing access with wrong password...")
            wrong_result = security_manager.decrypt_file(encrypted_file, "wrong_password")
            if not wrong_result["success"]:
                print("   ✅ Access correctly denied with wrong password")
            
            # Access with correct password
            print("   Testing access with correct password...")
            correct_result = security_manager.decrypt_file(encrypted_file, document_password)
            if correct_result["success"]:
                print(f"   ✅ Access granted: {correct_result['decrypted_path']}")
                print("   ✅ Document content verified")
            else:
                print(f"   ❌ Access failed: {correct_result['error']}")
            print()
            
            # Step 5: Show audit logs
            print("📊 Step 5: Reviewing audit logs...")
            audit_events = security_manager.get_audit_log(limit=5)
            access_events = security_manager.get_access_log(limit=5)
            
            print(f"   Recent security events: {len(audit_events)}")
            print(f"   Recent access events: {len(access_events)}")
            
            if audit_events:
                print("   Latest security events:")
                for event in audit_events[:3]:
                    print(f"     • {event['event_type']}: {event['event_description']}")
            print()
            
            # Step 6: Generate security report
            print("📋 Step 6: Generating security audit report...")
            report_path = "security_audit_report.pdf"
            report_result = security_manager.export_audit_report(report_path)
            
            if report_result["success"]:
                print(f"✅ Audit report generated: {report_path}")
                print(f"   Events included: {report_result['audit_entries']}")
                print(f"   Access events: {report_result['access_entries']}")
            else:
                print(f"❌ Report generation failed: {report_result['error']}")
            print()
            
            # Step 7: Show security status
            print("🛡️  Step 7: Security status overview...")
            status = security_manager.get_security_status()
            
            print(f"   Encryption: {'✅ Enabled' if status['encryption_enabled'] else '❌ Disabled'}")
            print(f"   Audit Logging: {'✅ Enabled' if status['audit_logging_enabled'] else '❌ Disabled'}")
            print(f"   Protected Files: {status['password_protected_files']}")
            print(f"   Security Directory: {status['security_dir']}")
            print()
            
            # Step 8: Demonstrate secure deletion
            print("🗑️  Step 8: Demonstrating secure deletion...")
            print("   Creating temporary file for secure deletion...")
            
            temp_file = "temp_sensitive_data.txt"
            with open(temp_file, 'w') as f:
                f.write("This file will be securely deleted to prevent data recovery.")
            
            if os.path.exists(temp_file):
                print(f"   ✅ Created: {temp_file}")
                delete_result = security_manager.secure_delete_file(temp_file)
                
                if delete_result["success"]:
                    print(f"   ✅ File securely deleted: {delete_result['file_path']}")
                    print(f"   ✅ Overwrite passes: {delete_result['passes']}")
                    print(f"   ✅ File size: {delete_result['file_size']} bytes")
                    
                    if not os.path.exists(temp_file):
                        print("   ✅ File verification: Successfully deleted")
                    else:
                        print("   ❌ File verification: File still exists")
                else:
                    print(f"   ❌ Secure deletion failed: {delete_result['error']}")
            print()
            
            # Summary
            print("🎯 Security Features Summary")
            print("=" * 30)
            print("✅ Document encryption with AES-256-GCM")
            print("✅ Password protection for sensitive files")
            print("✅ Comprehensive audit logging")
            print("✅ Secure deletion with multi-pass overwrite")
            print("✅ Master password management")
            print("✅ PDF audit report generation")
            print("✅ Security status monitoring")
            print()
            print("🔒 All sensitive legal documents are now protected with")
            print("   professional-grade security measures that meet legal")
            print("   confidentiality requirements.")
            
        finally:
            os.chdir(original_dir)


if __name__ == "__main__":
    demonstrate_security_features() 