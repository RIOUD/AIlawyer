#!/usr/bin/env python3
"""
User Testing Scenarios Framework for LawyerAgent

Defines comprehensive testing scenarios for different user types and use cases.
Provides structured testing framework for validating system performance and usability.
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path
import sqlite3
import requests

# Import feedback system
from user_feedback_system import (
    UserFeedbackSystem, UserType, FeedbackCategory, 
    SentimentScore, SessionData
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestScenario(Enum):
    """Types of test scenarios."""
    BASIC_QUERY = "basic_query"
    ADVANCED_FILTERING = "advanced_filtering"
    DOCUMENT_GENERATION = "document_generation"
    SECURITY_FEATURES = "security_features"
    PERFORMANCE_TESTING = "performance_testing"
    INTEGRATION_TESTING = "integration_testing"
    STRESS_TESTING = "stress_testing"


class TestPriority(Enum):
    """Test priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TestCase:
    """Individual test case definition."""
    test_id: str
    scenario: TestScenario
    priority: TestPriority
    title: str
    description: str
    user_type: UserType
    prerequisites: List[str]
    steps: List[str]
    expected_results: List[str]
    success_criteria: List[str]
    estimated_duration: int  # minutes
    difficulty: str  # easy, medium, hard
    tags: List[str]


@dataclass
class TestSession:
    """Test session data."""
    session_id: str
    user_id: str
    test_cases: List[TestCase]
    start_time: datetime
    end_time: Optional[datetime]
    results: Dict[str, Any]
    feedback_collected: List[str]
    performance_metrics: Dict[str, float]


@dataclass
class TestResult:
    """Individual test result."""
    test_id: str
    user_id: str
    session_id: str
    passed: bool
    execution_time: float
    errors: List[str]
    feedback: Optional[str]
    performance_data: Dict[str, Any]
    timestamp: datetime


class UserTestingFramework:
    """
    Comprehensive user testing framework for LawyerAgent.
    """
    
    def __init__(self, feedback_system: UserFeedbackSystem):
        """
        Initialize the testing framework.
        
        Args:
            feedback_system: User feedback system instance
        """
        self.feedback_system = feedback_system
        self.test_cases = self._load_test_cases()
        self.test_results = []
        
        logger.info("User testing framework initialized")
    
    def _load_test_cases(self) -> List[TestCase]:
        """Load predefined test cases."""
        test_cases = []
        
        # Basic Query Test Cases
        test_cases.extend([
            TestCase(
                test_id="BQ001",
                scenario=TestScenario.BASIC_QUERY,
                priority=TestPriority.HIGH,
                title="Simple Legal Question",
                description="Ask a basic legal question and verify response accuracy",
                user_type=UserType.SOLO_LAWYER,
                prerequisites=["System running", "Sample documents loaded"],
                steps=[
                    "1. Start the LawyerAgent application",
                    "2. Navigate to the query interface",
                    "3. Ask: 'What are the requirements for filing a motion to dismiss?'",
                    "4. Review the response and source citations",
                    "5. Verify response relevance and accuracy"
                ],
                expected_results=[
                    "System provides relevant legal information",
                    "Response includes source citations",
                    "Information is accurate and up-to-date",
                    "Response time is under 30 seconds"
                ],
                success_criteria=[
                    "Response contains actionable legal information",
                    "At least 2 source documents are cited",
                    "Response time < 30 seconds",
                    "User rates response as helpful (4+ stars)"
                ],
                estimated_duration=10,
                difficulty="easy",
                tags=["basic", "query", "accuracy"]
            ),
            
            TestCase(
                test_id="BQ002",
                scenario=TestScenario.BASIC_QUERY,
                priority=TestPriority.HIGH,
                title="Multi-language Query",
                description="Test system's ability to handle queries in different languages",
                user_type=UserType.SMALL_FIRM,
                prerequisites=["System running", "Multi-language documents loaded"],
                steps=[
                    "1. Start the LawyerAgent application",
                    "2. Set language preference to French",
                    "3. Ask: 'Quelles sont les exigences pour un contrat de travail?'",
                    "4. Switch to Dutch and ask: 'Wat zijn de vereisten voor een arbeidsovereenkomst?'",
                    "5. Compare responses for consistency"
                ],
                expected_results=[
                    "System responds appropriately in French",
                    "System responds appropriately in Dutch",
                    "Responses are consistent across languages",
                    "Source documents are relevant to the jurisdiction"
                ],
                success_criteria=[
                    "Both language responses are accurate",
                    "Responses are jurisdictionally appropriate",
                    "Response time < 45 seconds per query",
                    "User confirms language support is adequate"
                ],
                estimated_duration=15,
                difficulty="medium",
                tags=["multilingual", "query", "jurisdiction"]
            )
        ])
        
        # Advanced Filtering Test Cases
        test_cases.extend([
            TestCase(
                test_id="AF001",
                scenario=TestScenario.ADVANCED_FILTERING,
                priority=TestPriority.MEDIUM,
                title="Jurisdiction-based Filtering",
                description="Test filtering by legal jurisdiction (Federaal/Vlaams/Waals/Brussels)",
                user_type=UserType.LARGE_FIRM,
                prerequisites=["System running", "Documents from multiple jurisdictions"],
                steps=[
                    "1. Access the filtering interface",
                    "2. Select 'Vlaams' jurisdiction filter",
                    "3. Search for employment law information",
                    "4. Verify only Flemish documents are returned",
                    "5. Switch to 'Federaal' jurisdiction and repeat"
                ],
                expected_results=[
                    "Filter correctly identifies jurisdiction",
                    "Only relevant documents are returned",
                    "Filter can be combined with other filters",
                    "Filter state is clearly indicated"
                ],
                success_criteria=[
                    "100% of returned documents match selected jurisdiction",
                    "Filter can be applied and removed easily",
                    "Filter combinations work correctly",
                    "User can understand filter results"
                ],
                estimated_duration=12,
                difficulty="medium",
                tags=["filtering", "jurisdiction", "search"]
            ),
            
            TestCase(
                test_id="AF002",
                scenario=TestScenario.ADVANCED_FILTERING,
                priority=TestPriority.MEDIUM,
                title="Document Type Filtering",
                description="Test filtering by document type (wetboeken, jurisprudentie, contracten)",
                user_type=UserType.LEGAL_RESEARCHER,
                prerequisites=["System running", "Various document types loaded"],
                steps=[
                    "1. Access the filtering interface",
                    "2. Select 'jurisprudentie' document type",
                    "3. Search for recent case law",
                    "4. Verify only case law documents are returned",
                    "5. Test date range filtering with document type"
                ],
                expected_results=[
                    "Filter correctly identifies document types",
                    "Date filtering works with document type filtering",
                    "Results are relevant to the search query",
                    "Filter combinations are intuitive"
                ],
                success_criteria=[
                    "All returned documents are of the selected type",
                    "Date filtering works correctly",
                    "Filter interface is intuitive",
                    "Results are relevant and recent"
                ],
                estimated_duration=10,
                difficulty="easy",
                tags=["filtering", "document_type", "date_range"]
            )
        ])
        
        # Document Generation Test Cases
        test_cases.extend([
            TestCase(
                test_id="DG001",
                scenario=TestScenario.DOCUMENT_GENERATION,
                priority=TestPriority.HIGH,
                title="Employment Contract Generation",
                description="Generate a standard employment contract using templates",
                user_type=UserType.SOLO_LAWYER,
                prerequisites=["System running", "Employment contract template available"],
                steps=[
                    "1. Access the document generation interface",
                    "2. Select 'Employment Contract' template",
                    "3. Fill in required variables (employer, employee, position, salary)",
                    "4. Generate the document",
                    "5. Review and export the generated document"
                ],
                expected_results=[
                    "Template loads correctly with all variables",
                    "Document is generated with proper formatting",
                    "All variables are correctly inserted",
                    "Document can be exported as PDF"
                ],
                success_criteria=[
                    "Document is legally compliant",
                    "All variables are properly filled",
                    "PDF export works correctly",
                    "Document formatting is professional"
                ],
                estimated_duration=20,
                difficulty="medium",
                tags=["document_generation", "templates", "employment"]
            ),
            
            TestCase(
                test_id="DG002",
                scenario=TestScenario.DOCUMENT_GENERATION,
                priority=TestPriority.MEDIUM,
                title="Custom Template Creation",
                description="Create and use a custom legal document template",
                user_type=UserType.LARGE_FIRM,
                prerequisites=["System running", "Template creation permissions"],
                steps=[
                    "1. Access template management interface",
                    "2. Create a new custom template",
                    "3. Define template variables and structure",
                    "4. Save and test the template",
                    "5. Generate a document using the custom template"
                ],
                expected_results=[
                    "Template creation interface is intuitive",
                    "Variables can be defined and validated",
                    "Template saves correctly",
                    "Generated document uses custom template"
                ],
                success_criteria=[
                    "Template creation is straightforward",
                    "Variables work correctly",
                    "Template can be reused",
                    "Generated document is properly formatted"
                ],
                estimated_duration=25,
                difficulty="hard",
                tags=["template_creation", "custom", "advanced"]
            )
        ])
        
        # Security Features Test Cases
        test_cases.extend([
            TestCase(
                test_id="SF001",
                scenario=TestScenario.SECURITY_FEATURES,
                priority=TestPriority.CRITICAL,
                title="Document Encryption",
                description="Test document encryption and secure storage",
                user_type=UserType.SOLO_LAWYER,
                prerequisites=["System running", "Security features enabled"],
                steps=[
                    "1. Upload a sensitive legal document",
                    "2. Verify document is encrypted at rest",
                    "3. Access the document through the system",
                    "4. Check audit logs for access records",
                    "5. Test secure deletion of the document"
                ],
                expected_results=[
                    "Document is encrypted when stored",
                    "Access is logged in audit trail",
                    "Document can be accessed securely",
                    "Secure deletion works correctly"
                ],
                success_criteria=[
                    "Document encryption is verified",
                    "Audit logs are complete and accurate",
                    "Access controls work properly",
                    "Secure deletion prevents recovery"
                ],
                estimated_duration=15,
                difficulty="medium",
                tags=["security", "encryption", "audit"]
            ),
            
            TestCase(
                test_id="SF002",
                scenario=TestScenario.SECURITY_FEATURES,
                priority=TestPriority.HIGH,
                title="Offline Operation",
                description="Verify system operates completely offline",
                user_type=UserType.SMALL_FIRM,
                prerequisites=["System running", "Internet connection available"],
                steps=[
                    "1. Disconnect from internet",
                    "2. Perform legal queries",
                    "3. Generate documents",
                    "4. Access stored documents",
                    "5. Verify no external connections are made"
                ],
                expected_results=[
                    "All functions work without internet",
                    "No external API calls are made",
                    "Local LLM processes queries",
                    "Local database stores all data"
                ],
                success_criteria=[
                    "100% offline operation verified",
                    "No network activity detected",
                    "All features remain functional",
                    "Performance is acceptable offline"
                ],
                estimated_duration=20,
                difficulty="easy",
                tags=["security", "offline", "privacy"]
            )
        ])
        
        # Performance Testing Test Cases
        test_cases.extend([
            TestCase(
                test_id="PT001",
                scenario=TestScenario.PERFORMANCE_TESTING,
                priority=TestPriority.MEDIUM,
                title="Concurrent User Testing",
                description="Test system performance with multiple concurrent users",
                user_type=UserType.LARGE_FIRM,
                prerequisites=["System running", "Multiple test users available"],
                steps=[
                    "1. Start 5 concurrent user sessions",
                    "2. Each user performs 10 queries",
                    "3. Monitor system performance metrics",
                    "4. Check for response time degradation",
                    "5. Verify system stability under load"
                ],
                expected_results=[
                    "System handles concurrent users",
                    "Response times remain acceptable",
                    "No system crashes or errors",
                    "All queries are processed correctly"
                ],
                success_criteria=[
                    "Average response time < 60 seconds",
                    "No system crashes or errors",
                    "All queries return results",
                    "Memory usage remains stable"
                ],
                estimated_duration=30,
                difficulty="hard",
                tags=["performance", "concurrent", "load_testing"]
            ),
            
            TestCase(
                test_id="PT002",
                scenario=TestScenario.PERFORMANCE_TESTING,
                priority=TestPriority.MEDIUM,
                title="Large Document Processing",
                description="Test system performance with large legal documents",
                user_type=UserType.LEGAL_RESEARCHER,
                prerequisites=["System running", "Large documents available"],
                steps=[
                    "1. Upload a 100+ page legal document",
                    "2. Process and index the document",
                    "3. Perform queries on the large document",
                    "4. Monitor processing time and memory usage",
                    "5. Verify query accuracy on large documents"
                ],
                expected_results=[
                    "Large document is processed successfully",
                    "Indexing completes in reasonable time",
                    "Queries return relevant results",
                    "Memory usage is acceptable"
                ],
                success_criteria=[
                    "Document processing < 10 minutes",
                    "Query response time < 45 seconds",
                    "Memory usage < 4GB",
                    "Query accuracy maintained"
                ],
                estimated_duration=25,
                difficulty="medium",
                tags=["performance", "large_documents", "processing"]
            )
        ])
        
        return test_cases
    
    def get_test_cases_for_user_type(self, user_type: UserType) -> List[TestCase]:
        """
        Get test cases appropriate for a specific user type.
        
        Args:
            user_type: Type of user
            
        Returns:
            List of relevant test cases
        """
        return [tc for tc in self.test_cases if tc.user_type == user_type]
    
    def get_test_cases_by_scenario(self, scenario: TestScenario) -> List[TestCase]:
        """
        Get test cases for a specific scenario.
        
        Args:
            scenario: Test scenario
            
        Returns:
            List of test cases for the scenario
        """
        return [tc for tc in self.test_cases if tc.scenario == scenario]
    
    def run_test_case(self, test_case: TestCase, user_id: str) -> TestResult:
        """
        Run a single test case.
        
        Args:
            test_case: Test case to run
            user_id: User ID running the test
            
        Returns:
            Test result
        """
        logger.info(f"Running test case: {test_case.test_id} - {test_case.title}")
        
        start_time = time.time()
        session_id = self.feedback_system.start_session(user_id)
        
        try:
            # Simulate test execution
            # In a real implementation, this would interact with the actual system
            time.sleep(test_case.estimated_duration * 0.1)  # Simulate execution time
            
            # Simulate test results
            passed = random.choice([True, True, True, False])  # 75% pass rate for demo
            errors = [] if passed else ["Simulated test error"]
            
            execution_time = time.time() - start_time
            
            # Collect feedback
            feedback_id = None
            if passed:
                feedback_id = self.feedback_system.submit_feedback(
                    user_id=user_id,
                    category=FeedbackCategory.USABILITY,
                    sentiment=SentimentScore.POSITIVE,
                    title=f"Test passed: {test_case.title}",
                    description=f"Successfully completed test case {test_case.test_id}",
                    feature_used=test_case.scenario.value,
                    session_id=session_id
                )
            
            # Create test result
            result = TestResult(
                test_id=test_case.test_id,
                user_id=user_id,
                session_id=session_id,
                passed=passed,
                execution_time=execution_time,
                errors=errors,
                feedback=feedback_id,
                performance_data={
                    "response_time": execution_time,
                    "memory_usage": random.uniform(100, 500),
                    "cpu_usage": random.uniform(10, 30)
                },
                timestamp=datetime.now()
            )
            
            self.test_results.append(result)
            
            # End session
            session_data = SessionData(
                session_id=session_id,
                user_id=user_id,
                start_time=datetime.now() - timedelta(seconds=execution_time),
                end_time=datetime.now(),
                queries_count=len(test_case.steps),
                documents_accessed=[],
                features_used=[test_case.scenario.value],
                errors_encountered=errors,
                performance_metrics={"avg_response_time": execution_time}
            )
            self.feedback_system.end_session(session_id, session_data)
            
            logger.info(f"Test case {test_case.test_id} completed: {'PASSED' if passed else 'FAILED'}")
            return result
            
        except Exception as e:
            logger.error(f"Error running test case {test_case.test_id}: {e}")
            return TestResult(
                test_id=test_case.test_id,
                user_id=user_id,
                session_id=session_id,
                passed=False,
                execution_time=time.time() - start_time,
                errors=[str(e)],
                feedback=None,
                performance_data={},
                timestamp=datetime.now()
            )
    
    def run_test_suite(self, user_type: UserType, scenarios: Optional[List[TestScenario]] = None) -> Dict[str, Any]:
        """
        Run a complete test suite for a user type.
        
        Args:
            user_type: Type of user to test
            scenarios: Specific scenarios to test (if None, test all)
            
        Returns:
            Test suite results
        """
        logger.info(f"Running test suite for user type: {user_type.value}")
        
        # Get relevant test cases
        test_cases = self.get_test_cases_for_user_type(user_type)
        if scenarios:
            test_cases = [tc for tc in test_cases if tc.scenario in scenarios]
        
        # Create test user
        user_id = self.feedback_system.create_user_profile(
            user_type=user_type,
            experience_years=random.randint(5, 20),
            practice_areas=["general_practice"],
            jurisdiction="federaal",
            language_preference="dutch"
        )
        
        # Run test cases
        results = []
        for test_case in test_cases:
            result = self.run_test_case(test_case, user_id)
            results.append(result)
        
        # Calculate summary statistics
        total_tests = len(results)
        passed_tests = len([r for r in results if r.passed])
        failed_tests = total_tests - passed_tests
        avg_execution_time = sum(r.execution_time for r in results) / total_tests if total_tests > 0 else 0
        
        # Get feedback analytics
        analytics = self.feedback_system.get_feedback_analytics(user_type=user_type)
        
        suite_results = {
            "user_type": user_type.value,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "average_execution_time": avg_execution_time,
            "scenarios_tested": list(set(r.test_id[:2] for r in results)),
            "feedback_analytics": analytics,
            "detailed_results": [asdict(r) for r in results],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Test suite completed: {passed_tests}/{total_tests} tests passed")
        return suite_results
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a comprehensive test report.
        
        Args:
            results: Test suite results
            
        Returns:
            Path to generated report
        """
        report_path = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Test report generated: {report_path}")
        return report_path
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """
        Get overall test statistics.
        
        Returns:
            Test statistics
        """
        if not self.test_results:
            return {"message": "No test results available"}
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.passed])
        
        # Group by user type
        user_type_stats = {}
        for result in self.test_results:
            user_type = result.user_id  # In real implementation, get actual user type
            if user_type not in user_type_stats:
                user_type_stats[user_type] = {"total": 0, "passed": 0}
            user_type_stats[user_type]["total"] += 1
            if result.passed:
                user_type_stats[user_type]["passed"] += 1
        
        # Calculate pass rates
        for user_type in user_type_stats:
            stats = user_type_stats[user_type]
            stats["pass_rate"] = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "overall_pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "user_type_statistics": user_type_stats,
            "average_execution_time": sum(r.execution_time for r in self.test_results) / total_tests if total_tests > 0 else 0
        }


def main():
    """Main function for running user testing scenarios."""
    # Initialize feedback system
    feedback_system = UserFeedbackSystem()
    
    # Initialize testing framework
    testing_framework = UserTestingFramework(feedback_system)
    
    # Run test suites for different user types
    user_types = [UserType.SOLO_LAWYER, UserType.SMALL_FIRM, UserType.LARGE_FIRM]
    
    all_results = []
    
    for user_type in user_types:
        print(f"\n{'='*50}")
        print(f"Testing User Type: {user_type.value}")
        print(f"{'='*50}")
        
        # Run test suite
        results = testing_framework.run_test_suite(user_type)
        all_results.append(results)
        
        # Print summary
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Pass Rate: {results['pass_rate']:.1f}%")
        print(f"Average Execution Time: {results['average_execution_time']:.2f}s")
    
    # Generate overall report
    print(f"\n{'='*50}")
    print("OVERALL TEST RESULTS")
    print(f"{'='*50}")
    
    stats = testing_framework.get_test_statistics()
    print(json.dumps(stats, indent=2, default=str))
    
    # Generate detailed report
    report_path = testing_framework.generate_test_report({
        "test_suites": all_results,
        "overall_statistics": stats,
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"\nDetailed report saved to: {report_path}")


if __name__ == "__main__":
    main() 