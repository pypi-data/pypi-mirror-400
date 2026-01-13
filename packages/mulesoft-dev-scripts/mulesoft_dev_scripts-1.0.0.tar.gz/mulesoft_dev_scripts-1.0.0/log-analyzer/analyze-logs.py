#!/usr/bin/env python3
"""
MuleSoft Log Analyzer

Analyzes MuleSoft application logs to identify common issues,
missing correlation IDs, log flooding, and error patterns.
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
from datetime import datetime


class LogAnalyzer:
    def __init__(self):
        self.log_entries: List[Dict] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict = {
            'total_lines': 0,
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'debug_count': 0,
            'correlation_ids': set(),
            'error_types': Counter(),
            'log_patterns': Counter()
        }

    def parse_log_file(self, log_path: Path) -> None:
        """Parse a MuleSoft log file."""
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    self.stats['total_lines'] += 1
                    entry = self.parse_log_line(line, line_num)
                    if entry:
                        self.log_entries.append(entry)
        except Exception as e:
            self.errors.append(f"Error reading {log_path}: {e}")

    def parse_log_line(self, line: str, line_num: int) -> Dict:
        """Parse a single log line."""
        # MuleSoft log format: TIMESTAMP LEVEL [THREAD] LOGGER - MESSAGE
        # Example: 2024-01-15 10:30:45.123 INFO  [http-listener-1] org.mule.runtime.core - Processing request
        
        entry = {
            'line_num': line_num,
            'raw': line,
            'timestamp': None,
            'level': None,
            'thread': None,
            'logger': None,
            'message': line,
            'correlation_id': None,
            'is_error': False
        }

        # Try to extract timestamp (various formats)
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})',
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    entry['timestamp'] = datetime.strptime(match.group(1), 
                        '%Y-%m-%d %H:%M:%S.%f' if '.' in match.group(1) else '%Y-%m-%d %H:%M:%S')
                except:
                    pass
                break

        # Extract log level
        level_match = re.search(r'\b(ERROR|WARN|INFO|DEBUG|TRACE)\b', line)
        if level_match:
            entry['level'] = level_match.group(1)
            if entry['level'] == 'ERROR':
                entry['is_error'] = True
                self.stats['error_count'] += 1
            elif entry['level'] == 'WARN':
                self.stats['warning_count'] += 1
            elif entry['level'] == 'INFO':
                self.stats['info_count'] += 1
            elif entry['level'] == 'DEBUG':
                self.stats['debug_count'] += 1

        # Extract correlation ID (common patterns)
        correlation_patterns = [
            r'correlationId[=:]\s*([a-f0-9-]+)',
            r'\[([a-f0-9-]{36})\]',  # UUID format
            r'correlation-id[=:]\s*([a-f0-9-]+)',
        ]
        
        for pattern in correlation_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                entry['correlation_id'] = match.group(1)
                self.stats['correlation_ids'].add(match.group(1))
                break

        # Extract thread name
        thread_match = re.search(r'\[([^\]]+)\]', line)
        if thread_match:
            entry['thread'] = thread_match.group(1)

        # Extract logger name
        logger_match = re.search(r'(\S+\.\S+) -', line)
        if logger_match:
            entry['logger'] = logger_match.group(1)

        return entry

    def check_correlation_ids(self) -> None:
        """Check for missing correlation IDs."""
        entries_with_correlation = sum(1 for e in self.log_entries if e.get('correlation_id'))
        total_entries = len(self.log_entries)
        
        if total_entries == 0:
            return

        coverage = (entries_with_correlation / total_entries) * 100
        
        if coverage < 80:
            self.warnings.append(
                f"Missing correlation IDs in {100 - coverage:.1f}% of log entries\n"
                f"  Coverage: {coverage:.1f}% ({entries_with_correlation}/{total_entries})\n"
                f"  Recommendation: Enable correlation IDs in all flows"
            )
        else:
            self.stats['correlation_coverage'] = coverage

    def check_errors(self) -> None:
        """Analyze error patterns."""
        error_entries = [e for e in self.log_entries if e.get('is_error')]
        
        if not error_entries:
            return

        error_rate = (len(error_entries) / len(self.log_entries)) * 100
        
        # Extract error types
        error_patterns = [
            (r'HTTP:(\w+)', 'HTTP'),
            (r'CONNECTIVITY', 'CONNECTIVITY'),
            (r'TIMEOUT', 'TIMEOUT'),
            (r'VALIDATION', 'VALIDATION'),
            (r'EXPRESSION', 'EXPRESSION'),
            (r'TRANSFORMATION', 'TRANSFORMATION'),
        ]

        for entry in error_entries:
            message = entry.get('message', '')
            for pattern, error_type in error_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    self.stats['error_types'][error_type] += 1
                    break

        if error_rate > 5:
            error_summary = ', '.join([f"{k} ({v})" for k, v in 
                                     self.stats['error_types'].most_common(5)])
            self.errors.append(
                f"High error rate: {error_rate:.1f}%\n"
                f"  Errors found: {len(error_entries)}\n"
                f"  Most common: {error_summary if error_summary else 'Various'}"
            )
        elif error_rate > 0:
            self.stats['error_rate'] = error_rate

    def check_log_flooding(self) -> None:
        """Detect log flooding patterns."""
        # Group by logger and message pattern
        logger_counts = Counter(e.get('logger', 'unknown') for e in self.log_entries)
        message_patterns = Counter()

        for entry in self.log_entries:
            # Extract message pattern (simplified)
            message = entry.get('message', '')
            # Remove variable parts
            pattern = re.sub(r'\d+', 'N', message)
            pattern = re.sub(r'[a-f0-9-]{36}', 'UUID', pattern)
            message_patterns[pattern[:100]] += 1

        # Check for excessive logging
        threshold = 1000
        for pattern, count in message_patterns.most_common(10):
            if count > threshold:
                self.warnings.append(
                    f"Log flooding detected\n"
                    f"  Pattern: \"{pattern[:50]}...\" appears {count:,} times\n"
                    f"  Recommendation: Change log level to INFO or WARN"
                )

        # Check for excessive DEBUG logs
        if self.stats['debug_count'] > self.stats['info_count'] * 2:
            self.warnings.append(
                f"Excessive DEBUG logging detected\n"
                f"  DEBUG: {self.stats['debug_count']:,} entries\n"
                f"  INFO: {self.stats['info_count']:,} entries\n"
                f"  Recommendation: Set log level to INFO in log4j2.xml"
            )

    def check_log_levels(self) -> None:
        """Check log level distribution."""
        total = sum([
            self.stats['error_count'],
            self.stats['warning_count'],
            self.stats['info_count'],
            self.stats['debug_count']
        ])
        
        if total == 0:
            return

        if self.stats['debug_count'] / total > 0.7:
            self.warnings.append(
                "Log level may be too verbose\n"
                "  Consider setting root logger to INFO level"
            )

    def analyze(self) -> Dict:
        """Run all analysis checks."""
        self.check_correlation_ids()
        self.check_errors()
        self.check_log_flooding()
        self.check_log_levels()
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'stats': self.stats
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

        print(f"\n📊 Statistics:")
        print(f"  Total log entries: {self.stats['total_lines']:,}")
        print(f"  Errors: {self.stats['error_count']:,}")
        print(f"  Warnings: {self.stats['warning_count']:,}")
        print(f"  Correlation IDs: {len(self.stats['correlation_ids'])} unique")
        
        if 'correlation_coverage' in self.stats:
            print(f"  Correlation coverage: {self.stats['correlation_coverage']:.1f}%")
        
        if 'error_rate' in self.stats:
            print(f"  Error rate: {self.stats['error_rate']:.1f}%")

        if not self.errors:
            print("\n✅ Log analysis complete")
        else:
            print(f"\n❌ Found {len(self.errors)} issue(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze MuleSoft application logs"
    )
    parser.add_argument(
        'log_files',
        nargs='+',
        help='Log file(s) to analyze'
    )
    parser.add_argument(
        '--check-correlation',
        action='store_true',
        help='Check for missing correlation IDs'
    )
    parser.add_argument(
        '--check-errors',
        action='store_true',
        help='Analyze error patterns'
    )
    parser.add_argument(
        '--check-flooding',
        action='store_true',
        help='Detect log flooding'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer()
    
    # Parse all log files
    for log_file in args.log_files:
        log_path = Path(log_file)
        if not log_path.exists():
            print(f"❌ Error: Log file does not exist: {log_path}")
            sys.exit(1)
        print(f"📖 Reading {log_path}...")
        analyzer.parse_log_file(log_path)
    
    # Run analysis
    print("🔍 Analyzing logs...")
    results = analyzer.analyze()
    
    if args.format == 'json':
        import json
        print(json.dumps(results, indent=2, default=str))
    else:
        analyzer.print_results(verbose=args.verbose)
    
    sys.exit(0 if results['valid'] else 1)


if __name__ == '__main__':
    main()

