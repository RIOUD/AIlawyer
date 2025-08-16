#!/usr/bin/env python3
"""
User Feedback Collection System for LawyerAgent

Collects structured feedback from different user types during testing phases.
Maintains privacy and security while gathering actionable insights.
"""

import os
import json
import sqlite3
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import requests
from cryptography.fernet import Fernet
import bcrypt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserType(Enum):
    """Types of users for feedback collection."""
    SOLO_LAWYER = "solo_lawyer"
    SMALL_FIRM = "small_firm"
    LARGE_FIRM = "large_firm"
    LEGAL_RESEARCHER = "legal_researcher"
    LAW_STUDENT = "law_student"
    PARALEGAL = "paralegal"
    LEGAL_TECH = "legal_tech"


class FeedbackCategory(Enum):
    """Categories of feedback."""
    USABILITY = "usability"
    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    SECURITY = "security"
    FEATURES = "features"
    INTEGRATION = "integration"
    SUPPORT = "support"


class SentimentScore(Enum):
    """Sentiment scores for feedback."""
    VERY_NEGATIVE = 1
    NEGATIVE = 2
    NEUTRAL = 3
    POSITIVE = 4
    VERY_POSITIVE = 5


@dataclass
class UserProfile:
    """User profile for feedback collection."""
    user_id: str
    user_type: UserType
    experience_years: int
    practice_areas: List[str]
    jurisdiction: str
    language_preference: str
    created_at: datetime
    last_active: datetime
    feedback_count: int = 0
    session_count: int = 0


@dataclass
class FeedbackEntry:
    """Individual feedback entry."""
    feedback_id: str
    user_id: str
    category: FeedbackCategory
    sentiment: SentimentScore
    title: str
    description: str
    feature_used: str
    session_id: str
    timestamp: datetime
    metadata: Dict[str, Any]
    is_anonymous: bool = False


@dataclass
class SessionData:
    """Session data for analytics."""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    queries_count: int
    documents_accessed: List[str]
    features_used: List[str]
    errors_encountered: List[str]
    performance_metrics: Dict[str, float]


class UserFeedbackSystem:
    """
    Comprehensive user feedback collection system.
    """
    
    def __init__(self, db_path: str = "user_feedback.db", encryption_key: Optional[str] = None):
        """
        Initialize the feedback system.
        
        Args:
            db_path: Path to the feedback database
            encryption_key: Encryption key for sensitive data
        """
        self.db_path = db_path
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Initialize database
        self._init_database()
        
        # Load configuration
        self.config = self._load_config()
        
        logger.info("User feedback system initialized")
    
    def _init_database(self):
        """Initialize the feedback database."""
        with sqlite3.connect(self.db_path) as conn:
            # Users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    user_type TEXT NOT NULL,
                    experience_years INTEGER,
                    practice_areas TEXT,
                    jurisdiction TEXT,
                    language_preference TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    feedback_count INTEGER DEFAULT 0,
                    session_count INTEGER DEFAULT 0,
                    encrypted_data TEXT
                )
            """)
            
            # Feedback table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    category TEXT NOT NULL,
                    sentiment INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    feature_used TEXT,
                    session_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    is_anonymous BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    queries_count INTEGER DEFAULT 0,
                    documents_accessed TEXT,
                    features_used TEXT,
                    errors_encountered TEXT,
                    performance_metrics TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)
            
            # Analytics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    user_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load feedback system configuration."""
        config_path = Path("feedback_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "feedback_prompts": {
                "usability": [
                    "How easy was it to find the information you needed?",
                    "How intuitive was the interface?",
                    "Were there any confusing elements?"
                ],
                "performance": [
                    "How fast did the system respond to your queries?",
                    "Were there any delays or timeouts?",
                    "How would you rate the overall performance?"
                ],
                "accuracy": [
                    "How accurate were the legal answers provided?",
                    "Were the source citations helpful?",
                    "Did you find any incorrect information?"
                ],
                "security": [
                    "How confident are you in the security of your data?",
                    "Were there any security concerns?",
                    "How important is offline operation to you?"
                ]
            },
            "feedback_thresholds": {
                "min_feedback_length": 10,
                "max_feedback_length": 1000,
                "daily_feedback_limit": 10,
                "session_feedback_limit": 3
            },
            "privacy_settings": {
                "anonymize_by_default": True,
                "retention_days": 365,
                "encrypt_sensitive_data": True,
                "allow_data_export": False
            }
        }
        
        # Save default configuration
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def create_user_profile(self, 
                           user_type: UserType,
                           experience_years: int,
                           practice_areas: List[str],
                           jurisdiction: str,
                           language_preference: str = "dutch") -> str:
        """
        Create a new user profile.
        
        Args:
            user_type: Type of legal professional
            experience_years: Years of legal experience
            practice_areas: List of practice areas
            jurisdiction: Legal jurisdiction
            language_preference: Preferred language
            
        Returns:
            User ID for the created profile
        """
        user_id = str(uuid.uuid4())
        
        # Encrypt sensitive data
        sensitive_data = {
            "practice_areas": practice_areas,
            "experience_years": experience_years
        }
        encrypted_data = self.cipher.encrypt(json.dumps(sensitive_data).encode())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO users (
                    user_id, user_type, experience_years, practice_areas,
                    jurisdiction, language_preference, encrypted_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, user_type.value, experience_years,
                json.dumps(practice_areas), jurisdiction,
                language_preference, encrypted_data
            ))
        
        logger.info(f"Created user profile: {user_id} ({user_type.value})")
        return user_id
    
    def submit_feedback(self,
                       user_id: str,
                       category: FeedbackCategory,
                       sentiment: SentimentScore,
                       title: str,
                       description: str,
                       feature_used: str = "",
                       session_id: str = "",
                       metadata: Optional[Dict[str, Any]] = None,
                       is_anonymous: bool = False) -> str:
        """
        Submit user feedback.
        
        Args:
            user_id: User ID
            category: Feedback category
            sentiment: Sentiment score
            title: Feedback title
            description: Detailed feedback
            feature_used: Feature being feedbacked
            session_id: Session ID
            metadata: Additional metadata
            is_anonymous: Whether to anonymize the feedback
            
        Returns:
            Feedback ID
        """
        feedback_id = str(uuid.uuid4())
        
        # Validate feedback
        if len(description) < self.config["feedback_thresholds"]["min_feedback_length"]:
            raise ValueError("Feedback description too short")
        
        if len(description) > self.config["feedback_thresholds"]["max_feedback_length"]:
            raise ValueError("Feedback description too long")
        
        # Check daily limit
        if not self._check_feedback_limit(user_id):
            raise ValueError("Daily feedback limit exceeded")
        
        with sqlite3.connect(self.db_path) as conn:
            # Insert feedback
            conn.execute("""
                INSERT INTO feedback (
                    feedback_id, user_id, category, sentiment, title,
                    description, feature_used, session_id, metadata, is_anonymous
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback_id, user_id, category.value, sentiment.value,
                title, description, feature_used, session_id,
                json.dumps(metadata or {}), is_anonymous
            ))
            
            # Update user feedback count
            conn.execute("""
                UPDATE users SET feedback_count = feedback_count + 1,
                last_active = CURRENT_TIMESTAMP WHERE user_id = ?
            """, (user_id,))
        
        logger.info(f"Feedback submitted: {feedback_id} by {user_id}")
        return feedback_id
    
    def start_session(self, user_id: str) -> str:
        """
        Start a new user session.
        
        Args:
            user_id: User ID
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions (
                    session_id, user_id, start_time
                ) VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (session_id, user_id))
            
            # Update user session count
            conn.execute("""
                UPDATE users SET session_count = session_count + 1,
                last_active = CURRENT_TIMESTAMP WHERE user_id = ?
            """, (user_id,))
        
        logger.info(f"Session started: {session_id} for user {user_id}")
        return session_id
    
    def end_session(self, session_id: str, session_data: SessionData):
        """
        End a user session and record analytics.
        
        Args:
            session_id: Session ID
            session_data: Session data to record
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE sessions SET
                    end_time = CURRENT_TIMESTAMP,
                    queries_count = ?,
                    documents_accessed = ?,
                    features_used = ?,
                    errors_encountered = ?,
                    performance_metrics = ?
                WHERE session_id = ?
            """, (
                session_data.queries_count,
                json.dumps(session_data.documents_accessed),
                json.dumps(session_data.features_used),
                json.dumps(session_data.errors_encountered),
                json.dumps(session_data.performance_metrics),
                session_id
            ))
        
        logger.info(f"Session ended: {session_id}")
    
    def get_feedback_analytics(self, 
                              user_type: Optional[UserType] = None,
                              date_range: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Get feedback analytics.
        
        Args:
            user_type: Filter by user type
            date_range: Date range tuple (start_date, end_date)
            
        Returns:
            Analytics data
        """
        with sqlite3.connect(self.db_path) as conn:
            # Base query
            query = """
                SELECT f.category, f.sentiment, u.user_type, f.timestamp
                FROM feedback f
                JOIN users u ON f.user_id = u.user_id
                WHERE 1=1
            """
            params = []
            
            if user_type:
                query += " AND u.user_type = ?"
                params.append(user_type.value)
            
            if date_range:
                query += " AND f.timestamp BETWEEN ? AND ?"
                params.extend(date_range)
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        
        # Process analytics
        analytics = {
            "total_feedback": len(rows),
            "sentiment_distribution": {},
            "category_distribution": {},
            "user_type_distribution": {},
            "average_sentiment": 0.0
        }
        
        if rows:
            sentiments = [row[1] for row in rows]
            categories = [row[0] for row in rows]
            user_types = [row[2] for row in rows]
            
            analytics["sentiment_distribution"] = self._count_distribution(sentiments)
            analytics["category_distribution"] = self._count_distribution(categories)
            analytics["user_type_distribution"] = self._count_distribution(user_types)
            analytics["average_sentiment"] = sum(sentiments) / len(sentiments)
        
        return analytics
    
    def get_user_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of recommendations
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get user profile
            cursor = conn.execute("""
                SELECT user_type, experience_years, practice_areas
                FROM users WHERE user_id = ?
            """, (user_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return []
            
            user_type, experience_years, practice_areas = user_data
            practice_areas = json.loads(practice_areas) if practice_areas else []
            
            # Get feedback from similar users
            cursor = conn.execute("""
                SELECT f.title, f.description, f.sentiment, f.category
                FROM feedback f
                JOIN users u ON f.user_id = u.user_id
                WHERE u.user_type = ? AND f.sentiment >= 4
                ORDER BY f.timestamp DESC
                LIMIT 10
            """, (user_type,))
            
            similar_feedback = cursor.fetchall()
        
        # Generate recommendations
        recommendations = []
        for title, description, sentiment, category in similar_feedback:
            recommendations.append({
                "type": "feature_recommendation",
                "title": title,
                "description": description,
                "category": category,
                "confidence": sentiment / 5.0
            })
        
        return recommendations
    
    def _check_feedback_limit(self, user_id: str) -> bool:
        """Check if user has exceeded daily feedback limit."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM feedback
                WHERE user_id = ? AND DATE(timestamp) = DATE('now')
            """, (user_id,))
            count = cursor.fetchone()[0]
        
        return count < self.config["feedback_thresholds"]["daily_feedback_limit"]
    
    def _count_distribution(self, items: List[Any]) -> Dict[str, int]:
        """Count distribution of items."""
        distribution = {}
        for item in items:
            distribution[str(item)] = distribution.get(str(item), 0) + 1
        return distribution
    
    def export_feedback_report(self, 
                              format: str = "json",
                              include_sensitive: bool = False) -> str:
        """
        Export feedback report.
        
        Args:
            format: Export format (json, csv, pdf)
            include_sensitive: Whether to include sensitive data
            
        Returns:
            Path to exported report
        """
        # Implementation for report export
        # This would generate comprehensive reports for analysis
        pass


def main():
    """Main function for testing the feedback system."""
    # Initialize feedback system
    feedback_system = UserFeedbackSystem()
    
    # Create test user profiles
    user_ids = []
    
    # Solo lawyer
    solo_lawyer_id = feedback_system.create_user_profile(
        UserType.SOLO_LAWYER,
        experience_years=8,
        practice_areas=["family_law", "civil_litigation"],
        jurisdiction="vlaams",
        language_preference="dutch"
    )
    user_ids.append(solo_lawyer_id)
    
    # Small firm lawyer
    small_firm_id = feedback_system.create_user_profile(
        UserType.SMALL_FIRM,
        experience_years=12,
        practice_areas=["corporate_law", "employment_law"],
        jurisdiction="federaal",
        language_preference="french"
    )
    user_ids.append(small_firm_id)
    
    # Submit test feedback
    for user_id in user_ids:
        session_id = feedback_system.start_session(user_id)
        
        # Submit usability feedback
        feedback_system.submit_feedback(
            user_id=user_id,
            category=FeedbackCategory.USABILITY,
            sentiment=SentimentScore.POSITIVE,
            title="Easy to use interface",
            description="The interface is intuitive and easy to navigate. I found the search functionality particularly helpful.",
            feature_used="search",
            session_id=session_id
        )
        
        # Submit performance feedback
        feedback_system.submit_feedback(
            user_id=user_id,
            category=FeedbackCategory.PERFORMANCE,
            sentiment=SentimentScore.NEUTRAL,
            title="Good response times",
            description="Response times are generally good, but could be faster for complex queries.",
            feature_used="query_processing",
            session_id=session_id
        )
        
        # End session
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            queries_count=5,
            documents_accessed=["contract_1.pdf", "case_law_2.pdf"],
            features_used=["search", "filter", "export"],
            errors_encountered=[],
            performance_metrics={"avg_response_time": 2.5, "success_rate": 0.95}
        )
        feedback_system.end_session(session_id, session_data)
    
    # Get analytics
    analytics = feedback_system.get_feedback_analytics()
    print("Feedback Analytics:")
    print(json.dumps(analytics, indent=2, default=str))
    
    # Get recommendations for first user
    recommendations = feedback_system.get_user_recommendations(user_ids[0])
    print(f"\nRecommendations for user {user_ids[0]}:")
    print(json.dumps(recommendations, indent=2, default=str))


if __name__ == "__main__":
    main() 