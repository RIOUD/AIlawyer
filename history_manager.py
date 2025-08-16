#!/usr/bin/env python3
"""
History Manager for Secure Offline Legal Assistant

Provides high-level interface for managing query history, sessions,
and export functionality.
"""

import os
import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from database import LegalAssistantDB
from export_utils import ConversationExporter


class HistoryManager:
    """
    Manages query history, sessions, and export functionality.
    """
    
    def __init__(self, db_path: str = "./legal_assistant.db", 
                 export_dir: str = "./exports"):
        """
        Initialize the history manager.
        
        Args:
            db_path: Path to the SQLite database
            export_dir: Directory for exported PDFs
        """
        self.db = LegalAssistantDB(db_path)
        self.exporter = ConversationExporter()
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
        
        # Current session tracking
        self.current_session_id = None
        self.session_start_time = None
    
    def start_session(self, filters: Optional[Dict] = None) -> str:
        """
        Start a new session.
        
        Args:
            filters: Optional filters for the session
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())[:8]  # Short session ID
        self.current_session_id = session_id
        self.session_start_time = time.time()
        
        success = self.db.create_session(session_id, filters)
        if success:
            print(f"✅ Started new session: {session_id}")
        else:
            print(f"⚠️  Session {session_id} already exists")
        
        return session_id
    
    def end_session(self) -> bool:
        """
        End the current session.
        
        Returns:
            True if session ended successfully
        """
        if not self.current_session_id:
            return False
        
        success = self.db.end_session(self.current_session_id)
        if success:
            print(f"✅ Ended session: {self.current_session_id}")
            self.current_session_id = None
            self.session_start_time = None
        
        return success
    
    def save_query(self, question: str, answer: str, sources: List[Dict], 
                   filters: Optional[Dict] = None, processing_time: Optional[float] = None) -> bool:
        """
        Save a query to the current session.
        
        Args:
            question: User's question
            answer: AI-generated answer
            sources: List of source documents
            filters: Filters applied to the query
            processing_time: Time taken to process the query
            
        Returns:
            True if query saved successfully
        """
        if not self.current_session_id:
            print("⚠️  No active session. Starting new session...")
            self.start_session()
        
        success = self.db.save_query(
            self.current_session_id, question, answer, sources, 
            filters, processing_time
        )
        
        if success:
            print(f"💾 Query saved to session: {self.current_session_id}")
        
        return success
    
    def search_history(self, search_term: str, session_id: Optional[str] = None, 
                      limit: Optional[int] = None) -> List[Dict]:
        """
        Search through query history.
        
        Args:
            search_term: Term to search for
            session_id: Optional session filter
            limit: Maximum number of results
            
        Returns:
            List of matching queries
        """
        results = self.db.search_queries(search_term, session_id, limit)
        print(f"🔍 Found {len(results)} matching queries for '{search_term}'")
        return results
    
    def get_session_history(self, session_id: Optional[str] = None, 
                           limit: Optional[int] = None) -> List[Dict]:
        """
        Get query history for a session.
        
        Args:
            session_id: Session ID (uses current session if None)
            limit: Maximum number of queries to return
            
        Returns:
            List of queries
        """
        if not session_id:
            session_id = self.current_session_id
        
        if not session_id:
            print("⚠️  No session specified")
            return []
        
        queries = self.db.get_session_queries(session_id, limit)
        print(f"📋 Retrieved {len(queries)} queries from session: {session_id}")
        return queries
    
    def list_sessions(self, limit: Optional[int] = None) -> List[Dict]:
        """
        List all sessions with summary information.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of session summaries
        """
        sessions = self.db.get_all_sessions(limit)
        print(f"📊 Found {len(sessions)} sessions")
        return sessions
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall usage statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = self.db.get_query_statistics()
        return stats
    
    def export_session_to_pdf(self, session_id: Optional[str] = None, 
                             output_path: Optional[str] = None) -> Optional[str]:
        """
        Export a session to PDF.
        
        Args:
            session_id: Session ID (uses current session if None)
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path to exported PDF file, or None if failed
        """
        if not session_id:
            session_id = self.current_session_id
        
        if not session_id:
            print("⚠️  No session specified")
            return None
        
        # Get session data
        sessions = self.db.get_all_sessions()
        session_data = next((s for s in sessions if s['session_id'] == session_id), None)
        
        if not session_data:
            print(f"❌ Session {session_id} not found")
            return None
        
        # Get queries
        queries = self.db.get_session_queries(session_id)
        
        if not queries:
            print(f"⚠️  No queries found for session {session_id}")
            return None
        
        # Generate output path
        if not output_path:
            filename = self.exporter.get_export_filename(session_id=session_id, export_type="session")
            output_path = self.export_dir / filename
        
        # Export to PDF
        success = self.exporter.export_session_to_pdf(session_data, queries, str(output_path))
        
        if success:
            print(f"📄 Session exported to: {output_path}")
            return str(output_path)
        else:
            print(f"❌ Failed to export session {session_id}")
            return None
    
    def export_search_results_to_pdf(self, search_term: str, results: List[Dict], 
                                    output_path: Optional[str] = None) -> Optional[str]:
        """
        Export search results to PDF.
        
        Args:
            search_term: The search term used
            results: List of matching queries
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path to exported PDF file, or None if failed
        """
        if not results:
            print("⚠️  No search results to export")
            return None
        
        # Generate output path
        if not output_path:
            filename = self.exporter.get_export_filename(search_term=search_term, export_type="search")
            output_path = self.export_dir / filename
        
        # Export to PDF
        success = self.exporter.export_search_results_to_pdf(search_term, results, str(output_path))
        
        if success:
            print(f"📄 Search results exported to: {output_path}")
            return str(output_path)
        else:
            print(f"❌ Failed to export search results")
            return None
    
    def export_statistics_to_pdf(self, output_path: Optional[str] = None) -> Optional[str]:
        """
        Export usage statistics to PDF.
        
        Args:
            output_path: Output file path (auto-generated if None)
            
        Returns:
            Path to exported PDF file, or None if failed
        """
        # Get statistics
        stats = self.get_statistics()
        
        if not stats:
            print("⚠️  No statistics available")
            return None
        
        # Generate output path
        if not output_path:
            filename = self.exporter.get_export_filename(export_type="stats")
            output_path = self.export_dir / filename
        
        # Export to PDF
        success = self.exporter.export_statistics_to_pdf(stats, str(output_path))
        
        if success:
            print(f"📄 Statistics exported to: {output_path}")
            return str(output_path)
        else:
            print(f"❌ Failed to export statistics")
            return None
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its queries.
        
        Args:
            session_id: Session ID to delete
            
        Returns:
            True if session deleted successfully
        """
        success = self.db.delete_session(session_id)
        
        if success:
            print(f"🗑️  Deleted session: {session_id}")
        else:
            print(f"❌ Failed to delete session: {session_id}")
        
        return success
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up sessions older than specified days.
        
        Args:
            days_old: Number of days to keep sessions
            
        Returns:
            Number of sessions deleted
        """
        deleted_count = self.db.cleanup_old_sessions(days_old)
        
        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} old sessions (older than {days_old} days)")
        else:
            print(f"✨ No old sessions to clean up")
        
        return deleted_count
    
    def display_session_summary(self, session_id: Optional[str] = None):
        """
        Display a summary of a session.
        
        Args:
            session_id: Session ID (uses current session if None)
        """
        if not session_id:
            session_id = self.current_session_id
        
        if not session_id:
            print("⚠️  No session specified")
            return
        
        # Get session data
        sessions = self.db.get_all_sessions()
        session_data = next((s for s in sessions if s['session_id'] == session_id), None)
        
        if not session_data:
            print(f"❌ Session {session_id} not found")
            return
        
        print(f"\n📊 Session Summary: {session_id}")
        print("=" * 50)
        print(f"Start Time: {session_data.get('start_time', 'Unknown')}")
        print(f"End Time: {session_data.get('end_time', 'Active')}")
        print(f"Total Queries: {session_data.get('total_queries', 0)}")
        print(f"Status: {session_data.get('status', 'Unknown')}")
        
        # Show filters if available
        filters_used = session_data.get('filters_used')
        if filters_used:
            try:
                import json
                filters_dict = json.loads(filters_used)
                filter_str = ", ".join([f"{k}: {v}" for k, v in filters_dict.items() if v])
                print(f"Filters: {filter_str}")
            except:
                print(f"Filters: {filters_used}")
        
        print("=" * 50)
    
    def display_statistics(self):
        """Display usage statistics."""
        stats = self.get_statistics()
        
        if not stats:
            print("⚠️  No statistics available")
            return
        
        print(f"\n📈 Usage Statistics")
        print("=" * 30)
        print(f"Total Queries: {stats.get('total_queries', 0)}")
        print(f"Total Sessions: {stats.get('total_sessions', 0)}")
        print(f"Avg Queries per Session: {stats.get('avg_queries_per_session', 0)}")
        
        # Show common filters
        common_filters = stats.get('common_filters', [])
        if common_filters:
            print(f"\nMost Common Filters:")
            for filter_info, count in common_filters[:3]:
                try:
                    import json
                    filter_dict = json.loads(filter_info) if filter_info else {}
                    filter_str = ", ".join([f"{k}: {v}" for k, v in filter_dict.items() if v])
                    print(f"  - {filter_str}: {count} times")
                except:
                    print(f"  - {filter_info}: {count} times")
        
        print("=" * 30) 