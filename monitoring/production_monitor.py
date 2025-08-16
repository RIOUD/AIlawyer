#!/usr/bin/env python3
"""
Production Monitoring System for LawyerAgent

Real-time monitoring of system health, performance, user activity, and security events
for production deployment.
"""

import os
import json
import time
import psutil
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import threading
from collections import defaultdict, deque
import asyncio
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics to monitor."""
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE = "performance"
    USER_ACTIVITY = "user_activity"
    SECURITY = "security"
    BUSINESS = "business"


@dataclass
class SystemMetrics:
    """System health and performance metrics."""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    ollama_status: str
    vector_db_status: str
    web_interface_status: str


@dataclass
class PerformanceMetrics:
    """Application performance metrics."""
    timestamp: datetime
    query_response_time: float
    document_processing_time: float
    concurrent_users: int
    queries_per_minute: float
    error_rate: float
    cache_hit_rate: float


@dataclass
class UserActivityMetrics:
    """User activity and engagement metrics."""
    timestamp: datetime
    active_sessions: int
    total_queries: int
    unique_users: int
    session_duration: float
    feature_usage: Dict[str, int]
    user_satisfaction: float


@dataclass
class SecurityMetrics:
    """Security and compliance metrics."""
    timestamp: datetime
    failed_login_attempts: int
    suspicious_activities: int
    encrypted_documents: int
    audit_events: int
    security_alerts: List[str]
    compliance_status: str


class ProductionMonitor:
    """
    Real-time production monitoring system.
    """
    
    def __init__(self, config_path: str = "monitoring_config.json"):
        """
        Initialize the production monitor.
        
        Args:
            config_path: Path to monitoring configuration
        """
        self.config = self._load_config(config_path)
        self.metrics_history = {
            MetricType.SYSTEM_HEALTH: deque(maxlen=1000),
            MetricType.PERFORMANCE: deque(maxlen=1000),
            MetricType.USER_ACTIVITY: deque(maxlen=1000),
            MetricType.SECURITY: deque(maxlen=1000),
            MetricType.BUSINESS: deque(maxlen=1000)
        }
        self.alerts = []
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Initialize database
        self._init_monitoring_db()
        
        logger.info("Production monitor initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load monitoring configuration."""
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        default_config = {
            "monitoring_interval": 30,  # seconds
            "alert_thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "response_time": 60.0,
                "error_rate": 5.0,
                "failed_logins": 10
            },
            "endpoints": {
                "lawyeragent": "http://localhost:5000",
                "ollama": "http://localhost:11434",
                "grafana": "http://localhost:3000",
                "prometheus": "http://localhost:9090"
            },
            "retention_days": 30,
            "alert_channels": ["console", "email", "webhook"]
        }
        
        # Save default configuration
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _init_monitoring_db(self):
        """Initialize monitoring database."""
        db_path = "monitoring.db"
        with sqlite3.connect(db_path) as conn:
            # System metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_io TEXT,
                    active_connections INTEGER,
                    ollama_status TEXT,
                    vector_db_status TEXT,
                    web_interface_status TEXT
                )
            """)
            
            # Performance metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    query_response_time REAL,
                    document_processing_time REAL,
                    concurrent_users INTEGER,
                    queries_per_minute REAL,
                    error_rate REAL,
                    cache_hit_rate REAL
                )
            """)
            
            # User activity metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_activity_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    active_sessions INTEGER,
                    total_queries INTEGER,
                    unique_users INTEGER,
                    session_duration REAL,
                    feature_usage TEXT,
                    user_satisfaction REAL
                )
            """)
            
            # Security metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS security_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    failed_login_attempts INTEGER,
                    suspicious_activities INTEGER,
                    encrypted_documents INTEGER,
                    audit_events INTEGER,
                    security_alerts TEXT,
                    compliance_status TEXT
                )
            """)
            
            # Alerts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metric_value REAL,
                    threshold REAL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TIMESTAMP
                )
            """)
    
    def start_monitoring(self):
        """Start the monitoring system."""
        if self.is_monitoring:
            logger.warning("Monitoring is already running")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Production monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        
        logger.info("Production monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Collect all metrics
                system_metrics = self._collect_system_metrics()
                performance_metrics = self._collect_performance_metrics()
                user_activity_metrics = self._collect_user_activity_metrics()
                security_metrics = self._collect_security_metrics()
                
                # Store metrics
                self._store_metrics(system_metrics, performance_metrics, 
                                  user_activity_metrics, security_metrics)
                
                # Check for alerts
                self._check_alerts(system_metrics, performance_metrics, 
                                 user_activity_metrics, security_metrics)
                
                # Clean up old data
                self._cleanup_old_data()
                
                # Wait for next interval
                time.sleep(self.config["monitoring_interval"])
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system health metrics."""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Active connections
            active_connections = len(psutil.net_connections())
            
            # Service status checks
            ollama_status = self._check_service_status("ollama")
            vector_db_status = self._check_vector_db_status()
            web_interface_status = self._check_web_interface_status()
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                active_connections=active_connections,
                ollama_status=ollama_status,
                vector_db_status=vector_db_status,
                web_interface_status=web_interface_status
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                active_connections=0,
                ollama_status="error",
                vector_db_status="error",
                web_interface_status="error"
            )
    
    def _collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect application performance metrics."""
        try:
            # Query response time (simulated)
            query_response_time = self._get_average_response_time()
            
            # Document processing time (simulated)
            document_processing_time = self._get_document_processing_time()
            
            # Concurrent users (simulated)
            concurrent_users = self._get_concurrent_users()
            
            # Queries per minute
            queries_per_minute = self._get_queries_per_minute()
            
            # Error rate
            error_rate = self._get_error_rate()
            
            # Cache hit rate
            cache_hit_rate = self._get_cache_hit_rate()
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                query_response_time=query_response_time,
                document_processing_time=document_processing_time,
                concurrent_users=concurrent_users,
                queries_per_minute=queries_per_minute,
                error_rate=error_rate,
                cache_hit_rate=cache_hit_rate
            )
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                query_response_time=0.0,
                document_processing_time=0.0,
                concurrent_users=0,
                queries_per_minute=0.0,
                error_rate=0.0,
                cache_hit_rate=0.0
            )
    
    def _collect_user_activity_metrics(self) -> UserActivityMetrics:
        """Collect user activity metrics."""
        try:
            # Active sessions
            active_sessions = self._get_active_sessions()
            
            # Total queries
            total_queries = self._get_total_queries()
            
            # Unique users
            unique_users = self._get_unique_users()
            
            # Session duration
            session_duration = self._get_average_session_duration()
            
            # Feature usage
            feature_usage = self._get_feature_usage()
            
            # User satisfaction
            user_satisfaction = self._get_user_satisfaction()
            
            return UserActivityMetrics(
                timestamp=datetime.now(),
                active_sessions=active_sessions,
                total_queries=total_queries,
                unique_users=unique_users,
                session_duration=session_duration,
                feature_usage=feature_usage,
                user_satisfaction=user_satisfaction
            )
            
        except Exception as e:
            logger.error(f"Error collecting user activity metrics: {e}")
            return UserActivityMetrics(
                timestamp=datetime.now(),
                active_sessions=0,
                total_queries=0,
                unique_users=0,
                session_duration=0.0,
                feature_usage={},
                user_satisfaction=0.0
            )
    
    def _collect_security_metrics(self) -> SecurityMetrics:
        """Collect security metrics."""
        try:
            # Failed login attempts
            failed_login_attempts = self._get_failed_login_attempts()
            
            # Suspicious activities
            suspicious_activities = self._get_suspicious_activities()
            
            # Encrypted documents
            encrypted_documents = self._get_encrypted_documents_count()
            
            # Audit events
            audit_events = self._get_audit_events_count()
            
            # Security alerts
            security_alerts = self._get_security_alerts()
            
            # Compliance status
            compliance_status = self._get_compliance_status()
            
            return SecurityMetrics(
                timestamp=datetime.now(),
                failed_login_attempts=failed_login_attempts,
                suspicious_activities=suspicious_activities,
                encrypted_documents=encrypted_documents,
                audit_events=audit_events,
                security_alerts=security_alerts,
                compliance_status=compliance_status
            )
            
        except Exception as e:
            logger.error(f"Error collecting security metrics: {e}")
            return SecurityMetrics(
                timestamp=datetime.now(),
                failed_login_attempts=0,
                suspicious_activities=0,
                encrypted_documents=0,
                audit_events=0,
                security_alerts=[],
                compliance_status="unknown"
            )
    
    def _check_service_status(self, service: str) -> str:
        """Check if a service is running."""
        try:
            if service == "ollama":
                response = requests.get(f"{self.config['endpoints']['ollama']}/api/tags", timeout=5)
                return "running" if response.status_code == 200 else "error"
            else:
                return "unknown"
        except Exception:
            return "error"
    
    def _check_vector_db_status(self) -> str:
        """Check vector database status."""
        try:
            # Check if ChromaDB is accessible
            if os.path.exists("chroma_db"):
                return "running"
            else:
                return "error"
        except Exception:
            return "error"
    
    def _check_web_interface_status(self) -> str:
        """Check web interface status."""
        try:
            response = requests.get(f"{self.config['endpoints']['lawyeragent']}/health", timeout=5)
            return "running" if response.status_code == 200 else "error"
        except Exception:
            return "error"
    
    def _get_average_response_time(self) -> float:
        """Get average query response time."""
        # Simulated - in real implementation, this would query the application logs
        return 2.5  # seconds
    
    def _get_document_processing_time(self) -> float:
        """Get average document processing time."""
        # Simulated
        return 15.0  # seconds
    
    def _get_concurrent_users(self) -> int:
        """Get number of concurrent users."""
        # Simulated
        return 3
    
    def _get_queries_per_minute(self) -> float:
        """Get queries per minute."""
        # Simulated
        return 12.5
    
    def _get_error_rate(self) -> float:
        """Get error rate percentage."""
        # Simulated
        return 1.2  # percentage
    
    def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate."""
        # Simulated
        return 85.0  # percentage
    
    def _get_active_sessions(self) -> int:
        """Get number of active sessions."""
        # Simulated
        return 5
    
    def _get_total_queries(self) -> int:
        """Get total queries in the last hour."""
        # Simulated
        return 750
    
    def _get_unique_users(self) -> int:
        """Get number of unique users in the last hour."""
        # Simulated
        return 8
    
    def _get_average_session_duration(self) -> float:
        """Get average session duration in minutes."""
        # Simulated
        return 45.0  # minutes
    
    def _get_feature_usage(self) -> Dict[str, int]:
        """Get feature usage statistics."""
        # Simulated
        return {
            "search": 150,
            "filter": 75,
            "document_generation": 25,
            "export": 30,
            "templates": 20
        }
    
    def _get_user_satisfaction(self) -> float:
        """Get user satisfaction score."""
        # Simulated
        return 4.2  # out of 5
    
    def _get_failed_login_attempts(self) -> int:
        """Get failed login attempts in the last hour."""
        # Simulated
        return 2
    
    def _get_suspicious_activities(self) -> int:
        """Get suspicious activities detected."""
        # Simulated
        return 0
    
    def _get_encrypted_documents_count(self) -> int:
        """Get number of encrypted documents."""
        # Simulated
        return 1250
    
    def _get_audit_events_count(self) -> int:
        """Get number of audit events in the last hour."""
        # Simulated
        return 45
    
    def _get_security_alerts(self) -> List[str]:
        """Get current security alerts."""
        # Simulated
        return []
    
    def _get_compliance_status(self) -> str:
        """Get compliance status."""
        # Simulated
        return "compliant"
    
    def _store_metrics(self, system_metrics: SystemMetrics, 
                      performance_metrics: PerformanceMetrics,
                      user_activity_metrics: UserActivityMetrics,
                      security_metrics: SecurityMetrics):
        """Store metrics in database and memory."""
        # Store in memory
        self.metrics_history[MetricType.SYSTEM_HEALTH].append(system_metrics)
        self.metrics_history[MetricType.PERFORMANCE].append(performance_metrics)
        self.metrics_history[MetricType.USER_ACTIVITY].append(user_activity_metrics)
        self.metrics_history[MetricType.SECURITY].append(security_metrics)
        
        # Store in database
        with sqlite3.connect("monitoring.db") as conn:
            # System metrics
            conn.execute("""
                INSERT INTO system_metrics (
                    cpu_usage, memory_usage, disk_usage, network_io,
                    active_connections, ollama_status, vector_db_status, web_interface_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                system_metrics.cpu_usage, system_metrics.memory_usage,
                system_metrics.disk_usage, json.dumps(system_metrics.network_io),
                system_metrics.active_connections, system_metrics.ollama_status,
                system_metrics.vector_db_status, system_metrics.web_interface_status
            ))
            
            # Performance metrics
            conn.execute("""
                INSERT INTO performance_metrics (
                    query_response_time, document_processing_time, concurrent_users,
                    queries_per_minute, error_rate, cache_hit_rate
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                performance_metrics.query_response_time,
                performance_metrics.document_processing_time,
                performance_metrics.concurrent_users,
                performance_metrics.queries_per_minute,
                performance_metrics.error_rate,
                performance_metrics.cache_hit_rate
            ))
            
            # User activity metrics
            conn.execute("""
                INSERT INTO user_activity_metrics (
                    active_sessions, total_queries, unique_users,
                    session_duration, feature_usage, user_satisfaction
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_activity_metrics.active_sessions,
                user_activity_metrics.total_queries,
                user_activity_metrics.unique_users,
                user_activity_metrics.session_duration,
                json.dumps(user_activity_metrics.feature_usage),
                user_activity_metrics.user_satisfaction
            ))
            
            # Security metrics
            conn.execute("""
                INSERT INTO security_metrics (
                    failed_login_attempts, suspicious_activities, encrypted_documents,
                    audit_events, security_alerts, compliance_status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                security_metrics.failed_login_attempts,
                security_metrics.suspicious_activities,
                security_metrics.encrypted_documents,
                security_metrics.audit_events,
                json.dumps(security_metrics.security_alerts),
                security_metrics.compliance_status
            ))
    
    def _check_alerts(self, system_metrics: SystemMetrics,
                     performance_metrics: PerformanceMetrics,
                     user_activity_metrics: UserActivityMetrics,
                     security_metrics: SecurityMetrics):
        """Check for alert conditions."""
        thresholds = self.config["alert_thresholds"]
        
        # CPU usage alert
        if system_metrics.cpu_usage > thresholds["cpu_usage"]:
            self._create_alert("high_cpu_usage", "warning", 
                             f"CPU usage is {system_metrics.cpu_usage:.1f}%",
                             system_metrics.cpu_usage, thresholds["cpu_usage"])
        
        # Memory usage alert
        if system_metrics.memory_usage > thresholds["memory_usage"]:
            self._create_alert("high_memory_usage", "warning",
                             f"Memory usage is {system_metrics.memory_usage:.1f}%",
                             system_metrics.memory_usage, thresholds["memory_usage"])
        
        # Response time alert
        if performance_metrics.query_response_time > thresholds["response_time"]:
            self._create_alert("high_response_time", "warning",
                             f"Response time is {performance_metrics.query_response_time:.1f}s",
                             performance_metrics.query_response_time, thresholds["response_time"])
        
        # Error rate alert
        if performance_metrics.error_rate > thresholds["error_rate"]:
            self._create_alert("high_error_rate", "critical",
                             f"Error rate is {performance_metrics.error_rate:.1f}%",
                             performance_metrics.error_rate, thresholds["error_rate"])
        
        # Failed login attempts alert
        if security_metrics.failed_login_attempts > thresholds["failed_logins"]:
            self._create_alert("high_failed_logins", "critical",
                             f"Failed login attempts: {security_metrics.failed_login_attempts}",
                             security_metrics.failed_login_attempts, thresholds["failed_logins"])
    
    def _create_alert(self, alert_type: str, severity: str, message: str,
                     metric_value: float, threshold: float):
        """Create and store an alert."""
        alert = {
            "timestamp": datetime.now(),
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "metric_value": metric_value,
            "threshold": threshold
        }
        
        # Store in database
        with sqlite3.connect("monitoring.db") as conn:
            conn.execute("""
                INSERT INTO alerts (
                    alert_type, severity, message, metric_value, threshold
                ) VALUES (?, ?, ?, ?, ?)
            """, (alert_type, severity, message, metric_value, threshold))
        
        # Store in memory
        self.alerts.append(alert)
        
        # Send alert notifications
        self._send_alert_notifications(alert)
        
        logger.warning(f"Alert: {severity.upper()} - {message}")
    
    def _send_alert_notifications(self, alert: Dict[str, Any]):
        """Send alert notifications through configured channels."""
        for channel in self.config["alert_channels"]:
            try:
                if channel == "console":
                    self._send_console_alert(alert)
                elif channel == "email":
                    self._send_email_alert(alert)
                elif channel == "webhook":
                    self._send_webhook_alert(alert)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel}: {e}")
    
    def _send_console_alert(self, alert: Dict[str, Any]):
        """Send alert to console."""
        print(f"[{alert['severity'].upper()}] {alert['message']}")
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """Send alert via email."""
        # Implementation would use SMTP
        pass
    
    def _send_webhook_alert(self, alert: Dict[str, Any]):
        """Send alert via webhook."""
        # Implementation would use HTTP POST
        pass
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config["retention_days"])
            
            with sqlite3.connect("monitoring.db") as conn:
                # Clean up old metrics
                conn.execute("DELETE FROM system_metrics WHERE timestamp < ?", (cutoff_date,))
                conn.execute("DELETE FROM performance_metrics WHERE timestamp < ?", (cutoff_date,))
                conn.execute("DELETE FROM user_activity_metrics WHERE timestamp < ?", (cutoff_date,))
                conn.execute("DELETE FROM security_metrics WHERE timestamp < ?", (cutoff_date,))
                
                # Clean up resolved alerts older than 7 days
                alert_cutoff = datetime.now() - timedelta(days=7)
                conn.execute("DELETE FROM alerts WHERE resolved = 1 AND timestamp < ?", (alert_cutoff,))
            
            logger.info("Old monitoring data cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        if not self.metrics_history[MetricType.SYSTEM_HEALTH]:
            return {"message": "No metrics available"}
        
        latest_system = self.metrics_history[MetricType.SYSTEM_HEALTH][-1]
        latest_performance = self.metrics_history[MetricType.PERFORMANCE][-1]
        latest_user_activity = self.metrics_history[MetricType.USER_ACTIVITY][-1]
        latest_security = self.metrics_history[MetricType.SECURITY][-1]
        
        return {
            "timestamp": latest_system.timestamp.isoformat(),
            "system_health": {
                "cpu_usage": latest_system.cpu_usage,
                "memory_usage": latest_system.memory_usage,
                "disk_usage": latest_system.disk_usage,
                "ollama_status": latest_system.ollama_status,
                "vector_db_status": latest_system.vector_db_status,
                "web_interface_status": latest_system.web_interface_status
            },
            "performance": {
                "query_response_time": latest_performance.query_response_time,
                "concurrent_users": latest_performance.concurrent_users,
                "queries_per_minute": latest_performance.queries_per_minute,
                "error_rate": latest_performance.error_rate
            },
            "user_activity": {
                "active_sessions": latest_user_activity.active_sessions,
                "total_queries": latest_user_activity.total_queries,
                "unique_users": latest_user_activity.unique_users,
                "user_satisfaction": latest_user_activity.user_satisfaction
            },
            "security": {
                "failed_login_attempts": latest_security.failed_login_attempts,
                "encrypted_documents": latest_security.encrypted_documents,
                "compliance_status": latest_security.compliance_status
            },
            "active_alerts": len([a for a in self.alerts if not a.get("resolved", False)])
        }
    
    def get_metrics_history(self, metric_type: MetricType, 
                          hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics history for a specific type."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        metrics = []
        for metric in self.metrics_history[metric_type]:
            if metric.timestamp >= cutoff_time:
                metrics.append(asdict(metric))
        
        return metrics
    
    def get_alerts(self, severity: Optional[str] = None, 
                  resolved: bool = False) -> List[Dict[str, Any]]:
        """Get alerts with optional filtering."""
        with sqlite3.connect("monitoring.db") as conn:
            query = "SELECT * FROM alerts WHERE resolved = ?"
            params = [resolved]
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            query += " ORDER BY timestamp DESC LIMIT 100"
            
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


def main():
    """Main function for running the production monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LawyerAgent Production Monitor")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--metrics", action="store_true", help="Show current metrics")
    parser.add_argument("--alerts", action="store_true", help="Show active alerts")
    
    args = parser.parse_args()
    
    monitor = ProductionMonitor()
    
    if args.start:
        print("Starting production monitoring...")
        monitor.start_monitoring()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            monitor.stop_monitoring()
    
    elif args.status:
        metrics = monitor.get_current_metrics()
        print("Current System Status:")
        print(json.dumps(metrics, indent=2, default=str))
    
    elif args.metrics:
        for metric_type in MetricType:
            history = monitor.get_metrics_history(metric_type, hours=1)
            print(f"\n{metric_type.value.upper()} Metrics (Last Hour):")
            print(json.dumps(history, indent=2, default=str))
    
    elif args.alerts:
        alerts = monitor.get_alerts(resolved=False)
        print("Active Alerts:")
        print(json.dumps(alerts, indent=2, default=str))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 