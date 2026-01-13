"""
CHRONOS - Unified Quantum Security Platform
Setup configuration for package distribution.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip()
        for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="chronos-security",
    version="1.1.1",
    author="CHRONOS Security Team",
    author_email="team@chronos-security.io",
    description="Unified Security Fusion Platform - Threat Intelligence, Vulnerability Management, IR Playbooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/CHRONOS",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/CHRONOS/issues",
        "Documentation": "https://chronos-security.io/docs",
        "Source Code": "https://github.com/yourusername/CHRONOS",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples", "venv", "venv.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering",
        "Typing :: Typed",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pyyaml>=6.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "cryptography>=41.0.0",
        "httpx>=0.25.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "matplotlib>=3.8.0",
        "jinja2>=3.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.5.0",
            "pre-commit>=3.5.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.4.0",
        ],
        "quantum": [
            "pycryptodome>=3.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "chronos=chronos.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "security",
        "threat-intelligence",
        "vulnerability-management",
        "phishing-detection",
        "incident-response",
        "log-analysis",
        "cve",
        "epss",
        "cybersecurity",
        "infosec",
    ],
)
