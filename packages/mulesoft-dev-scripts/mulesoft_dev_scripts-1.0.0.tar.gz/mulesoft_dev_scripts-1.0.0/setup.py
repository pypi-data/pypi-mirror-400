#!/usr/bin/env python3
"""
Setup script for MuleSoft Developer Scripts
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="mulesoft-dev-scripts",
    version="1.0.0",
    description="Open-source scripts and tools to solve common MuleSoft development and operations problems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Upendra Manike",
    author_email="",
    url="https://github.com/upendra-manike/mulesoft-dev-scripts",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    py_modules=[],
    scripts=[
        "config-validator/validate-properties.py",
        "log-analyzer/analyze-logs.py",
        "security-scanner/secret-scan.py",
        "api-validator/raml-vs-flow-check.py",
        "munit-analyzer/munit-coverage.py",
    ],
    install_requires=[],
    extras_require={
        "dev": [
            "flake8",
            "pylint",
        ],
        "yaml": [
            "pyyaml",
        ],
    },
    entry_points={
        "console_scripts": [
            "mule-validate-config=config_validator.validate_properties:main",
            "mule-analyze-logs=log_analyzer.analyze_logs:main",
            "mule-scan-security=security_scanner.secret_scan:main",
            "mule-validate-api=api_validator.raml_vs_flow_check:main",
            "mule-analyze-munit=munit_analyzer.munit_coverage:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

