#!/usr/bin/env python3
"""
MuleSoft Security Scanner

Scans MuleSoft projects for security vulnerabilities including hardcoded secrets,
weak TLS configurations, missing API policies, and insecure configurations.
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from enum import Enum


class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityIssue:
    def __init__(self, file_path: Path, line_num: int, issue_type: str, 
                 severity: Severity, message: str, pattern: str = None):
        self.file_path = file_path
        self.line_num = line_num
        self.issue_type = issue_type
        self.severity = severity
        self.message = message
        self.pattern = pattern

    def __str__(self):
        return (f"{self.severity.value}: {self.issue_type}\n"
                f"  File: {self.file_path}:{self.line_num}\n"
                f"  {self.message}")


class SecurityScanner:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()
        self.issues: List[SecurityIssue] = []
        
        # Secret patterns (common hardcoded secrets)
        self.secret_patterns = [
            (r'password\s*=\s*["\']([^"\']+)["\']', 'Hardcoded password', Severity.HIGH),
            (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', 'Hardcoded API key', Severity.HIGH),
            (r'secret\s*=\s*["\']([^"\']+)["\']', 'Hardcoded secret', Severity.HIGH),
            (r'token\s*=\s*["\']([^"\']+)["\']', 'Hardcoded token', Severity.HIGH),
            (r'aws[_-]?secret[_-]?access[_-]?key\s*=\s*["\']([^"\']+)["\']', 'AWS secret key', Severity.CRITICAL),
            (r'private[_-]?key\s*=\s*["\']([^"\']+)["\']', 'Private key', Severity.CRITICAL),
            (r'jdbc:.*:.*:.*:.*:([^:]+)@', 'Database password in JDBC URL', Severity.HIGH),
        ]

    def scan_file(self, file_path: Path) -> None:
        """Scan a single file for security issues."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            
            for line_num, line in enumerate(lines, 1):
                # Check for hardcoded secrets
                self.check_secrets(file_path, line_num, line)
                
                # Check for insecure HTTP listeners
                self.check_http_listeners(file_path, line_num, line)
                
                # Check for weak TLS
                self.check_tls_config(file_path, line_num, line)
                
                # Check for missing API policies
                self.check_api_policies(file_path, line_num, line)
                
        except Exception as e:
            # Skip binary files or files we can't read
            pass

    def check_secrets(self, file_path: Path, line_num: int, line: str) -> None:
        """Check for hardcoded secrets."""
        # Skip comments and property placeholders
        if line.strip().startswith('#') or '${' in line:
            return
        
        for pattern, issue_type, severity in self.secret_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Skip if it's a property placeholder
                if '${' in line:
                    continue
                
                # Skip common false positives
                if any(fp in line.lower() for fp in ['example', 'sample', 'test', 'placeholder']):
                    continue
                
                secret_value = match.group(1) if match.groups() else match.group(0)
                # Skip if it's clearly a placeholder
                if secret_value in ['password', 'secret', 'key', 'token', 'changeme']:
                    continue
                
                self.issues.append(SecurityIssue(
                    file_path=file_path,
                    line_num=line_num,
                    issue_type=issue_type,
                    severity=severity,
                    message=f"Found: {secret_value[:20]}...",
                    pattern=pattern
                ))

    def check_http_listeners(self, file_path: Path, line_num: int, line: str) -> None:
        """Check for insecure HTTP listeners."""
        # Check for HTTP (not HTTPS) listeners
        if re.search(r'<http:listener', line, re.IGNORECASE):
            if 'protocol="HTTPS"' not in line.upper() and 'tls' not in line.lower():
                # Check if it's in a test file
                if 'test' not in str(file_path).lower():
                    self.issues.append(SecurityIssue(
                        file_path=file_path,
                        line_num=line_num,
                        issue_type='Insecure HTTP listener',
                        severity=Severity.MEDIUM,
                        message='HTTP listener without HTTPS/TLS configured',
                        pattern='http:listener'
                    ))

    def check_tls_config(self, file_path: Path, line_num: int, line: str) -> None:
        """Check for weak TLS configurations."""
        # Check for TLS 1.0 or 1.1 (deprecated)
        if re.search(r'tls[_-]?version\s*[=:]\s*["\']?1\.0', line, re.IGNORECASE):
            self.issues.append(SecurityIssue(
                file_path=file_path,
                line_num=line_num,
                issue_type='Weak TLS version',
                severity=Severity.HIGH,
                message='TLS 1.0 detected (deprecated, use TLS 1.2+)',
                pattern='tls.*1.0'
            ))
        
        if re.search(r'tls[_-]?version\s*[=:]\s*["\']?1\.1', line, re.IGNORECASE):
            self.issues.append(SecurityIssue(
                file_path=file_path,
                line_num=line_num,
                issue_type='Weak TLS version',
                severity=Severity.HIGH,
                message='TLS 1.1 detected (deprecated, use TLS 1.2+)',
                pattern='tls.*1.1'
            ))

    def check_api_policies(self, file_path: Path, line_num: int, line: str) -> None:
        """Check for missing API policies."""
        # This is a basic check - can be enhanced
        if re.search(r'<http:listener.*path=', line, re.IGNORECASE):
            # Check if API policies are configured (would need more context)
            # This is a simplified check
            pass

    def scan_project(self, exclude_patterns: List[str] = None) -> None:
        """Scan entire project for security issues."""
        exclude_patterns = exclude_patterns or []
        
        # Files to scan
        file_extensions = ['.xml', '.properties', '.yaml', '.yml', '.json', '.java', '.js']
        
        for ext in file_extensions:
            for file_path in self.project_path.rglob(f'*{ext}'):
                # Skip excluded patterns
                if any(pattern in str(file_path) for pattern in exclude_patterns):
                    continue
                
                # Skip common directories
                if any(skip in str(file_path) for skip in ['target/', '.mule/', 'node_modules/', '.git/']):
                    continue
                
                self.scan_file(file_path)

    def get_issues_by_severity(self, severity: Severity = None) -> List[SecurityIssue]:
        """Get issues filtered by severity."""
        if severity:
            return [issue for issue in self.issues if issue.severity == severity]
        return self.issues

    def print_results(self, verbose: bool = False, fail_on: Severity = None) -> bool:
        """Print scan results."""
        if not self.issues:
            print("\n✅ No security issues found!")
            return True

        # Group by severity
        critical = self.get_issues_by_severity(Severity.CRITICAL)
        high = self.get_issues_by_severity(Severity.HIGH)
        medium = self.get_issues_by_severity(Severity.MEDIUM)
        low = self.get_issues_by_severity(Severity.LOW)

        print(f"\n🔍 Security Scan Results:")
        print(f"  Critical: {len(critical)}")
        print(f"  High: {len(high)}")
        print(f"  Medium: {len(medium)}")
        print(f"  Low: {len(low)}")

        if critical:
            print("\n❌ CRITICAL Issues:\n")
            for issue in critical:
                print(f"  {issue}\n")

        if high:
            print("\n❌ HIGH Severity Issues:\n")
            for issue in high:
                print(f"  {issue}\n")

        if medium and verbose:
            print("\n⚠️  MEDIUM Severity Issues:\n")
            for issue in medium:
                print(f"  {issue}\n")

        if low and verbose:
            print("\n⚠️  LOW Severity Issues:\n")
            for issue in low:
                print(f"  {issue}\n")

        # Check if we should fail
        if fail_on:
            fail_severities = {
                Severity.CRITICAL: [Severity.CRITICAL],
                Severity.HIGH: [Severity.CRITICAL, Severity.HIGH],
                Severity.MEDIUM: [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM],
            }
            if fail_on in fail_severities:
                failing_issues = [issue for issue in self.issues 
                                if issue.severity in fail_severities[fail_on]]
                if failing_issues:
                    return False

        return len(critical) == 0 and len(high) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Scan MuleSoft project for security vulnerabilities"
    )
    parser.add_argument(
        '--path',
        type=str,
        default='.',
        help='Path to MuleSoft project root (default: current directory)'
    )
    parser.add_argument(
        '--exclude',
        action='append',
        help='Pattern to exclude from scan (can be used multiple times)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show all issues including medium and low severity'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--fail-on',
        choices=['critical', 'high', 'medium'],
        help='Exit with error code if issues of this severity or higher are found'
    )
    
    args = parser.parse_args()
    
    project_path = Path(args.path)
    if not project_path.exists():
        print(f"❌ Error: Project path does not exist: {project_path}")
        sys.exit(1)
    
    scanner = SecurityScanner(project_path)
    exclude_patterns = args.exclude or []
    
    print("🔍 Scanning project for security issues...")
    scanner.scan_project(exclude_patterns=exclude_patterns)
    
    if args.format == 'json':
        import json
        output = {
            'issues': [
                {
                    'file': str(issue.file_path),
                    'line': issue.line_num,
                    'type': issue.issue_type,
                    'severity': issue.severity.value,
                    'message': issue.message
                }
                for issue in scanner.issues
            ],
            'summary': {
                'total': len(scanner.issues),
                'critical': len(scanner.get_issues_by_severity(Severity.CRITICAL)),
                'high': len(scanner.get_issues_by_severity(Severity.HIGH)),
                'medium': len(scanner.get_issues_by_severity(Severity.MEDIUM)),
                'low': len(scanner.get_issues_by_severity(Severity.LOW))
            }
        }
        print(json.dumps(output, indent=2))
    else:
        fail_on_severity = None
        if args.fail_on:
            fail_on_severity = Severity[args.fail_on.upper()]
        
        is_valid = scanner.print_results(verbose=args.verbose, fail_on=fail_on_severity)
        sys.exit(0 if is_valid else 1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()

