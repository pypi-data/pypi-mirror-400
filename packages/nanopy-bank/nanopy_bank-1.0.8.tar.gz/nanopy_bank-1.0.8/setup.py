#!/usr/bin/env python3
"""
NanoPy Bank - Online Banking System with SEPA/ISO20022 XML
"""

from setuptools import setup, find_packages

setup(
    name="nanopy-bank",
    version="1.0.8",
    author="NanoPy Team",
    author_email="dev@nanopy.chain",
    description="Online Banking System with Streamlit UI and SEPA XML support",
    long_description="""# NanoPy Bank

Online Banking System built with Python, Streamlit and shadcn-ui.

## Features

- Account Management (IBAN, BIC)
- Transaction History
- SEPA/ISO20022 XML Import/Export
- Real-time Balance Updates
- Multi-currency Support
- PDF Statements
- API for integrations

## Installation

```bash
pip install nanopy-bank
nanopy-bank serve
```

## Usage

```bash
# Start the banking UI
nanopy-bank serve --port 8501

# Generate SEPA XML
nanopy-bank export-sepa --account FR7612345678901234567890123
```
""",
    long_description_content_type="text/markdown",
    url="https://github.com/Web3-League/nanopy-bank",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.28.0",
        "streamlit-shadcn-ui>=0.1.0",
        "streamlit-extras>=0.3.0",  # Icons, animations, components
        "streamlit-option-menu>=0.3.0",  # Better navigation menus
        "lxml>=4.9.0",
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "aiohttp>=3.8.0",
        "python-dateutil>=2.8.0",
        "schwifty>=2023.0.0",  # IBAN/BIC validation
        "reportlab>=4.0.0",  # PDF generation
        "qrcode>=7.4.0",
        "pillow>=10.0.0",
        "click>=8.0.0",
    ],
    include_package_data=True,
    package_data={
        "nanopy_bank": ["static/*", "templates/*"],
    },
    entry_points={
        "console_scripts": [
            "nanopy-bank=nanopy_bank.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="banking sepa xml iso20022 streamlit fintech",
)
