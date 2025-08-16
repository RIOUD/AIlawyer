#!/usr/bin/env python3
"""
Authentication Manager for Secure Offline Legal Assistant

Provides secure authentication and session management for the legal assistant platform.
Implements JWT-based authentication with secure session handling.
"""

import os
import jwt
import bcrypt
import secrets
import hashlib
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

from exceptions import AuthenticationError, AuthorizationError, SessionError
from logger import get_logger

logger = get_logger("auth_manager")


@dataclass
class User:
    """User data structure."""
    user_id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None


@dataclass
class Session:
    """Session data structure."""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool


class AuthManager:
    """
    Secure authentication manager for the legal assistant platform.
    
    Features:
    - JWT-based authentication
    - Secure password hashing with bcrypt
    - Session management with automatic expiration
    - Role-based access control
    - Brute force protection
    - Audit logging
    """
    
    def __init__(self, 
                 db_path: str = "./security/auth.db",
                 jwt_secret: Optional[str] = None,
                 jwt_expiry_hours: int = 24,
                 max_failed_attempts: int = 5,
                 lockout_duration_minutes: int = 15):
        """
        Initialize the authentication manager.
        
        Args:
            db_path: Path to authentication database
            jwt_secret: JWT secret key (if None, uses environment variable)
            jwt_expiry_hours: JWT token expiry time in hours
            max_failed_attempts: Maximum failed login attempts before lockout
            lockout_duration_minutes: Lockout duration in minutes
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # JWT configuration
        self.jwt_secret = jwt_secret or os.getenv('JWT_SECRET')
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable must be set")
        
        self.jwt_expiry_hours = jwt_expiry_hours
        self.max_failed_attempts = max_failed_attempts
        self.lockout_duration_minutes = lockout_duration_minutes
        
        # Initialize database
        self._init_database()
        
        # Create default admin user if no users exist
        self._create_default_admin()
        
        logger.info("Authentication manager initialized successfully")
    
    def _init_database(self):
        """Initialize the authentication database."""
        with sqlite3.connect(self.db_path) as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    failed_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP
                )
            """)
            
            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Audit log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS auth_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN DEFAULT TRUE,
                    details TEXT
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON auth_audit_log(timestamp)")
    
    def _create_default_admin(self):
        """Create default admin user if no users exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                # Create default admin user
                admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
                self.create_user(
                    username="admin",
                    email="admin@legalassistant.local",
                    password=admin_password,
                    role="admin"
                )
                logger.warning("Default admin user created with password 'admin123'")
                logger.warning("CHANGE THIS PASSWORD IMMEDIATELY in production!")
    
    def create_user(self, 
                   username: str, 
                   email: str, 
                   password: str, 
                   role: str = "user") -> str:
        """
        Create a new user account.
        
        Args:
            username: Username for the account
            email: Email address
            password: Plain text password
            role: User role (admin, user, readonly)
            
        Returns:
            User ID of the created user
            
        Raises:
            AuthenticationError: If user creation fails
        """
        try:
            # Validate input
            if not username or not email or not password:
                raise AuthenticationError("Username, email, and password are required")
            
            if len(password) < 8:
                raise AuthenticationError("Password must be at least 8 characters long")
            
            if role not in ["admin", "user", "readonly"]:
                raise AuthenticationError("Invalid role specified")
            
            # Generate user ID
            user_id = secrets.token_hex(16)
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO users (user_id, username, email, password_hash, role)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, username, email, password_hash.decode(), role))
                
                # Log the action
                self._log_auth_action(user_id, "USER_CREATED", True, f"Role: {role}")
                
                logger.info(f"User created successfully: {username}")
                return user_id
                
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise AuthenticationError("Username or email already exists")
            else:
                raise AuthenticationError(f"Database error: {e}")
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise AuthenticationError(f"Failed to create user: {e}")
    
    def authenticate(self, 
                    username: str, 
                    password: str, 
                    ip_address: str = None,
                    user_agent: str = None) -> Tuple[str, str]:
        """
        Authenticate a user and return JWT token.
        
        Args:
            username: Username
            password: Plain text password
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (user_id, jwt_token)
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Check if user is locked
            if self._is_user_locked(username):
                raise AuthenticationError("Account is temporarily locked due to failed attempts")
            
            # Get user from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT user_id, password_hash, role, is_active
                    FROM users WHERE username = ?
                """, (username,))
                
                result = cursor.fetchone()
                if not result:
                    self._record_failed_attempt(username, ip_address, user_agent)
                    raise AuthenticationError("Invalid username or password")
                
                user_id, password_hash, role, is_active = result
                
                if not is_active:
                    raise AuthenticationError("Account is deactivated")
                
                # Verify password
                if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode()):
                    self._record_failed_attempt(username, ip_address, user_agent)
                    raise AuthenticationError("Invalid username or password")
                
                # Reset failed attempts on successful login
                conn.execute("""
                    UPDATE users 
                    SET failed_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (user_id,))
                
                # Create session
                session_id = self._create_session(user_id, ip_address, user_agent)
                
                # Generate JWT token
                token = self._generate_jwt_token(user_id, username, role, session_id)
                
                # Log successful authentication
                self._log_auth_action(user_id, "LOGIN_SUCCESS", True, f"IP: {ip_address}")
                
                logger.info(f"User authenticated successfully: {username}")
                return user_id, token
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationError(f"Authentication failed: {e}")
    
    def _is_user_locked(self, username: str) -> bool:
        """Check if user account is locked."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT locked_until FROM users WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            if result and result[0]:
                locked_until = datetime.fromisoformat(result[0])
                if datetime.now(timezone.utc) < locked_until:
                    return True
                else:
                    # Clear expired lock
                    conn.execute("""
                        UPDATE users SET locked_until = NULL WHERE username = ?
                    """, (username,))
            
            return False
    
    def _record_failed_attempt(self, username: str, ip_address: str, user_agent: str):
        """Record a failed login attempt."""
        with sqlite3.connect(self.db_path) as conn:
            # Increment failed attempts
            conn.execute("""
                UPDATE users 
                SET failed_attempts = failed_attempts + 1
                WHERE username = ?
            """, (username,))
            
            # Check if account should be locked
            cursor = conn.execute("""
                SELECT failed_attempts FROM users WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            if result and result[0] >= self.max_failed_attempts:
                lockout_until = datetime.now(timezone.utc) + timedelta(minutes=self.lockout_duration_minutes)
                conn.execute("""
                    UPDATE users 
                    SET locked_until = ? 
                    WHERE username = ?
                """, (lockout_until.isoformat(), username))
                
                logger.warning(f"Account locked for {username} due to failed attempts")
            
            # Log failed attempt
            self._log_auth_action(None, "LOGIN_FAILED", False, f"Username: {username}, IP: {ip_address}")
    
    def _create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Create a new session for the user."""
        session_id = secrets.token_hex(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=self.jwt_expiry_hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions (session_id, user_id, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, user_id, expires_at.isoformat(), ip_address, user_agent))
        
        return session_id
    
    def _generate_jwt_token(self, user_id: str, username: str, role: str, session_id: str) -> str:
        """Generate a JWT token for the user."""
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'session_id': session_id,
            'exp': datetime.now(timezone.utc) + timedelta(hours=self.jwt_expiry_hours),
            'iat': datetime.now(timezone.utc)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token and return user information.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Dictionary with user information
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check if session is still valid
            if not self._is_session_valid(payload['session_id']):
                raise AuthenticationError("Session has expired")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise AuthenticationError(f"Token verification failed: {e}")
    
    def _is_session_valid(self, session_id: str) -> bool:
        """Check if session is still valid."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT expires_at, is_active 
                FROM sessions 
                WHERE session_id = ?
            """, (session_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            expires_at, is_active = result
            if not is_active:
                return False
            
            expires_at_dt = datetime.fromisoformat(expires_at)
            return datetime.now(timezone.utc) < expires_at_dt
    
    def logout(self, token: str):
        """Logout user by invalidating session."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            session_id = payload['session_id']
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE sessions SET is_active = FALSE WHERE session_id = ?
                """, (session_id,))
            
            self._log_auth_action(payload['user_id'], "LOGOUT", True)
            logger.info(f"User logged out: {payload['username']}")
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
    
    def _log_auth_action(self, user_id: Optional[str], action: str, success: bool, details: str = ""):
        """Log authentication actions for audit purposes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO auth_audit_log (user_id, action, success, details)
                    VALUES (?, ?, ?, ?)
                """, (user_id, action, success, details))
        except Exception as e:
            logger.error(f"Failed to log auth action: {e}")
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user information by user ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT user_id, username, email, role, is_active, created_at, last_login
                FROM users WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                return User(
                    user_id=result[0],
                    username=result[1],
                    email=result[2],
                    role=result[3],
                    is_active=bool(result[4]),
                    created_at=datetime.fromisoformat(result[5]),
                    last_login=datetime.fromisoformat(result[6]) if result[6] else None
                )
            return None
    
    def change_password(self, user_id: str, current_password: str, new_password: str):
        """Change user password."""
        try:
            # Verify current password
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT password_hash FROM users WHERE user_id = ?
                """, (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    raise AuthenticationError("User not found")
                
                if not bcrypt.checkpw(current_password.encode('utf-8'), result[0].encode()):
                    raise AuthenticationError("Current password is incorrect")
                
                # Hash new password
                new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                
                # Update password
                conn.execute("""
                    UPDATE users SET password_hash = ? WHERE user_id = ?
                """, (new_password_hash.decode(), user_id))
                
                self._log_auth_action(user_id, "PASSWORD_CHANGED", True)
                logger.info(f"Password changed for user: {user_id}")
                
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Password change error: {e}")
            raise AuthenticationError(f"Failed to change password: {e}")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE sessions 
                    SET is_active = FALSE 
                    WHERE expires_at < CURRENT_TIMESTAMP
                """)
                
                deleted_count = conn.total_changes
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired sessions")
                    
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
    
    def get_audit_log(self, limit: int = 100) -> list:
        """Get recent audit log entries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, user_id, action, ip_address, success, details
                FROM auth_audit_log
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return [
                {
                    'timestamp': row[0],
                    'user_id': row[1],
                    'action': row[2],
                    'ip_address': row[3],
                    'success': bool(row[4]),
                    'details': row[5]
                }
                for row in cursor.fetchall()
            ] 