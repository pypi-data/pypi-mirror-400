#!/usr/bin/env python3
"""
MuleSoft API Validator

Validates API configurations, listeners, TLS settings, and contract mismatches
in MuleSoft projects. Checks for RAML/OpenAPI vs implementation mismatches.
"""

import re
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class APIValidator:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.api_specs: Dict[str, Dict] = {}
        self.flows: Dict[str, Dict] = {}
        self.listeners: List[Dict] = []

    def find_api_specs(self) -> None:
        """Find RAML and OpenAPI specification files."""
        for spec_file in self.project_path.rglob("*.raml"):
            try:
                self.parse_raml(spec_file)
            except Exception as e:
                self.warnings.append(f"Could not parse RAML file {spec_file}: {e}")

        for spec_file in self.project_path.rglob("*.yaml"):
            if 'api' in spec_file.name.lower() or 'openapi' in spec_file.name.lower():
                try:
                    self.parse_openapi(spec_file)
                except Exception as e:
                    self.warnings.append(f"Could not parse OpenAPI file {spec_file}: {e}")

        for spec_file in self.project_path.rglob("openapi.json"):
            try:
                self.parse_openapi(spec_file)
            except Exception as e:
                self.warnings.append(f"Could not parse OpenAPI file {spec_file}: {e}")

    def parse_raml(self, raml_file: Path) -> None:
        """Parse RAML file to extract API information."""
        content = raml_file.read_text(encoding='utf-8', errors='ignore')
        
        # Extract basic info
        title_match = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
        version_match = re.search(r'^version:\s*(.+)$', content, re.MULTILINE)
        base_uri_match = re.search(r'^baseUri:\s*(.+)$', content, re.MULTILINE)
        
        # Extract resources (endpoints)
        resources = []
        resource_pattern = r'^\s*/([^\s:]+):'
        for match in re.finditer(resource_pattern, content, re.MULTILINE):
            resources.append(match.group(1))
        
        # Extract methods
        methods = []
        method_pattern = r'^\s+(get|post|put|delete|patch):'
        for match in re.finditer(method_pattern, content, re.MULTILINE | re.IGNORECASE):
            methods.append(match.group(1).upper())

        spec_name = raml_file.stem
        self.api_specs[spec_name] = {
            'file': raml_file,
            'type': 'RAML',
            'title': title_match.group(1) if title_match else None,
            'version': version_match.group(1) if version_match else None,
            'baseUri': base_uri_match.group(1) if base_uri_match else None,
            'resources': resources,
            'methods': methods
        }

    def parse_openapi(self, spec_file: Path) -> None:
        """Parse OpenAPI/Swagger file."""
        content = spec_file.read_text(encoding='utf-8', errors='ignore')
        
        try:
            if spec_file.suffix == '.json':
                spec = json.loads(content)
            else:
                import yaml
                spec = yaml.safe_load(content)
        except Exception as e:
            self.warnings.append(f"Could not parse {spec_file}: {e}")
            return

        paths = spec.get('paths', {})
        resources = list(paths.keys())
        methods = []
        for path, methods_dict in paths.items():
            methods.extend([m.upper() for m in methods_dict.keys() if m.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']])

        spec_name = spec_file.stem
        self.api_specs[spec_name] = {
            'file': spec_file,
            'type': 'OpenAPI',
            'title': spec.get('info', {}).get('title'),
            'version': spec.get('info', {}).get('version'),
            'baseUri': None,
            'resources': resources,
            'methods': list(set(methods))
        }

    def find_http_listeners(self) -> None:
        """Find HTTP listeners in Mule XML files."""
        for xml_file in self.project_path.rglob("*.xml"):
            try:
                content = xml_file.read_text(encoding='utf-8', errors='ignore')
                self.parse_http_listeners(xml_file, content)
            except Exception as e:
                pass  # Skip files we can't read

    def parse_http_listeners(self, xml_file: Path, content: str) -> None:
        """Parse HTTP listeners from XML content."""
        # Pattern for http:listener
        listener_pattern = r'<http:listener\s+([^>]+)>'
        
        for match in re.finditer(listener_pattern, content, re.IGNORECASE):
            attrs_str = match.group(1)
            
            # Extract attributes
            config_ref = re.search(r'config-ref="([^"]+)"', attrs_str)
            path = re.search(r'path="([^"]+)"', attrs_str)
            allowedMethods = re.search(r'allowedMethods="([^"]+)"', attrs_str)
            protocol = re.search(r'protocol="([^"]+)"', attrs_str)
            
            # Extract line number
            line_num = content[:match.start()].count('\n') + 1
            
            listener = {
                'file': xml_file,
                'line': line_num,
                'config_ref': config_ref.group(1) if config_ref else None,
                'path': path.group(1) if path else None,
                'methods': allowedMethods.group(1).split(',') if allowedMethods else [],
                'protocol': protocol.group(1) if protocol else 'HTTP'
            }
            
            self.listeners.append(listener)

    def validate_listeners(self) -> None:
        """Validate HTTP listener configurations."""
        for listener in self.listeners:
            # Check for insecure HTTP
            if listener['protocol'].upper() == 'HTTP':
                # Check if it's in a test file
                if 'test' not in str(listener['file']).lower():
                    self.warnings.append(
                        f"Insecure HTTP listener (not HTTPS)\n"
                        f"  File: {listener['file']}:{listener['line']}\n"
                        f"  Path: {listener['path']}\n"
                        f"  Recommendation: Use HTTPS or configure TLS"
                    )

            # Check for missing path
            if not listener['path']:
                self.errors.append(
                    f"HTTP listener missing path attribute\n"
                    f"  File: {listener['file']}:{listener['line']}"
                )

    def validate_api_contracts(self) -> None:
        """Validate API contracts match implementations."""
        if not self.api_specs:
            self.warnings.append("No API specification files (RAML/OpenAPI) found")
            return

        if not self.listeners:
            self.warnings.append("No HTTP listeners found in flows")
            return

        # Extract paths from listeners
        listener_paths = {listener['path'] for listener in self.listeners if listener['path']}
        
        # Check each API spec
        for spec_name, spec in self.api_specs.items():
            spec_resources = spec.get('resources', [])
            
            # Normalize paths for comparison
            spec_paths = {self.normalize_path(r) for r in spec_resources}
            listener_paths_normalized = {self.normalize_path(p) for p in listener_paths}
            
            # Find missing implementations
            missing_impl = spec_paths - listener_paths_normalized
            if missing_impl:
                self.errors.append(
                    f"API contract mismatch: {spec_name}\n"
                    f"  Specified in {spec['type']} but not implemented:\n"
                    f"  {', '.join(missing_impl)}"
                )

            # Find extra implementations (not in spec)
            extra_impl = listener_paths_normalized - spec_paths
            if extra_impl and len(spec_paths) > 0:
                self.warnings.append(
                    f"Extra endpoints not in API spec: {spec_name}\n"
                    f"  Implemented but not in {spec['type']}:\n"
                    f"  {', '.join(extra_impl)}"
                )

    def normalize_path(self, path: str) -> str:
        """Normalize API path for comparison."""
        # Remove leading/trailing slashes, convert to lowercase
        path = path.strip('/').lower()
        # Replace path parameters {id} with :id or remove
        path = re.sub(r'\{[^}]+\}', '*', path)
        return path

    def check_timeouts(self) -> None:
        """Check for HTTP timeout configurations."""
        for xml_file in self.project_path.rglob("*.xml"):
            try:
                content = xml_file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for HTTP request configurations
                if re.search(r'<http:request', content, re.IGNORECASE):
                    # Check for timeout settings
                    if not re.search(r'responseTimeout', content, re.IGNORECASE):
                        # This is just a warning, not all requests need explicit timeouts
                        pass
                    
                    # Check for very long timeouts
                    timeout_match = re.search(r'responseTimeout="(\d+)"', content, re.IGNORECASE)
                    if timeout_match:
                        timeout_ms = int(timeout_match.group(1))
                        if timeout_ms > 60000:  # More than 60 seconds
                            line_num = content[:timeout_match.start()].count('\n') + 1
                            self.warnings.append(
                                f"Very long HTTP timeout: {timeout_ms}ms\n"
                                f"  File: {xml_file}:{line_num}\n"
                                f"  Recommendation: Consider shorter timeout with retry strategy"
                            )
            except Exception:
                pass

    def check_cors(self) -> None:
        """Check for CORS configuration."""
        cors_found = False
        for xml_file in self.project_path.rglob("*.xml"):
            try:
                content = xml_file.read_text(encoding='utf-8', errors='ignore')
                if re.search(r'cors', content, re.IGNORECASE):
                    cors_found = True
                    break
            except Exception:
                pass

        if not cors_found and self.listeners:
            self.warnings.append(
                "No CORS configuration found\n"
                "  If your API is accessed from browsers, consider adding CORS headers"
            )

    def validate(self) -> bool:
        """Run all validation checks."""
        print("🔍 Scanning for API specifications...")
        self.find_api_specs()
        
        print("🔍 Scanning for HTTP listeners...")
        self.find_http_listeners()
        
        print("✅ Validating listeners...")
        self.validate_listeners()
        
        print("✅ Validating API contracts...")
        self.validate_api_contracts()
        
        print("✅ Checking timeouts...")
        self.check_timeouts()
        
        print("✅ Checking CORS...")
        self.check_cors()
        
        return len(self.errors) == 0

    def print_results(self, verbose: bool = False) -> None:
        """Print validation results."""
        if self.errors:
            print("\n❌ Validation Errors:\n")
            for error in self.errors:
                print(f"  {error}\n")

        if self.warnings and verbose:
            print("\n⚠️  Warnings:\n")
            for warning in self.warnings:
                print(f"  {warning}\n")

        # Summary
        print(f"\n📊 Summary:")
        print(f"  API Specifications: {len(self.api_specs)}")
        print(f"  HTTP Listeners: {len(self.listeners)}")
        
        if self.api_specs:
            for spec_name, spec in self.api_specs.items():
                print(f"    - {spec_name} ({spec['type']}): {len(spec.get('resources', []))} endpoints")

        if not self.errors:
            print("\n✅ API validation passed!")
            if self.warnings and not verbose:
                print(f"⚠️  {len(self.warnings)} warning(s) found (use --verbose to see)")
        else:
            print(f"\n❌ Found {len(self.errors)} error(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Validate MuleSoft API configurations and contracts"
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
    
    validator = APIValidator(project_path)
    is_valid = validator.validate()
    
    if args.format == 'json':
        output = {
            'valid': is_valid,
            'errors': validator.errors,
            'warnings': validator.warnings,
            'stats': {
                'api_specs': len(validator.api_specs),
                'listeners': len(validator.listeners),
                'errors_count': len(validator.errors),
                'warnings_count': len(validator.warnings)
            }
        }
        print(json.dumps(output, indent=2, default=str))
    else:
        validator.print_results(verbose=args.verbose)
    
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()

