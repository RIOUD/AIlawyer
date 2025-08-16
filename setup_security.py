#!/usr/bin/env python3
"""
Security Setup Script for Legal Assistant AI Platform

This script helps users configure secure environment variables and validate
their security configuration for production deployment.
"""

import os
import secrets
import hashlib
import getpass
import re
from pathlib import Path
from typing import Dict, List, Optional


class SecuritySetup:
    """Security configuration setup and validation."""
    
    def __init__(self):
        self.env_file = Path(".env")
        self.template_file = Path("env.template")
        self.required_vars = [
            'SECRET_KEY',
            'MASTER_PASSWORD', 
            'JWT_SECRET',
            'ADMIN_PASSWORD'
        ]
    
    def run_setup(self):
        """Run the complete security setup process."""
        print("🔒 LEGAL ASSISTANT AI PLATFORM - SECURITY SETUP")
        print("=" * 60)
        
        # Check if .env file exists
        if self.env_file.exists():
            print("⚠️  .env file already exists!")
            overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
            if overwrite != 'y':
                print("Setup cancelled.")
                return
        
        # Generate secure secrets
        print("\n🔐 Generating secure secrets...")
        secrets_config = self._generate_secure_secrets()
        
        # Get user input for passwords
        print("\n🔑 Setting up passwords...")
        password_config = self._get_password_config()
        
        # Create .env file
        print("\n📝 Creating .env file...")
        self._create_env_file(secrets_config, password_config)
        
        # Validate configuration
        print("\n✅ Validating configuration...")
        self._validate_configuration()
        
        print("\n🎉 Security setup completed successfully!")
        print("\n⚠️  IMPORTANT SECURITY NOTES:")
        print("• Keep your .env file secure and never commit it to version control")
        print("• Store your passwords securely - you cannot recover them if lost")
        print("• Change the default admin password immediately after first login")
        print("• Regularly rotate your secrets in production environments")
        print("• Use a secrets management service for production deployments")
    
    def _generate_secure_secrets(self) -> Dict[str, str]:
        """Generate secure random secrets."""
        return {
            'SECRET_KEY': secrets.token_hex(32),
            'JWT_SECRET': secrets.token_hex(32)
        }
    
    def _get_password_config(self) -> Dict[str, str]:
        """Get password configuration from user."""
        config = {}
        
        # Master password
        while True:
            master_password = getpass.getpass("Enter master password (min 12 chars): ")
            if len(master_password) < 12:
                print("❌ Master password must be at least 12 characters long")
                continue
            
            confirm = getpass.getpass("Confirm master password: ")
            if master_password != confirm:
                print("❌ Passwords do not match")
                continue
            
            config['MASTER_PASSWORD'] = master_password
            break
        
        # Admin password
        while True:
            admin_password = getpass.getpass("Enter admin password (min 8 chars): ")
            if len(admin_password) < 8:
                print("❌ Admin password must be at least 8 characters long")
                continue
            
            confirm = getpass.getpass("Confirm admin password: ")
            if admin_password != confirm:
                print("❌ Passwords do not match")
                continue
            
            config['ADMIN_PASSWORD'] = admin_password
            break
        
        return config
    
    def _create_env_file(self, secrets_config: Dict[str, str], password_config: Dict[str, str]):
        """Create the .env file with secure configuration."""
        if not self.template_file.exists():
            raise FileNotFoundError("env.template file not found")
        
        # Read template
        with open(self.template_file, 'r') as f:
            template_content = f.read()
        
        # Replace placeholders with actual values
        env_content = template_content
        
        # Replace secrets
        env_content = env_content.replace('your_secure_secret_key_here_min_32_chars', secrets_config['SECRET_KEY'])
        env_content = env_content.replace('your_secure_jwt_secret_here_min_32_chars', secrets_config['JWT_SECRET'])
        
        # Replace passwords
        env_content = env_content.replace('your_secure_master_password_here_min_12_chars', password_config['MASTER_PASSWORD'])
        env_content = env_content.replace('your_secure_admin_password_here_min_8_chars', password_config['ADMIN_PASSWORD'])
        
        # Write .env file
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        # Set secure permissions (Unix-like systems)
        try:
            os.chmod(self.env_file, 0o600)  # Owner read/write only
            print(f"✅ Created .env file with secure permissions")
        except Exception as e:
            print(f"⚠️  Created .env file but could not set secure permissions: {e}")
    
    def _validate_configuration(self):
        """Validate the security configuration."""
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        errors = []
        
        # Check required variables
        for var in self.required_vars:
            value = os.getenv(var)
            if not value:
                errors.append(f"Missing required environment variable: {var}")
            elif var in ['SECRET_KEY', 'JWT_SECRET'] and len(value) < 32:
                errors.append(f"{var} must be at least 32 characters long")
            elif var == 'MASTER_PASSWORD' and len(value) < 12:
                errors.append(f"{var} must be at least 12 characters long")
            elif var == 'ADMIN_PASSWORD' and len(value) < 8:
                errors.append(f"{var} must be at least 8 characters long")
        
        # Check password strength
        master_password = os.getenv('MASTER_PASSWORD')
        if master_password:
            if not self._is_strong_password(master_password):
                errors.append("Master password should contain uppercase, lowercase, numbers, and special characters")
        
        admin_password = os.getenv('ADMIN_PASSWORD')
        if admin_password:
            if not self._is_strong_password(admin_password):
                errors.append("Admin password should contain uppercase, lowercase, numbers, and special characters")
        
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"   • {error}")
            raise ValueError("Security configuration validation failed")
        else:
            print("✅ All security configurations are valid")
    
    def _is_strong_password(self, password: str) -> bool:
        """Check if password meets strength requirements."""
        if len(password) < 8:
            return False
        
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        return has_upper and has_lower and has_digit and has_special
    
    def validate_existing_config(self):
        """Validate existing configuration without modifying it."""
        print("🔍 Validating existing security configuration...")
        
        if not self.env_file.exists():
            print("❌ .env file not found")
            return False
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        try:
            self._validate_configuration()
            print("✅ Existing configuration is valid")
            return True
        except ValueError as e:
            print(f"❌ Configuration validation failed: {e}")
            return False


def main():
    """Main function for security setup."""
    setup = SecuritySetup()
    
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--validate':
        # Validate existing configuration
        setup.validate_existing_config()
    else:
        # Run full setup
        setup.run_setup()


if __name__ == "__main__":
    main() 