#!/usr/bin/env python3
"""
Setup script for LDC_Vortex-Datalayer package.
Minimal setup with only required fields.
"""

from setuptools import find_packages, setup

# Required fields with additional metadata
setup(
    name="LDC_Vortex-Datalayer",
    version="0.0.3",
    author="Sonu Sharma",
    author_email="sonu.sharma@lendenclub.com",
    maintainer="Sonu Sharma",
    maintainer_email="sonu.sharma@lendenclub.com",
    description="A comprehensive data access layer for Vortex apps",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10.0",
    install_requires=[
        "Django>=5.2.0",
        "psycopg[binary,pool]>=3.2.9",
        "redis>=5.0.3",
        "pytz>=2024.1",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)
