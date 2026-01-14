#!/usr/bin/env python3
from setuptools import setup, find_packages
import os

# Read README if exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="ag-cc-proxy",
    version="0.1.0",
    author="Catalyst",
    author_email="tutralabs@gmail.com",
    description="Proxy for Antigravity Claude/Gemini models with Claude Code CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TutraLabs/ag-cc-proxy",
    license="MIT",
    
    # Find packages in current directory (no src/)
    packages=find_packages(),
    
    python_requires=">=3.10",
    
    install_requires=[
        "aiohttp>=3.9.0",
    ],
    
    entry_points={
        "console_scripts": [
            "ag-cc-proxy=antigravity_proxy.__main__:main",
        ],
    },
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
)
