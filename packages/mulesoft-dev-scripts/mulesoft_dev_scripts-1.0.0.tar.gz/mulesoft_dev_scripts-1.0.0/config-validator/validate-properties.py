#!/usr/bin/env python3
"""
MuleSoft Configuration Validator

Validates property placeholders, mule-artifact.json, and configuration files
to catch issues before deployment.
"""

import re
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Set, List, Tuple
from collections import defaultdict


class ConfigValidator:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path).resolve()
        self.properties: Dict[str, Path] = {}
        self.placeholders: Set[str] = set()
        self.placeholder_locations: Dict[str, List[Tuple[Path, int]]] = defaultdict(list)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def find_properties_files(self) -> None:
        """Find all .properties files in the project."""
        for props_file in self.project_path.rglob("*.properties"):
            try:
                for line_num, line in enumerate(props_file.read_text().splitlines(), 1):
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key = line.split("=", 1)[0].strip()
                        if key:
                            if key in self.properties:
                                self.warnings.append(
                                    f"Duplicate property '{key}' found in:\n"
                                    f"  - {self.properties[key]}\n"
                                    f"  - {props_file}"
                                )
                            self.properties[key] = props_file
            except Exception as e:
                self.errors.append(f"Error reading {props_file}: {e}")

    def find_placeholders(self) -> None:
        """Find all ${property.name} placeholders in XML files."""
        placeholder_pattern = re.compile(r'\$\{([^}]+)\}')
        
        for xml_file in self.project_path.rglob("*.xml"):
            try:
                text = xml_file.read_text()
                for match in placeholder_pattern.finditer(text):
                    placeholder = match.group(1)
                    self.placeholders.add(placeholder)
                    # Calculate line number
                    line_num = text[:match.start()].count('\n') + 1
                    self.placeholder_locations[placeholder].append((xml_file, line_num))
            except Exception as e:
                self.errors.append(f"Error reading {xml_file}: {e}")

    def validate_placeholders(self) -> None:
        """Check if all placeholders have corresponding properties."""
        missing = self.placeholders - self.properties.keys()
        
        if missing:
            for placeholder in sorted(missing):
                locations = self.placeholder_locations[placeholder]
                location_str = "\n".join(f"  - {path}:{line}" for path, line in locations)
                self.errors.append(
                    f"Missing property: {placeholder}\n"
                    f"Referenced in:\n{location_str}"
                )

    def validate_mule_artifact(self) -> None:
        """Validate mule-artifact.json file."""
        artifact_file = self.project_path / "mule-artifact.json"
        
        if not artifact_file.exists():
            self.warnings.append("mule-artifact.json not found (optional for some projects)")
            return

        try:
            with open(artifact_file, 'r') as f:
                artifact = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in mule-artifact.json: {e}")
            return
        except Exception as e:
            self.errors.append(f"Error reading mule-artifact.json: {e}")
            return

        # Required fields
        required_fields = {
            'minMuleVersion': 'Minimum Mule runtime version',
            'name': 'Application name'
        }

        for field, description in required_fields.items():
            if field not in artifact or not artifact[field]:
                self.errors.append(
                    f"Invalid mule-artifact.json:\n"
                    f"  - Missing required field: {field} ({description})"
                )

        # Validate minMuleVersion format
        if 'minMuleVersion' in artifact:
            version = artifact['minMuleVersion']
            if not re.match(r'^\d+\.\d+\.\d+', version):
                self.warnings.append(
                    f"minMuleVersion format may be invalid: {version}\n"
                    f"  Expected format: X.Y.Z (e.g., 4.5.0)"
                )

    def find_unused_properties(self) -> None:
        """Find properties that are defined but never used."""
        unused = set(self.properties.keys()) - self.placeholders
        
        if unused:
            for prop in sorted(unused):
                self.warnings.append(
                    f"Unused property: {prop}\n"
                    f"  Defined in: {self.properties[prop]}"
                )

    def validate(self) -> bool:
        """Run all validation checks."""
        print("🔍 Scanning project...")
        self.find_properties_files()
        self.find_placeholders()
        
        print("✅ Validating placeholders...")
        self.validate_placeholders()
        
        print("✅ Validating mule-artifact.json...")
        self.validate_mule_artifact()
        
        print("✅ Checking for unused properties...")
        self.find_unused_properties()
        
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
        
        if not self.errors:
            print("\n✅ All validations passed!")
            if self.warnings and not verbose:
                print(f"⚠️  {len(self.warnings)} warning(s) found (use --verbose to see)")
        else:
            print(f"\n❌ Found {len(self.errors)} error(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Validate MuleSoft project configuration files"
    )
    parser.add_argument(
        '--project-path',
        type=str,
        default='.',
        help='Path to MuleSoft project root (default: current directory)'
    )
    parser.add_argument(
        '--verbose',
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
    
    validator = ConfigValidator(project_path)
    is_valid = validator.validate()
    
    if args.format == 'json':
        import json as json_module
        output = {
            'valid': is_valid,
            'errors': validator.errors,
            'warnings': validator.warnings,
            'stats': {
                'properties_found': len(validator.properties),
                'placeholders_found': len(validator.placeholders),
                'errors_count': len(validator.errors),
                'warnings_count': len(validator.warnings)
            }
        }
        print(json_module.dumps(output, indent=2))
    else:
        validator.print_results(verbose=args.verbose)
    
    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()

