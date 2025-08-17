#!/usr/bin/env python3
"""
Simple Authentication System for Legal Platform

Provides basic authentication functionality for the legal practice management platform.
"""

import os
import secrets
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class User:
    """User data class."""
    user_id: str
    email: str
    name: str
    role: str  # lawyer, admin, assistant
    created_at: datetime
    last_login: Optional[datetime] = None

class AuthSystem:
    """Simple authentication system."""
    
    def __init__(self):
        """Initialize the authentication system."""
        self.secret_key = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        
        # In-memory user storage (replace with database in production)
        self.users = {}
        self.sessions = {}
        
        # Create default admin user
        self._create_default_users()
    
    def _create_default_users(self):
        """Create default users for testing."""
        admin_user = User(
            user_id="admin-001",
            email="admin@legalplatform.com",
            name="Admin User",
            role="admin",
            created_at=datetime.now()
        )
        self.users[admin_user.email] = admin_user
        
        lawyer_user = User(
            user_id="lawyer-001",
            email="lawyer@legalplatform.com",
            name="Test Lawyer",
            role="lawyer",
            created_at=datetime.now()
        )
        self.users[lawyer_user.email] = lawyer_user
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        return self.hash_password(password) == hashed
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = self.users.get(email)
        if not user:
            return None
        
        # For demo purposes, accept any password for existing users
        # In production, you would verify against hashed passwords
        if email == "admin@legalplatform.com" and password == "admin123":
            return user
        elif email == "lawyer@legalplatform.com" and password == "lawyer123":
            return user
        
        return None
    
    def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Login a user and return access token."""
        user = self.authenticate_user(email, password)
        if not user:
            return None
        
        # Update last login
        user.last_login = datetime.now()
        
        # Create access token
        access_token = self.create_access_token(
            data={"sub": user.email, "user_id": user.user_id, "role": user.role}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user.user_id,
                "email": user.email,
                "name": user.name,
                "role": user.role
            }
        }
    
    def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token."""
        payload = self.verify_token(token)
        if not payload:
            return None
        
        email = payload.get("sub")
        if not email:
            return None
        
        return self.users.get(email)
    
    def register_user(self, email: str, password: str, name: str, role: str = "lawyer") -> Optional[User]:
        """Register a new user."""
        if email in self.users:
            return None
        
        user = User(
            user_id=f"{role}-{secrets.token_hex(4)}",
            email=email,
            name=name,
            role=role,
            created_at=datetime.now()
        )
        
        self.users[email] = user
        return user

# Global auth instance
auth_system = AuthSystem() 