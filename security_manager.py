#!/usr/bin/env python3
"""
Security Manager for Secure Offline Legal Assistant

Provides professional-grade security features including:
- Document encryption at rest (AES-256)
- Access logging and audit trails
- Password protection for sensitive documents
- Secure deletion of documents
- Key management and secure storage
"""

import os
import json
import hashlib
import hmac
import secrets
import base64
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import bcrypt
import sqlite3


class SecurityManager:
    """
    Comprehensive security manager for the legal assistant application.
    
    Provides encryption, access control, audit logging, and secure deletion.
    """
    
    def __init__(self, 
                 security_dir: str = "./security",
                 master_password: Optional[str] = None,
                 enable_audit_logging: bool = True):
        """
        Initialize the security manager.
        
        Args:
            security_dir: Directory for security-related files
            master_password: Master password for encryption (if None, will prompt)
            enable_audit_logging: Whether to enable comprehensive audit logging
        """
        self.security_dir = Path(security_dir)
        self.security_dir.mkdir(exist_ok=True)
        
        # Security configuration
        self.enable_audit_logging = enable_audit_logging
        self.encryption_algorithm = "AES-256-GCM"
        self.key_derivation_rounds = 100000
        self.salt_size = 32
        self.iv_size = 16
        self.tag_size = 16
        
        # File paths
        self.keys_file = self.security_dir / "encryption_keys.json"
        self.audit_db = self.security_dir / "audit_log.db"
        self.access_control_file = self.security_dir / "access_control.json"
        
        # Initialize components
        self._init_audit_logging()
        self._init_access_control()
        self._init_encryption_keys(master_password)
        
        # Log security manager initialization
        self.log_security_event("SECURITY_MANAGER_INIT", "Security manager initialized successfully")
    
    def _init_audit_logging(self):
        """Initialize audit logging system."""
        if not self.enable_audit_logging:
            return
            
        # Create audit database
        with sqlite3.connect(self.audit_db) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT NOT NULL,
                    event_description TEXT NOT NULL,
                    user_id TEXT,
                    file_path TEXT,
                    ip_address TEXT,
                    success BOOLEAN DEFAULT TRUE,
                    additional_data TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource_path TEXT,
                    success BOOLEAN DEFAULT TRUE,
                    session_id TEXT,
                    ip_address TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                ON audit_log(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_access_timestamp 
                ON access_log(timestamp)
            """)
    
    def _init_access_control(self):
        """Initialize access control system."""
        if not self.access_control_file.exists():
            default_access_control = {
                "password_protected_files": {},
                "user_permissions": {},
                "session_timeouts": {
                    "default": 3600,  # 1 hour
                    "sensitive": 1800  # 30 minutes
                },
                "failed_login_attempts": {},
                "lockout_threshold": 5,
                "lockout_duration": 900  # 15 minutes
            }
            
            with open(self.access_control_file, 'w') as f:
                json.dump(default_access_control, f, indent=2)
    
    def _init_encryption_keys(self, master_password: Optional[str]):
        """Initialize encryption key management."""
        if not self.keys_file.exists():
            # Generate new encryption keys
            self._generate_new_keys(master_password)
        else:
            # Load existing keys
            self._load_existing_keys(master_password)
    
    def _generate_new_keys(self, master_password: Optional[str]):
        """Generate new encryption keys."""
        if master_password is None:
            master_password = self._prompt_master_password()
        
        # Generate master key
        master_salt = secrets.token_bytes(self.salt_size)
        master_key = self._derive_key(master_password, master_salt)
        
        # Generate document encryption key
        doc_key = secrets.token_bytes(32)  # AES-256 key
        
        # Encrypt document key with master key
        encrypted_doc_key = self._encrypt_with_key(doc_key, master_key)
        
        # Store keys securely
        keys_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "master_salt": base64.b64encode(master_salt).decode(),
            "encrypted_doc_key": base64.b64encode(encrypted_doc_key).decode(),
            "algorithm": self.encryption_algorithm
        }
        
        with open(self.keys_file, 'w') as f:
            json.dump(keys_data, f, indent=2)
        
        # Store keys in memory (encrypted)
        self.master_key = master_key
        self.doc_key = doc_key
        
        self.log_security_event("KEYS_GENERATED", "New encryption keys generated")
    
    def _load_existing_keys(self, master_password: Optional[str]):
        """Load existing encryption keys."""
        if master_password is None:
            master_password = self._prompt_master_password()
        
        with open(self.keys_file, 'r') as f:
            keys_data = json.load(f)
        
        # Reconstruct master key
        master_salt = base64.b64decode(keys_data["master_salt"])
        master_key = self._derive_key(master_password, master_salt)
        
        # Decrypt document key
        encrypted_doc_key = base64.b64decode(keys_data["encrypted_doc_key"])
        doc_key = self._decrypt_with_key(encrypted_doc_key, master_key)
        
        # Store keys in memory
        self.master_key = master_key
        self.doc_key = doc_key
        
        self.log_security_event("KEYS_LOADED", "Existing encryption keys loaded")
    
    def _prompt_master_password(self) -> str:
        """Prompt user for master password."""
        import getpass
        print("🔐 Security Setup Required")
        print("Enter a master password for document encryption:")
        password = getpass.getpass("Master Password: ")
        
        if len(password) < 8:
            raise ValueError("Master password must be at least 8 characters long")
        
        confirm = getpass.getpass("Confirm Master Password: ")
        if password != confirm:
            raise ValueError("Passwords do not match")
        
        return password
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.key_derivation_rounds,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    def _encrypt_with_key(self, data: bytes, key: bytes) -> bytes:
        """Encrypt data with AES-256-GCM."""
        iv = secrets.token_bytes(self.iv_size)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(data) + encryptor.finalize()
        return iv + encryptor.tag + ciphertext
    
    def _decrypt_with_key(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt data with AES-256-GCM."""
        iv = encrypted_data[:self.iv_size]
        tag = encrypted_data[self.iv_size:self.iv_size + self.tag_size]
        ciphertext = encrypted_data[self.iv_size + self.tag_size:]
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def encrypt_file(self, file_path: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Encrypt a file with AES-256-GCM.
        
        Args:
            file_path: Path to the file to encrypt
            password: Optional password for additional protection
            
        Returns:
            Dictionary with encryption result
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {"success": False, "error": "File not found"}
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Encrypt content
            encrypted_content = self._encrypt_with_key(file_content, self.doc_key)
            
            # Create encrypted file path
            encrypted_path = file_path.with_suffix(file_path.suffix + '.encrypted')
            
            # Write encrypted content
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_content)
            
            # Add password protection if specified
            if password:
                self._add_password_protection(str(encrypted_path), password)
            
            # Log encryption
            self.log_security_event("FILE_ENCRYPTED", f"File encrypted: {file_path}")
            self.log_access_event("ENCRYPT", str(file_path), True)
            
            return {
                "success": True,
                "encrypted_path": str(encrypted_path),
                "original_size": len(file_content),
                "encrypted_size": len(encrypted_content)
            }
            
        except Exception as e:
            self.log_security_event("ENCRYPTION_ERROR", f"Encryption failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def decrypt_file(self, encrypted_file_path: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Decrypt a file.
        
        Args:
            encrypted_file_path: Path to the encrypted file
            password: Password if file is password protected
            
        Returns:
            Dictionary with decryption result
        """
        try:
            encrypted_file_path = Path(encrypted_file_path)
            if not encrypted_file_path.exists():
                return {"success": False, "error": "Encrypted file not found"}
            
            # Check password protection
            if self._is_password_protected(str(encrypted_file_path)):
                if not password:
                    return {"success": False, "error": "Password required"}
                if not self._verify_password_protection(str(encrypted_file_path), password):
                    return {"success": False, "error": "Incorrect password"}
            
            # Read encrypted content
            with open(encrypted_file_path, 'rb') as f:
                encrypted_content = f.read()
            
            # Decrypt content
            decrypted_content = self._decrypt_with_key(encrypted_content, self.doc_key)
            
            # Create decrypted file path
            decrypted_path = encrypted_file_path.with_suffix('').with_suffix('')
            if decrypted_path.suffix == '.encrypted':
                decrypted_path = decrypted_path.with_suffix('')
            
            # Write decrypted content
            with open(decrypted_path, 'wb') as f:
                f.write(decrypted_content)
            
            # Log decryption
            self.log_security_event("FILE_DECRYPTED", f"File decrypted: {encrypted_file_path}")
            self.log_access_event("DECRYPT", str(encrypted_file_path), True)
            
            return {
                "success": True,
                "decrypted_path": str(decrypted_path),
                "original_size": len(encrypted_content),
                "decrypted_size": len(decrypted_content)
            }
            
        except Exception as e:
            self.log_security_event("DECRYPTION_ERROR", f"Decryption failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _add_password_protection(self, file_path: str, password: str):
        """Add password protection to a file."""
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        with open(self.access_control_file, 'r') as f:
            access_control = json.load(f)
        
        access_control["password_protected_files"][file_path] = {
            "password_hash": base64.b64encode(password_hash).decode(),
            "protected_at": datetime.now().isoformat()
        }
        
        with open(self.access_control_file, 'w') as f:
            json.dump(access_control, f, indent=2)
    
    def _is_password_protected(self, file_path: str) -> bool:
        """Check if a file is password protected."""
        with open(self.access_control_file, 'r') as f:
            access_control = json.load(f)
        
        return file_path in access_control["password_protected_files"]
    
    def _verify_password_protection(self, file_path: str, password: str) -> bool:
        """Verify password for a protected file."""
        with open(self.access_control_file, 'r') as f:
            access_control = json.load(f)
        
        if file_path not in access_control["password_protected_files"]:
            return False
        
        stored_hash = base64.b64decode(
            access_control["password_protected_files"][file_path]["password_hash"]
        )
        
        return bcrypt.checkpw(password.encode(), stored_hash)
    
    def secure_delete_file(self, file_path: str, passes: int = 3) -> Dict[str, Any]:
        """
        Securely delete a file using multiple overwrites.
        
        Args:
            file_path: Path to the file to delete
            passes: Number of overwrite passes (default: 3)
            
        Returns:
            Dictionary with deletion result
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {"success": False, "error": "File not found"}
            
            file_size = file_path.stat().st_size
            
            # Multiple overwrite passes
            patterns = [
                b'\x00' * 1024,  # Zeros
                b'\xFF' * 1024,  # Ones
                secrets.token_bytes(1024),  # Random data
            ]
            
            with open(file_path, 'r+b') as f:
                for i in range(passes):
                    f.seek(0)
                    pattern = patterns[i % len(patterns)]
                    
                    # Overwrite in chunks
                    remaining = file_size
                    while remaining > 0:
                        chunk_size = min(1024, remaining)
                        f.write(pattern[:chunk_size])
                        remaining -= chunk_size
                    
                    f.flush()
                    os.fsync(f.fileno())
            
            # Delete the file
            file_path.unlink()
            
            # Log secure deletion
            self.log_security_event("SECURE_DELETE", f"File securely deleted: {file_path}")
            self.log_access_event("SECURE_DELETE", str(file_path), True)
            
            return {
                "success": True,
                "file_path": str(file_path),
                "passes": passes,
                "file_size": file_size
            }
            
        except Exception as e:
            self.log_security_event("SECURE_DELETE_ERROR", f"Secure deletion failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def log_security_event(self, event_type: str, description: str, 
                          additional_data: Optional[Dict] = None):
        """Log a security event to the audit database."""
        if not self.enable_audit_logging:
            return
        
        try:
            with sqlite3.connect(self.audit_db) as conn:
                conn.execute("""
                    INSERT INTO audit_log 
                    (event_type, event_description, additional_data)
                    VALUES (?, ?, ?)
                """, (
                    event_type,
                    description,
                    json.dumps(additional_data) if additional_data else None
                ))
        except Exception as e:
            print(f"Warning: Failed to log security event: {e}")
    
    def log_access_event(self, action: str, resource_path: str, success: bool,
                        user_id: Optional[str] = None, session_id: Optional[str] = None):
        """Log an access event to the audit database."""
        if not self.enable_audit_logging:
            return
        
        try:
            with sqlite3.connect(self.audit_db) as conn:
                conn.execute("""
                    INSERT INTO access_log 
                    (action, resource_path, success, user_id, session_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (action, resource_path, success, user_id, session_id))
        except Exception as e:
            print(f"Warning: Failed to log access event: {e}")
    
    def get_audit_log(self, 
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None,
                     event_type: Optional[str] = None,
                     limit: int = 100) -> List[Dict]:
        """
        Retrieve audit log entries.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            event_type: Filter by event type
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries
        """
        if not self.enable_audit_logging:
            return []
        
        try:
            with sqlite3.connect(self.audit_db) as conn:
                query = "SELECT * FROM audit_log WHERE 1=1"
                params = []
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                columns = [description[0] for description in cursor.description]
                
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Warning: Failed to retrieve audit log: {e}")
            return []
    
    def get_access_log(self,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      action: Optional[str] = None,
                      limit: int = 100) -> List[Dict]:
        """
        Retrieve access log entries.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            action: Filter by action type
            limit: Maximum number of entries to return
            
        Returns:
            List of access log entries
        """
        if not self.enable_audit_logging:
            return []
        
        try:
            with sqlite3.connect(self.audit_db) as conn:
                query = "SELECT * FROM access_log WHERE 1=1"
                params = []
                
                if start_date:
                    query += " AND timestamp >= ?"
                    params.append(start_date.isoformat())
                
                if end_date:
                    query += " AND timestamp <= ?"
                    params.append(end_date.isoformat())
                
                if action:
                    query += " AND action = ?"
                    params.append(action)
                
                query += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                columns = [description[0] for description in cursor.description]
                
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Warning: Failed to retrieve access log: {e}")
            return []
    
    def export_audit_report(self, output_path: str, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Export audit report to PDF.
        
        Args:
            output_path: Path for the output PDF file
            start_date: Start date for the report
            end_date: End date for the report
            
        Returns:
            Dictionary with export result
        """
        try:
            # Get audit data
            audit_entries = self.get_audit_log(start_date, end_date, limit=1000)
            access_entries = self.get_access_log(start_date, end_date, limit=1000)
            
            # Generate PDF report
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                alignment=1,  # Center
                textColor=colors.darkblue
            )
            
            story.append(Paragraph("Security Audit Report", title_style))
            story.append(Spacer(1, 12))
            
            # Summary
            story.append(Paragraph("Summary", styles['Heading2']))
            story.append(Paragraph(f"Report Period: {start_date or 'All time'} to {end_date or 'Now'}", styles['Normal']))
            story.append(Paragraph(f"Security Events: {len(audit_entries)}", styles['Normal']))
            story.append(Paragraph(f"Access Events: {len(access_entries)}", styles['Normal']))
            story.append(Spacer(1, 12))
            
            # Security Events Table
            if audit_entries:
                story.append(Paragraph("Security Events", styles['Heading2']))
                
                data = [['Timestamp', 'Event Type', 'Description']]
                for entry in audit_entries[:50]:  # Limit to 50 entries
                    data.append([
                        entry['timestamp'],
                        entry['event_type'],
                        entry['event_description'][:50] + '...' if len(entry['event_description']) > 50 else entry['event_description']
                    ])
                
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 12))
            
            # Build PDF
            doc.build(story)
            
            self.log_security_event("AUDIT_REPORT_EXPORTED", f"Audit report exported to {output_path}")
            
            return {
                "success": True,
                "output_path": output_path,
                "audit_entries": len(audit_entries),
                "access_entries": len(access_entries)
            }
            
        except Exception as e:
            self.log_security_event("AUDIT_REPORT_ERROR", f"Audit report export failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def change_master_password(self, new_password: str) -> Dict[str, Any]:
        """
        Change the master password.
        
        Args:
            new_password: New master password
            
        Returns:
            Dictionary with result
        """
        try:
            if len(new_password) < 8:
                return {"success": False, "error": "Password must be at least 8 characters long"}
            
            # Generate new master key
            master_salt = secrets.token_bytes(self.salt_size)
            new_master_key = self._derive_key(new_password, master_salt)
            
            # Re-encrypt document key with new master key
            encrypted_doc_key = self._encrypt_with_key(self.doc_key, new_master_key)
            
            # Update keys file
            with open(self.keys_file, 'r') as f:
                keys_data = json.load(f)
            
            keys_data["master_salt"] = base64.b64encode(master_salt).decode()
            keys_data["encrypted_doc_key"] = base64.b64encode(encrypted_doc_key).decode()
            keys_data["updated_at"] = datetime.now().isoformat()
            
            with open(self.keys_file, 'w') as f:
                json.dump(keys_data, f, indent=2)
            
            # Update in-memory keys
            self.master_key = new_master_key
            
            self.log_security_event("MASTER_PASSWORD_CHANGED", "Master password changed successfully")
            
            return {"success": True, "message": "Master password changed successfully"}
            
        except Exception as e:
            self.log_security_event("PASSWORD_CHANGE_ERROR", f"Password change failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get current security status.
        
        Returns:
            Dictionary with security status information
        """
        try:
            # Count password protected files
            with open(self.access_control_file, 'r') as f:
                access_control = json.load(f)
            
            protected_files_count = len(access_control["password_protected_files"])
            
            # Get recent security events
            recent_events = self.get_audit_log(limit=10)
            
            # Get recent access events
            recent_access = self.get_access_log(limit=10)
            
            return {
                "encryption_enabled": True,
                "audit_logging_enabled": self.enable_audit_logging,
                "password_protected_files": protected_files_count,
                "recent_security_events": len(recent_events),
                "recent_access_events": len(recent_access),
                "security_dir": str(self.security_dir),
                "keys_file_exists": self.keys_file.exists(),
                "audit_db_exists": self.audit_db.exists()
            }
            
        except Exception as e:
            return {"error": str(e)} 