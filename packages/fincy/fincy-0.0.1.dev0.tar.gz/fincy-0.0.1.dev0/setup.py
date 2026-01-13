# -*- encoding: utf-8 -*-
"""
Setup configuration for the fincy package.

This setup.py file is configured to:
1. Build distributable wheel files
2. Publish to PyPI
3. Manage package metadata and dependencies
"""

from setuptools import setup, find_packages
import os

# Get absolute path to the directory containing setup.py
here = os.path.abspath(os.path.dirname(__file__))

# Read version from VERSION file
with open(os.path.join(here, "fincy", "VERSION"), "r", encoding="utf-8") as f:
    version = f.read().strip()

# Read README for long description
with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements from requirements.txt
requirements = []
req_file = os.path.join(here, "requirements.txt")
if os.path.exists(req_file):
    with open(req_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f.readlines()
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="fincy",
    version=version,
    description="A lightweight and extensible Python toolkit for calculating financial metrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="FinoFunda",
    url="https://github.com/finofunda/fincy",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "finance",
        "financial-metrics",
        "financial-analysis",
        "calculator",
        "toolkit",
    ],
    project_urls={
        "Bug Reports": "https://github.com/finofunda/fincy/issues",
        "Source": "https://github.com/finofunda/fincy",
        "Documentation": "https://fincy.readthedocs.io",
    },
    zip_safe=False,
)
