#!/usr/bin/env python3
"""
Dependency Update and Security Management Script

Automates dependency updates and security checks for the Legal Assistant AI Platform.
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse


class DependencyManager:
    """Manages dependency updates and security checks."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.requirements_file = self.project_root / "requirements.txt"
        
    def check_current_vulnerabilities(self) -> Dict[str, Any]:
        """Check for current vulnerabilities in dependencies."""
        print("🔍 Checking current vulnerabilities...")
        
        results = {
            'safety': self._run_safety_check(),
            'pip_audit': self._run_pip_audit_check(),
            'outdated': self._check_outdated_packages()
        }
        
        return results
    
    def _run_safety_check(self) -> Dict[str, Any]:
        """Run Safety vulnerability check."""
        try:
            result = subprocess.run(
                ['safety', 'scan', '-r', str(self.requirements_file), '--json'],
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
                    
        except Exception as e:
            return {
                'success': False,
                'vulnerabilities': [],
                'message': f'Safety check failed: {e}'
            }
    
    def _run_pip_audit_check(self) -> Dict[str, Any]:
        """Run pip-audit vulnerability check."""
        try:
            result = subprocess.run(
                ['pip-audit', '-r', str(self.requirements_file), '--format', 'json'],
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
                    
        except Exception as e:
            return {
                'success': False,
                'vulnerabilities': [],
                'message': f'pip-audit check failed: {e}'
            }
    
    def _check_outdated_packages(self) -> Dict[str, Any]:
        """Check for outdated packages."""
        try:
            result = subprocess.run(
                ['pip', 'list', '--outdated', '--format', 'json'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            if result.returncode == 0:
                try:
                    outdated = json.loads(result.stdout)
                    return {
                        'success': True,
                        'outdated': outdated,
                        'message': f'Found {len(outdated)} outdated packages'
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'outdated': [],
                        'message': 'Failed to parse outdated packages'
                    }
            else:
                return {
                    'success': False,
                    'outdated': [],
                    'message': 'Failed to check outdated packages'
                }
                
        except Exception as e:
            return {
                'success': False,
                'outdated': [],
                'message': f'Outdated check failed: {e}'
            }
    
    def update_requirements_file(self) -> bool:
        """Update requirements.txt with secure versions."""
        print("📦 Updating requirements.txt with secure versions...")
        
        # Read current requirements
        if not self.requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        with open(self.requirements_file, 'r') as f:
            current_requirements = f.read()
        
        # Define secure version updates
        secure_updates = {
            'cryptography': '>=42.0.8,<43.0.0',
            'requests': '>=2.32.4,<3.0.0',
            'scikit-learn': '>=1.5.0,<2.0.0',
            'sentence-transformers': '>=3.1.0,<4.0.0',
            'langchain': '>=0.1.14,<0.2.0',
            'langchain-community': '>=0.2.9,<0.3.0',
            'langchain-ollama': '>=0.3.6,<0.4.0'
        }
        
        # Apply updates
        updated_requirements = current_requirements
        for package, version in secure_updates.items():
            # Replace exact version pins with secure ranges
            pattern = rf'{package}==[0-9.]+'
            replacement = f'{package}{version}'
            updated_requirements = re.sub(pattern, replacement, updated_requirements)
            
            # Add if not present
            if f'{package}>=' not in updated_requirements and f'{package}==' not in updated_requirements:
                updated_requirements += f'\n{package}{version}\n'
        
        # Write updated requirements
        backup_file = self.requirements_file.with_suffix('.txt.backup')
        with open(backup_file, 'w') as f:
            f.write(current_requirements)
        
        with open(self.requirements_file, 'w') as f:
            f.write(updated_requirements)
        
        print(f"✅ Updated requirements.txt (backup saved to {backup_file})")
        return True
    
    def install_updated_dependencies(self) -> bool:
        """Install updated dependencies."""
        print("🔧 Installing updated dependencies...")
        
        try:
            result = subprocess.run(
                ['pip', 'install', '-r', str(self.requirements_file), '--upgrade'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )
            
            if result.returncode == 0:
                print("✅ Dependencies updated successfully")
                return True
            else:
                print(f"❌ Failed to update dependencies: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    def generate_update_report(self, before_results: Dict[str, Any], after_results: Dict[str, Any]) -> str:
        """Generate a report comparing before and after security states."""
        report = []
        report.append("# Dependency Update Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Before state
        report.append("## Before Update")
        before_vulns = 0
        for scan_type, result in before_results.items():
            if 'vulnerabilities' in result:
                before_vulns += len(result.get('vulnerabilities', []))
        
        report.append(f"- Vulnerabilities: {before_vulns}")
        report.append("")
        
        # After state
        report.append("## After Update")
        after_vulns = 0
        for scan_type, result in after_results.items():
            if 'vulnerabilities' in result:
                after_vulns += len(result.get('vulnerabilities', []))
        
        report.append(f"- Vulnerabilities: {after_vulns}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        if before_vulns > after_vulns:
            report.append(f"✅ Reduced vulnerabilities from {before_vulns} to {after_vulns}")
        elif before_vulns == after_vulns:
            report.append(f"⚠️  No change in vulnerability count: {before_vulns}")
        else:
            report.append(f"❌ Increased vulnerabilities from {before_vulns} to {after_vulns}")
        
        return "\n".join(report)
    
    def run_full_update(self) -> bool:
        """Run a complete dependency update process."""
        print("🚀 Starting full dependency update process...")
        
        # Check current state
        print("\n1. Checking current vulnerabilities...")
        before_results = self.check_current_vulnerabilities()
        
        # Update requirements file
        print("\n2. Updating requirements.txt...")
        if not self.update_requirements_file():
            return False
        
        # Install updated dependencies
        print("\n3. Installing updated dependencies...")
        if not self.install_updated_dependencies():
            return False
        
        # Check new state
        print("\n4. Checking updated vulnerabilities...")
        after_results = self.check_current_vulnerabilities()
        
        # Generate report
        print("\n5. Generating update report...")
        report = self.generate_update_report(before_results, after_results)
        
        report_file = self.project_root / "dependency_update_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Update report saved to: {report_file}")
        
        return True


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Dependency Update Manager for Legal Assistant AI Platform')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--check-only', action='store_true', help='Only check vulnerabilities, don\'t update')
    parser.add_argument('--update-only', action='store_true', help='Only update requirements.txt, don\'t install')
    
    args = parser.parse_args()
    
    manager = DependencyManager(args.project_root)
    
    if args.check_only:
        print("🔍 Running vulnerability check only...")
        results = manager.check_current_vulnerabilities()
        
        # Print summary
        total_vulns = 0
        for scan_type, result in results.items():
            if 'vulnerabilities' in result:
                total_vulns += len(result.get('vulnerabilities', []))
        
        print(f"\nTotal vulnerabilities found: {total_vulns}")
        
    elif args.update_only:
        print("📦 Updating requirements.txt only...")
        manager.update_requirements_file()
        
    else:
        print("🚀 Running full dependency update...")
        success = manager.run_full_update()
        
        if success:
            print("\n✅ Dependency update completed successfully!")
        else:
            print("\n❌ Dependency update failed!")
            sys.exit(1)


if __name__ == "__main__":
    main() 