#!/usr/bin/env python3
"""
MUnit Analyzer

Analyzes MUnit test coverage, execution time, and test quality in MuleSoft projects.
"""

import re
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime


class MUnitAnalyzer:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.test_files: List[Path] = []
        self.flows: List[Dict] = []
        self.tests: List[Dict] = []
        self.stats: Dict = {
            'total_tests': 0,
            'total_flows': 0,
            'covered_flows': set(),
            'uncovered_flows': set(),
            'test_execution_times': []
        }

    def find_flows(self) -> None:
        """Find all Mule flows in the project."""
        for xml_file in self.project_path.rglob("*.xml"):
            # Skip test files
            if 'test' in str(xml_file).lower() and 'munit' in str(xml_file).lower():
                continue
            
            try:
                content = xml_file.read_text(encoding='utf-8', errors='ignore')
                self.parse_flows(xml_file, content)
            except Exception:
                pass

    def parse_flows(self, xml_file: Path, content: str) -> None:
        """Parse flows from XML content."""
        # Pattern for flow definition
        flow_pattern = r'<flow\s+name="([^"]+)"'
        
        for match in re.finditer(flow_pattern, content, re.IGNORECASE):
            flow_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            # Check if flow has error handling
            flow_content = content[match.start():match.end() + 1000]  # Get flow content
            has_error_handling = 'error-handler' in flow_content.lower() or 'on-error-continue' in flow_content.lower()
            
            self.flows.append({
                'name': flow_name,
                'file': xml_file,
                'line': line_num,
                'has_error_handling': has_error_handling
            })
            self.stats['total_flows'] += 1

    def find_munit_tests(self) -> None:
        """Find all MUnit test files."""
        for xml_file in self.project_path.rglob("*.xml"):
            if 'test' in str(xml_file).lower() or 'munit' in str(xml_file).lower():
                try:
                    content = xml_file.read_text(encoding='utf-8', errors='ignore')
                    if re.search(r'munit', content, re.IGNORECASE):
                        self.test_files.append(xml_file)
                        self.parse_munit_tests(xml_file, content)
                except Exception:
                    pass

    def parse_munit_tests(self, xml_file: Path, content: str) -> None:
        """Parse MUnit tests from XML content."""
        # Pattern for test suite
        suite_pattern = r'<munit:test\s+name="([^"]+)"'
        
        for match in re.finditer(suite_pattern, content, re.IGNORECASE):
            test_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            # Extract test content
            test_content = content[match.start():match.end() + 2000]
            
            # Check for mocks
            has_mocks = 'mock' in test_content.lower() or 'munit:mock' in test_content.lower()
            
            # Check for assertions
            has_assertions = 'assert' in test_content.lower() or 'munit:assert' in test_content.lower()
            
            # Check for flow reference
            flow_ref_match = re.search(r'flow-ref\s+name="([^"]+)"', test_content, re.IGNORECASE)
            flow_ref = flow_ref_match.group(1) if flow_ref_match else None
            
            test = {
                'name': test_name,
                'file': xml_file,
                'line': line_num,
                'has_mocks': has_mocks,
                'has_assertions': has_assertions,
                'flow_ref': flow_ref
            }
            
            self.tests.append(test)
            self.stats['total_tests'] += 1
            
            if flow_ref:
                self.stats['covered_flows'].add(flow_ref)

    def analyze_coverage(self) -> None:
        """Analyze test coverage for flows."""
        flow_names = {flow['name'] for flow in self.flows}
        self.stats['uncovered_flows'] = flow_names - self.stats['covered_flows']
        
        if not self.flows:
            self.warnings.append("No flows found in project")
            return

        if not self.tests:
            self.errors.append("No MUnit tests found")
            return

        coverage_percent = (len(self.stats['covered_flows']) / len(flow_names) * 100) if flow_names else 0
        
        if coverage_percent < 50:
            self.errors.append(
                f"Low test coverage: {coverage_percent:.1f}%\n"
                f"  Covered flows: {len(self.stats['covered_flows'])}\n"
                f"  Total flows: {len(flow_names)}\n"
                f"  Recommendation: Add tests for uncovered flows"
            )
        elif coverage_percent < 80:
            self.warnings.append(
                f"Test coverage: {coverage_percent:.1f}%\n"
                f"  Uncovered flows: {len(self.stats['uncovered_flows'])}\n"
                f"  Recommendation: Aim for 80%+ coverage"
            )
        else:
            self.stats['coverage_percent'] = coverage_percent

    def analyze_test_quality(self) -> None:
        """Analyze quality of MUnit tests."""
        tests_without_assertions = [t for t in self.tests if not t['has_assertions']]
        tests_without_mocks = [t for t in self.tests if not t['has_mocks']]
        
        if tests_without_assertions:
            self.warnings.append(
                f"Tests without assertions: {len(tests_without_assertions)}\n"
                f"  Recommendation: Add assertions to validate test results"
            )

        # Check for flows without error handling that are tested
        flows_without_error_handling = [f for f in self.flows if not f['has_error_handling']]
        if flows_without_error_handling:
            uncovered_names = [f['name'] for f in flows_without_error_handling 
                              if f['name'] in self.stats['covered_flows']]
            if uncovered_names:
                self.warnings.append(
                    f"Tested flows without error handling: {len(uncovered_names)}\n"
                    f"  Recommendation: Add error handling to flows"
                )

    def check_test_structure(self) -> None:
        """Check MUnit test structure and best practices."""
        for test in self.tests:
            issues = []
            
            if not test['has_assertions']:
                issues.append("missing assertions")
            
            if not test['has_mocks'] and test['flow_ref']:
                # External dependencies might need mocks
                issues.append("consider adding mocks for external dependencies")
            
            if issues:
                self.warnings.append(
                    f"Test '{test['name']}' issues:\n"
                    f"  File: {test['file']}:{test['line']}\n"
                    f"  {', '.join(issues)}"
                )

    def analyze(self) -> Dict:
        """Run all analysis checks."""
        print("🔍 Finding flows...")
        self.find_flows()
        
        print("🔍 Finding MUnit tests...")
        self.find_munit_tests()
        
        print("✅ Analyzing coverage...")
        self.analyze_coverage()
        
        print("✅ Analyzing test quality...")
        self.analyze_test_quality()
        
        print("✅ Checking test structure...")
        self.check_test_structure()
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'stats': {
                **self.stats,
                'uncovered_flows': list(self.stats['uncovered_flows']),
                'covered_flows': list(self.stats['covered_flows'])
            }
        }

    def print_results(self, verbose: bool = False) -> None:
        """Print analysis results."""
        if self.errors:
            print("\n❌ Issues Found:\n")
            for error in self.errors:
                print(f"  {error}\n")

        if self.warnings and verbose:
            print("\n⚠️  Warnings:\n")
            for warning in self.warnings:
                print(f"  {warning}\n")

        print(f"\n📊 MUnit Analysis Results:")
        print(f"  Total flows: {self.stats['total_flows']}")
        print(f"  Total tests: {self.stats['total_tests']}")
        
        if 'coverage_percent' in self.stats:
            print(f"  Coverage: {self.stats['coverage_percent']:.1f}%")
        else:
            if self.stats['total_flows'] > 0:
                coverage = len(self.stats['covered_flows']) / self.stats['total_flows'] * 100
                print(f"  Coverage: {coverage:.1f}%")
        
        print(f"  Covered flows: {len(self.stats['covered_flows'])}")
        print(f"  Uncovered flows: {len(self.stats['uncovered_flows'])}")
        
        if self.stats['uncovered_flows']:
            print(f"\n  Uncovered flows:")
            for flow in sorted(list(self.stats['uncovered_flows']))[:10]:  # Show first 10
                print(f"    - {flow}")
            if len(self.stats['uncovered_flows']) > 10:
                print(f"    ... and {len(self.stats['uncovered_flows']) - 10} more")

        if not self.errors:
            print("\n✅ MUnit analysis complete")
        else:
            print(f"\n❌ Found {len(self.errors)} issue(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze MUnit test coverage and quality"
    )
    parser.add_argument(
        '--project-path',
        type=str,
        default='.',
        help='Path to MuleSoft project root (default: current directory)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show warnings in addition to errors'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    project_path = Path(args.project_path)
    if not project_path.exists():
        print(f"❌ Error: Project path does not exist: {project_path}")
        sys.exit(1)
    
    analyzer = MUnitAnalyzer(project_path)
    results = analyzer.analyze()
    
    if args.format == 'json':
        print(json.dumps(results, indent=2, default=str))
    else:
        analyzer.print_results(verbose=args.verbose)
    
    sys.exit(0 if results['valid'] else 1)


if __name__ == '__main__':
    main()

