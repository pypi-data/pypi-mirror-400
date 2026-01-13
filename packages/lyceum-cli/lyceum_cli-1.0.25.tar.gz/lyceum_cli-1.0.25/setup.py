#!/usr/bin/env python3
"""Setup script for Lyceum CLI"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file
this_directory = Path(__file__).parent
long_description = ""
readme_file = this_directory / "README.md"
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')

setup(
    name="lyceum-cli",
    version="1.0.25",
    description="Command-line interface for Lyceum Cloud Execution API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Lyceum Team",
    author_email="support@lyceum.technology",
    url="https://lyceum.technology",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.0.0",
        "httpx>=0.24.0",
        "click>=8.0.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0",
        "PyJWT>=2.8.0",
        "supabase>=2.0.0",
        "requests>=2.31.0",
        "attrs>=22.2.0",
    ],
    entry_points={
        "console_scripts": [
            "lyceum=lyceum.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development",
        "Topic :: System :: Distributed Computing",
        "Topic :: Utilities",
    ],
    keywords="cloud computing, code execution, docker, ai, inference, batch processing",
)