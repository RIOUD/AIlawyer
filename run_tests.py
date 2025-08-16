#!/usr/bin/env python3
"""
Comprehensive Test Runner for Legal Assistant AI Platform

This script provides a unified interface for running all types of tests
including unit tests, integration tests, security tests, and performance tests.
"""

import os
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class TestRunner:
    """Comprehensive test runner for the Legal Assistant platform."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.test_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Test categories
        self.test_categories = {
            "unit": {
                "pattern": "test_*.py",
                "marker": "unit",
                "description": "Unit tests"
            },
            "integration": {
                "pattern": "test_*_integration.py",
                "marker": "integration", 
                "description": "Integration tests"
            },
            "security": {
                "pattern": "test_*_security.py",
                "marker": "security",
                "description": "Security tests"
            },
            "performance": {
                "pattern": "test_*_performance.py",
                "marker": "performance",
                "description": "Performance tests"
            },
            "all": {
                "pattern": "test_*.py",
                "marker": None,
                "description": "All tests"
            }
        }
    
    def run_tests(self, 
                  category: str = "all",
                  verbose: bool = False,
                  coverage: bool = False,
                  parallel: bool = False,
                  output_format: str = "text") -> Dict[str, Any]:
        """
        Run tests for the specified category.
        
        Args:
            category: Test category to run
            verbose: Enable verbose output
            coverage: Generate coverage report
            parallel: Run tests in parallel
            output_format: Output format (text, json, html)
            
        Returns:
            Test results dictionary
        """
        if category not in self.test_categories:
            raise ValueError(f"Invalid test category: {category}")
        
        test_config = self.test_categories[category]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Build pytest command
        cmd = self._build_pytest_command(
            category=category,
            test_config=test_config,
            verbose=verbose,
            coverage=coverage,
            parallel=parallel,
            output_format=output_format,
            timestamp=timestamp
        )
        
        print(f"Running {test_config['description']}...")
        print(f"Command: {' '.join(cmd)}")
        print("-" * 80)
        
        # Run tests
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        # Parse results
        test_results = self._parse_test_results(
            result=result,
            category=category,
            duration=end_time - start_time,
            timestamp=timestamp
        )
        
        # Generate report
        self._generate_report(test_results, output_format, timestamp)
        
        return test_results
    
    def _build_pytest_command(self, 
                             category: str,
                             test_config: Dict[str, Any],
                             verbose: bool,
                             coverage: bool,
                             parallel: bool,
                             output_format: str,
                             timestamp: str) -> List[str]:
        """Build pytest command with appropriate arguments."""
        cmd = [sys.executable, "-m", "pytest"]
        
        # Add test directory
        cmd.append(str(self.test_dir))
        
        # Add pattern for test discovery
        if category != "all":
            cmd.extend(["-k", test_config["pattern"].replace("*.py", "")])
        
        # Add marker if specified
        if test_config["marker"]:
            cmd.extend(["-m", test_config["marker"]])
        
        # Add verbose flag
        if verbose:
            cmd.append("-v")
        
        # Add coverage if requested
        if coverage:
            cmd.extend([
                "--cov=.",
                "--cov-report=html:test_reports/coverage",
                "--cov-report=term-missing"
            ])
        
        # Add parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add output format
        if output_format == "json":
            cmd.extend([
                "--json-report",
                f"--json-report-file=test_reports/results_{category}_{timestamp}.json"
            ])
        elif output_format == "html":
            cmd.extend([
                "--html=test_reports/report.html",
                "--self-contained-html"
            ])
        
        # Add additional options
        cmd.extend([
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "--color=yes"
        ])
        
        return cmd
    
    def _parse_test_results(self, 
                           result: subprocess.CompletedProcess,
                           category: str,
                           duration: float,
                           timestamp: str) -> Dict[str, Any]:
        """Parse test execution results."""
        return {
            "category": category,
            "timestamp": timestamp,
            "duration": duration,
            "return_code": result.returncode,
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "summary": self._extract_summary(result.stdout)
        }
    
    def _extract_summary(self, stdout: str) -> Dict[str, Any]:
        """Extract test summary from pytest output."""
        summary = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0
        }
        
        # Parse pytest output for test counts
        lines = stdout.split('\n')
        for line in lines:
            if "passed" in line and "failed" in line:
                # Extract numbers from summary line
                import re
                numbers = re.findall(r'(\d+)', line)
                if len(numbers) >= 4:
                    summary["passed"] = int(numbers[0])
                    summary["failed"] = int(numbers[1])
                    summary["skipped"] = int(numbers[2])
                    summary["errors"] = int(numbers[3])
                    summary["total"] = sum(summary.values())
                break
        
        return summary
    
    def _generate_report(self, 
                        test_results: Dict[str, Any],
                        output_format: str,
                        timestamp: str):
        """Generate test report."""
        if output_format == "json":
            report_file = self.reports_dir / f"test_report_{timestamp}.json"
            with open(report_file, 'w') as f:
                json.dump(test_results, f, indent=2)
            print(f"JSON report saved to: {report_file}")
        
        # Always print summary
        self._print_summary(test_results)
    
    def _print_summary(self, test_results: Dict[str, Any]):
        """Print test execution summary."""
        print("\n" + "=" * 80)
        print("TEST EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Category: {test_results['category']}")
        print(f"Timestamp: {test_results['timestamp']}")
        print(f"Duration: {test_results['duration']:.2f} seconds")
        print(f"Status: {'PASSED' if test_results['success'] else 'FAILED'}")
        
        summary = test_results['summary']
        print(f"\nTest Results:")
        print(f"  Passed: {summary['passed']}")
        print(f"  Failed: {summary['failed']}")
        print(f"  Skipped: {summary['skipped']}")
        print(f"  Errors: {summary['errors']}")
        print(f"  Total: {summary['total']}")
        
        if test_results['success']:
            print("\n✅ All tests passed successfully!")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
    
    def run_security_scan(self) -> Dict[str, Any]:
        """Run security scanning tools."""
        print("Running security scans...")
        
        security_results = {
            "bandit": self._run_bandit(),
            "safety": self._run_safety(),
            "pip_audit": self._run_pip_audit()
        }
        
        return security_results
    
    def _run_bandit(self) -> Dict[str, Any]:
        """Run bandit security scanner."""
        try:
            cmd = [sys.executable, "-m", "bandit", "-r", ".", "-f", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"success": True, "issues": []}
            else:
                try:
                    issues = json.loads(result.stdout)
                    return {"success": False, "issues": issues}
                except json.JSONDecodeError:
                    return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_safety(self) -> Dict[str, Any]:
        """Run safety vulnerability scanner."""
        try:
            cmd = [sys.executable, "-m", "safety", "check", "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"success": True, "vulnerabilities": []}
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    return {"success": False, "vulnerabilities": vulnerabilities}
                except json.JSONDecodeError:
                    return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_pip_audit(self) -> Dict[str, Any]:
        """Run pip-audit vulnerability scanner."""
        try:
            cmd = [sys.executable, "-m", "pip_audit", "--format", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"success": True, "vulnerabilities": []}
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    return {"success": False, "vulnerabilities": vulnerabilities}
                except json.JSONDecodeError:
                    return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_code_quality_checks(self) -> Dict[str, Any]:
        """Run code quality checks."""
        print("Running code quality checks...")
        
        quality_results = {
            "black": self._run_black(),
            "flake8": self._run_flake8(),
            "mypy": self._run_mypy()
        }
        
        return quality_results
    
    def _run_black(self) -> Dict[str, Any]:
        """Run black code formatter check."""
        try:
            cmd = [sys.executable, "-m", "black", "--check", "."]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_flake8(self) -> Dict[str, Any]:
        """Run flake8 linting."""
        try:
            cmd = [sys.executable, "-m", "flake8", "."]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_mypy(self) -> Dict[str, Any]:
        """Run mypy type checking."""
        try:
            cmd = [sys.executable, "-m", "mypy", "."]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_full_test_suite(self, 
                           include_security: bool = True,
                           include_quality: bool = True) -> Dict[str, Any]:
        """Run the complete test suite."""
        print("=" * 80)
        print("RUNNING COMPLETE TEST SUITE")
        print("=" * 80)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "security": {},
            "quality": {}
        }
        
        # Run all test categories
        for category in ["unit", "integration", "security", "performance"]:
            print(f"\nRunning {category} tests...")
            results["tests"][category] = self.run_tests(
                category=category,
                verbose=True,
                coverage=True
            )
        
        # Run security scans
        if include_security:
            print(f"\nRunning security scans...")
            results["security"] = self.run_security_scan()
        
        # Run quality checks
        if include_quality:
            print(f"\nRunning quality checks...")
            results["quality"] = self.run_code_quality_checks()
        
        # Generate comprehensive report
        self._generate_comprehensive_report(results)
        
        return results
    
    def _generate_comprehensive_report(self, results: Dict[str, Any]):
        """Generate comprehensive test report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"comprehensive_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nComprehensive report saved to: {report_file}")
        
        # Print summary
        self._print_comprehensive_summary(results)
    
    def _print_comprehensive_summary(self, results: Dict[str, Any]):
        """Print comprehensive test summary."""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        # Test results summary
        test_success = all(
            result["success"] for result in results["tests"].values()
        )
        print(f"Tests: {'✅ PASSED' if test_success else '❌ FAILED'}")
        
        # Security results summary
        if results["security"]:
            security_success = all(
                result["success"] for result in results["security"].values()
            )
            print(f"Security: {'✅ PASSED' if security_success else '❌ FAILED'}")
        
        # Quality results summary
        if results["quality"]:
            quality_success = all(
                result["success"] for result in results["quality"].values()
            )
            print(f"Quality: {'✅ PASSED' if quality_success else '❌ FAILED'}")
        
        overall_success = test_success
        if results["security"]:
            overall_success = overall_success and security_success
        if results["quality"]:
            overall_success = overall_success and quality_success
        
        print(f"\nOverall Status: {'✅ PASSED' if overall_success else '❌ FAILED'}")


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Legal Assistant AI Platform Test Runner")
    
    parser.add_argument(
        "--category", "-c",
        choices=["unit", "integration", "security", "performance", "all"],
        default="all",
        help="Test category to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-C",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Run tests in parallel"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "html"],
        default="text",
        help="Output format"
    )
    
    parser.add_argument(
        "--security-scan", "-s",
        action="store_true",
        help="Run security scans"
    )
    
    parser.add_argument(
        "--quality-check", "-q",
        action="store_true",
        help="Run code quality checks"
    )
    
    parser.add_argument(
        "--full-suite", "-F",
        action="store_true",
        help="Run complete test suite"
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner()
    
    try:
        if args.full_suite:
            # Run complete test suite
            runner.run_full_test_suite(
                include_security=args.security_scan,
                include_quality=args.quality_check
            )
        elif args.security_scan:
            # Run only security scans
            results = runner.run_security_scan()
            print(json.dumps(results, indent=2))
        elif args.quality_check:
            # Run only quality checks
            results = runner.run_code_quality_checks()
            print(json.dumps(results, indent=2))
        else:
            # Run specific test category
            runner.run_tests(
                category=args.category,
                verbose=args.verbose,
                coverage=args.coverage,
                parallel=args.parallel,
                output_format=args.format
            )
    
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 