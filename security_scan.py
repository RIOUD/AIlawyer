#!/usr/bin/env python3
"""
Security Scanning and Vulnerability Assessment for Legal Assistant AI Platform

Automates security checks including:
- Dependency vulnerability scanning
- Code security analysis
- Configuration validation
- Security best practices compliance
"""

import os
import sys
import subprocess
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse


class SecurityScanner:
    """Comprehensive security scanner for the Legal Assistant platform."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities': [],
            'warnings': [],
            'recommendations': [],
            'overall_score': 0
        }
    
    def run_dependency_scan(self) -> Dict[str, Any]:
        """Run dependency vulnerability scanning."""
        print("🔍 Running dependency vulnerability scan...")
        
        scan_results = {
            'safety_scan': self._run_safety_scan(),
            'pip_audit': self._run_pip_audit(),
            'bandit_scan': self._run_bandit_scan()
        }
        
        return scan_results
    
    def _run_safety_scan(self) -> Dict[str, Any]:
        """Run Safety vulnerability scanner."""
        try:
            result = subprocess.run(
                ['safety', 'scan', '-r', 'requirements.txt', '--json'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'vulnerabilities': [],
                    'message': 'No vulnerabilities found'
                }
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    return {
                        'success': False,
                        'vulnerabilities': vulnerabilities,
                        'message': f'Found {len(vulnerabilities)} vulnerabilities'
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'vulnerabilities': [],
                        'message': 'Failed to parse safety output'
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'vulnerabilities': [],
                'message': 'Safety scan timed out'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'vulnerabilities': [],
                'message': 'Safety not installed. Run: pip install safety'
            }
    
    def _run_pip_audit(self) -> Dict[str, Any]:
        """Run pip-audit vulnerability scanner."""
        try:
            result = subprocess.run(
                ['pip-audit', '-r', 'requirements.txt', '--format', 'json'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'vulnerabilities': [],
                    'message': 'No vulnerabilities found'
                }
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    return {
                        'success': False,
                        'vulnerabilities': vulnerabilities,
                        'message': f'Found {len(vulnerabilities)} vulnerabilities'
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'vulnerabilities': [],
                        'message': 'Failed to parse pip-audit output'
                    }
                    
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'vulnerabilities': [],
                'message': 'pip-audit scan timed out'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'vulnerabilities': [],
                'message': 'pip-audit not installed. Run: pip install pip-audit'
            }
    
    def _run_bandit_scan(self) -> Dict[str, Any]:
        """Run Bandit security linter."""
        try:
            result = subprocess.run([
                'bandit', '-r', '.', '-f', 'json', '-o', '/tmp/bandit_report.json',
                '--exclude', 'tests/,venv/,env/,__pycache__/,*.pyc'
            ], capture_output=True, text=True, cwd=self.project_root, timeout=300)
            
            if os.path.exists('/tmp/bandit_report.json'):
                with open('/tmp/bandit_report.json', 'r') as f:
                    bandit_results = json.load(f)
                
                os.remove('/tmp/bandit_report.json')
                
                return {
                    'success': True,
                    'issues': bandit_results.get('results', []),
                    'message': f'Found {len(bandit_results.get("results", []))} security issues'
                }
            else:
                return {
                    'success': False,
                    'issues': [],
                    'message': 'Bandit scan failed to generate report'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'issues': [],
                'message': 'Bandit scan timed out'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'issues': [],
                'message': 'Bandit not installed. Run: pip install bandit'
            }
    
    def check_configuration_security(self) -> Dict[str, Any]:
        """Check configuration security settings."""
        print("🔧 Checking configuration security...")
        
        issues = []
        warnings = []
        
        # Check for hardcoded secrets
        hardcoded_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret_key\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        python_files = list(self.project_root.rglob('*.py'))
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in hardcoded_patterns:
                    import re
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        issues.append({
                            'file': str(file_path),
                            'issue': 'Hardcoded secret detected',
                            'pattern': pattern,
                            'severity': 'HIGH'
                        })
            except Exception as e:
                warnings.append(f"Could not read {file_path}: {e}")
        
        # Check for .env file
        env_file = self.project_root / '.env'
        if env_file.exists():
            warnings.append("Found .env file - ensure it's not committed to version control")
        
        # Check for security headers in web app
        web_app_file = self.project_root / 'web_app.py'
        if web_app_file.exists():
            with open(web_app_file, 'r') as f:
                content = f.read()
                if 'app.secret_key' in content and 'os.getenv' not in content:
                    issues.append({
                        'file': 'web_app.py',
                        'issue': 'Hardcoded Flask secret key',
                        'severity': 'HIGH'
                    })
        
        return {
            'issues': issues,
            'warnings': warnings,
            'recommendations': [
                'Use environment variables for all secrets',
                'Add .env to .gitignore',
                'Implement proper secret management',
                'Use python-dotenv for configuration'
            ]
        }
    
    def check_dependency_versions(self) -> Dict[str, Any]:
        """Check for outdated or vulnerable dependency versions."""
        print("📦 Checking dependency versions...")
        
        issues = []
        recommendations = []
        
        # Read requirements.txt
        requirements_file = self.project_root / 'requirements.txt'
        if not requirements_file.exists():
            issues.append("requirements.txt not found")
            return {'issues': issues, 'recommendations': recommendations}
        
        with open(requirements_file, 'r') as f:
            requirements = f.read()
        
        # Check for exact version pinning
        import re
        exact_pins = re.findall(r'==([0-9.]+)', requirements)
        if exact_pins:
            recommendations.append(
                f"Consider using version ranges instead of exact pins for {len(exact_pins)} packages"
            )
        
        # Check for known vulnerable versions
        vulnerable_versions = {
            'cryptography': ['41.0.7'],
            'requests': ['2.31.0'],
            'scikit-learn': ['1.3.0'],
            'sentence-transformers': ['2.2.2'],
            'langchain': ['0.1.0'],
            'langchain-community': ['0.0.10']
        }
        
        for package, versions in vulnerable_versions.items():
            for version in versions:
                if f'{package}=={version}' in requirements:
                    issues.append({
                        'package': package,
                        'version': version,
                        'issue': 'Known vulnerable version',
                        'severity': 'HIGH'
                    })
        
        return {
            'issues': issues,
            'recommendations': recommendations
        }
    
    def generate_report(self, scan_results: Dict[str, Any]) -> str:
        """Generate a comprehensive security report."""
        print("📊 Generating security report...")
        
        report = []
        report.append("# Security Scan Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_vulnerabilities = 0
        total_issues = 0
        
        for scan_type, result in scan_results.items():
            if 'vulnerabilities' in result:
                total_vulnerabilities += len(result.get('vulnerabilities', []))
            if 'issues' in result:
                total_issues += len(result.get('issues', []))
        
        report.append("## Summary")
        report.append(f"- Total vulnerabilities: {total_vulnerabilities}")
        report.append(f"- Total security issues: {total_issues}")
        report.append("")
        
        # Detailed results
        for scan_type, result in scan_results.items():
            report.append(f"## {scan_type.replace('_', ' ').title()}")
            
            if result.get('success') is False:
                report.append(f"❌ {result.get('message', 'Scan failed')}")
            else:
                report.append(f"✅ {result.get('message', 'Scan completed successfully')}")
            
            if 'vulnerabilities' in result and result['vulnerabilities']:
                report.append("### Vulnerabilities:")
                for vuln in result['vulnerabilities']:
                    report.append(f"- {vuln}")
            
            if 'issues' in result and result['issues']:
                report.append("### Issues:")
                for issue in result['issues']:
                    report.append(f"- {issue}")
            
            if 'recommendations' in result and result['recommendations']:
                report.append("### Recommendations:")
                for rec in result['recommendations']:
                    report.append(f"- {rec}")
            
            report.append("")
        
        return "\n".join(report)
    
    def save_report(self, report: str, output_file: str = "security_report.md"):
        """Save the security report to a file."""
        output_path = self.project_root / output_file
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"📄 Security report saved to: {output_path}")
        return output_path
    
    def run_full_scan(self) -> Dict[str, Any]:
        """Run a complete security scan."""
        print("🚀 Starting comprehensive security scan...")
        
        scan_results = {
            'dependency_scan': self.run_dependency_scan(),
            'configuration_security': self.check_configuration_security(),
            'dependency_versions': self.check_dependency_versions()
        }
        
        # Generate and save report
        report = self.generate_report(scan_results)
        self.save_report(report)
        
        return scan_results


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Security Scanner for Legal Assistant AI Platform')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--output', default='security_report.md', help='Output report file')
    parser.add_argument('--quick', action='store_true', help='Run quick scan only')
    
    args = parser.parse_args()
    
    scanner = SecurityScanner(args.project_root)
    
    if args.quick:
        print("⚡ Running quick security scan...")
        results = scanner.check_configuration_security()
        report = scanner.generate_report({'quick_scan': results})
    else:
        print("🔍 Running full security scan...")
        results = scanner.run_full_scan()
        report = scanner.generate_report(results)
    
    scanner.save_report(report, args.output)
    
    # Print summary to console
    print("\n" + "="*50)
    print("SECURITY SCAN COMPLETED")
    print("="*50)
    print(f"Report saved to: {args.output}")
    
    # Count issues
    total_issues = 0
    for scan_type, result in results.items():
        if isinstance(result, dict):
            total_issues += len(result.get('issues', []))
            total_issues += len(result.get('vulnerabilities', []))
    
    if total_issues == 0:
        print("✅ No security issues found!")
    else:
        print(f"⚠️  Found {total_issues} security issues. Please review the report.")


if __name__ == "__main__":
    main() 