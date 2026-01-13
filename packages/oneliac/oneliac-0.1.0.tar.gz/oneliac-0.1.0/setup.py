# Copyright 2025 Raza Ahmad. Licensed under Apache 2.0.

"""
Setup script for Healthcare Agents Python SDK
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Healthcare Agents Python SDK - Privacy-preserving healthcare API client"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['aiohttp>=3.9.0']

setup(
    name="oneliac",
    version="0.1.0",
    author="Raza Ahmad",
    author_email="raza@healthcare-agents.com",
    description="Python SDK for Privacy-Preserving Healthcare Agents API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/razaahmad9222/oneliac-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords=[
        "healthcare", "privacy", "zero-knowledge", "blockchain", "federated-learning",
        "medical", "api", "sdk", "hipaa", "gdpr", "solana"
    ],
    project_urls={
        "Bug Reports": "https://github.com/razaahmad9222/oneliac-python/issues",
        "Source": "https://github.com/razaahmad9222/oneliac-python",
        "Documentation": "https://healthcare-agents-sdk.readthedocs.io/",
        "API Documentation": "https://healthcare-agents-api.onrender.com/docs",
    },
)