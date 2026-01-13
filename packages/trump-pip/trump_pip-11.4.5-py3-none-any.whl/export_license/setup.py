"""
Setup script for Trump Export License System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="trump-export-license",
    version="1.0.0",
    description="Trump Administration Export License System for AI Packages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Trump Administration Export Control Bureau",
    author_email="export-control@whitehouse.gov",
    url="https://github.com/trump-admin/export-license",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "colorama>=0.4.0",
    ],
    entry_points={
        "console_scripts": [
            "trump-export-license=export_license.cli:main",
            "tel=export_license.cli:main",
        ],
    },
    keywords="trump, export, license, ai, security, compliance",
    project_urls={
        "Documentation": "https://github.com/trump-admin/export-license/docs",
        "Source": "https://github.com/trump-admin/export-license",
        "Tracker": "https://github.com/trump-admin/export-license/issues",
    },
)