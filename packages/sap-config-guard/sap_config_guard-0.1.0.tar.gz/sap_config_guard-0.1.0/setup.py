"""
Setup script for sap-config-guard
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="sap-config-guard",
    version="0.1.0",
    author="SAP Community",
    author_email="",
    description="Fail-fast configuration validation & environment drift detection for SAP landscapes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/upendra-manike/sap-config-guard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sap-config-guard=sap_config_guard.cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sap_config_guard": ["rules/*.yaml"],
    },
)

