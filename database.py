#!/usr/bin/env python3
"""
Database module for Secure Offline Legal Assistant

Handles SQLite database operations for query history, session management,
and persistent storage of conversations.
"""

import sqlite3
import json
import os
import threading
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from contextlib import contextmanager
from collections import defaultdict

from exceptions import DatabaseError, ConnectionError, QueryError

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Manages database connections with connection pooling."""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connection_pool = []
        self._lock = threading.Lock()
    
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        conn = None
        try:
            with self._lock:
                if self._connection_pool:
                    conn = self._connection_pool.pop()
                else:
                    conn = sqlite3.connect(
                        self.db_path,
                        check_same_thread=False,
                        timeout=30.0
                    )
                    conn.row_factory = sqlite3.Row
            
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise ConnectionError(f"Failed to connect to database: {e}", db_path=self.db_path)
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass


class LegalAssistantDB:
    """
    Enhanced SQLite database manager for the Legal Assistant application.
    
    Handles query history, session management, and data persistence with
    connection pooling and proper error handling.
    """
    
    def __init__(self, db_path: str = "./legal_assistant.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection_manager = DatabaseConnectionManager(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with self.connection_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP,
                        total_queries INTEGER DEFAULT 0,
                        filters_used TEXT,
                        status TEXT DEFAULT 'active'
                    )
                """)
                
                # Create queries table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS queries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        question TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        sources TEXT,
                        filters_applied TEXT,
                        query_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        processing_time REAL,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                """)
                
                # Create search index for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_queries_session 
                    ON queries (session_id)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_queries_time 
                    ON queries (query_time)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_queries_question 
                    ON queries (question)
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise DatabaseError(f"Failed to initialize database: {e}")
    
    def create_session(self, session_id: str, filters: Optional[Dict] = None) -> bool:
        """
        Create a new session with proper error handling.
        
        Args:
            session_id: Unique session identifier
            filters: Optional filters applied during session
            
        Returns:
            True if session created successfully
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self.connection_manager.get_connection() as conn:
                cursor = conn.cursor()
                filters_json = json.dumps(filters) if filters else None
                
                cursor.execute("""
                    INSERT INTO sessions (session_id, filters_used)
                    VALUES (?, ?)
                """, (session_id, filters_json))
                
                conn.commit()
                logger.info(f"Created session: {session_id}")
                return True
                
        except sqlite3.IntegrityError as e:
            logger.warning(f"Session already exists: {session_id}")
            return False
        except sqlite3.Error as e:
            logger.error(f"Database error creating session: {e}")
            raise DatabaseError(f"Failed to create session: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating session: {e}")
            raise DatabaseError(f"Unexpected error: {e}")
    
    def get_session_queries(self, session_id: str, include_metadata: bool = False) -> List[Dict[str, Any]]:
        """
        Get all queries for a session with optional metadata.
        
        Args:
            session_id: Session identifier
            include_metadata: Whether to include session metadata
            
        Returns:
            List of query dictionaries
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self.connection_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Use a single query with JOIN if metadata is needed
                if include_metadata:
                    cursor.execute("""
                        SELECT q.id, q.question, q.answer, q.sources, q.filters_applied,
                               q.query_time, q.processing_time, s.filters_used
                        FROM queries q
                        LEFT JOIN sessions s ON q.session_id = s.session_id
                        WHERE q.session_id = ?
                        ORDER BY q.query_time DESC
                    """, (session_id,))
                else:
                    cursor.execute("""
                        SELECT id, question, answer, sources, filters_applied, 
                               query_time, processing_time
                        FROM queries 
                        WHERE session_id = ?
                        ORDER BY query_time DESC
                    """, (session_id,))
                
                return [self._row_to_dict(row, cursor.description) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logger.error(f"Database error retrieving queries: {e}")
            raise DatabaseError(f"Failed to retrieve queries: {e}")
    
    def get_session_queries_batch(self, session_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get queries for multiple sessions in a single operation.
        
        Args:
            session_ids: List of session IDs
            
        Returns:
            Dictionary mapping session IDs to their queries
            
        Raises:
            DatabaseError: If database operation fails
        """
        if not session_ids:
            return {}
        
        try:
            with self.connection_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Use IN clause for batch retrieval
                placeholders = ','.join('?' * len(session_ids))
                cursor.execute(f"""
                    SELECT session_id, id, question, answer, sources, 
                           filters_applied, query_time, processing_time
                    FROM queries 
                    WHERE session_id IN ({placeholders})
                    ORDER BY session_id, query_time DESC
                """, session_ids)
                
                results = defaultdict(list)
                for row in cursor.fetchall():
                    session_id = row['session_id']
                    results[session_id].append({
                        'id': row['id'],
                        'question': row['question'],
                        'answer': row['answer'],
                        'sources': json.loads(row['sources']) if row['sources'] else None,
                        'filters_applied': json.loads(row['filters_applied']) if row['filters_applied'] else None,
                        'query_time': row['query_time'],
                        'processing_time': row['processing_time']
                    })
                
                return dict(results)
                
        except sqlite3.Error as e:
            logger.error(f"Database error retrieving batch queries: {e}")
            raise DatabaseError(f"Failed to retrieve queries: {e}")
    
    def _row_to_dict(self, row: tuple, description: tuple) -> Dict[str, Any]:
        """Convert database row to dictionary efficiently."""
        return {
            desc[0]: (json.loads(val) if val and desc[0] in ['sources', 'filters_applied', 'filters_used'] else val)
            for desc, val in zip(description, row)
        }
    
    def add_query(self, session_id: str, question: str, answer: str, 
                  sources: Optional[List[Dict]] = None, 
                  filters_applied: Optional[Dict] = None,
                  processing_time: Optional[float] = None) -> bool:
        """
        Add a new query to the database.
        
        Args:
            session_id: Session identifier
            question: User question
            answer: AI response
            sources: Source documents used
            filters_applied: Filters applied to the query
            processing_time: Time taken to process the query
            
        Returns:
            True if query added successfully
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self.connection_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO queries (session_id, question, answer, sources, 
                                       filters_applied, processing_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session_id, question, answer,
                    json.dumps(sources) if sources else None,
                    json.dumps(filters_applied) if filters_applied else None,
                    processing_time
                ))
                
                # Update session query count
                cursor.execute("""
                    UPDATE sessions 
                    SET total_queries = total_queries + 1
                    WHERE session_id = ?
                """, (session_id,))
                
                conn.commit()
                logger.info(f"Added query to session: {session_id}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Database error adding query: {e}")
            raise DatabaseError(f"Failed to add query: {e}")
    
    def end_session(self, session_id: str) -> bool:
        """
        End a session by updating its status and end time.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session ended successfully
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self.connection_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE sessions 
                    SET end_time = CURRENT_TIMESTAMP, status = 'ended'
                    WHERE session_id = ?
                """, (session_id,))
                
                conn.commit()
                logger.info(f"Ended session: {session_id}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Database error ending session: {e}")
            raise DatabaseError(f"Failed to end session: {e}")
    
    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session statistics dictionary or None if session not found
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self.connection_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT s.session_id, s.start_time, s.end_time, s.total_queries,
                           s.filters_used, s.status,
                           AVG(q.processing_time) as avg_processing_time,
                           COUNT(q.id) as total_queries
                    FROM sessions s
                    LEFT JOIN queries q ON s.session_id = q.session_id
                    WHERE s.session_id = ?
                    GROUP BY s.session_id
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'session_id': row['session_id'],
                        'start_time': row['start_time'],
                        'end_time': row['end_time'],
                        'total_queries': row['total_queries'],
                        'filters_used': json.loads(row['filters_used']) if row['filters_used'] else None,
                        'status': row['status'],
                        'avg_processing_time': row['avg_processing_time']
                    }
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Database error getting session stats: {e}")
            raise DatabaseError(f"Failed to get session stats: {e}")
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up old sessions and their queries.
        
        Args:
            days_old: Number of days after which sessions are considered old
            
        Returns:
            Number of sessions cleaned up
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            with self.connection_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get old session IDs
                cursor.execute("""
                    SELECT session_id FROM sessions 
                    WHERE start_time < datetime('now', '-{} days')
                    AND status = 'ended'
                """.format(days_old))
                
                old_session_ids = [row['session_id'] for row in cursor.fetchall()]
                
                if not old_session_ids:
                    return 0
                
                # Delete queries for old sessions
                placeholders = ','.join('?' * len(old_session_ids))
                cursor.execute(f"""
                    DELETE FROM queries 
                    WHERE session_id IN ({placeholders})
                """, old_session_ids)
                
                # Delete old sessions
                cursor.execute(f"""
                    DELETE FROM sessions 
                    WHERE session_id IN ({placeholders})
                """, old_session_ids)
                
                conn.commit()
                logger.info(f"Cleaned up {len(old_session_ids)} old sessions")
                return len(old_session_ids)
                
        except sqlite3.Error as e:
            logger.error(f"Database error cleaning up old sessions: {e}")
            raise DatabaseError(f"Failed to cleanup old sessions: {e}") 