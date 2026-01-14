"""
fast2common - Core utilities for automated Android testing

A comprehensive toolkit for Android RPA (Robotic Process Automation)
including ADB control, AI-powered UI analysis, and test case actions.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="fast2common",
    version="0.2.0",
    author="Auto Test Team",
    author_email="test@example.com",
    description="Core utilities for Laite RPA: ADB control, AI client, UI analysis, and test actions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/fast2common",  # 替换为实际仓库地址
    packages=find_packages(exclude=["tests", "tests.*", "*.tests", "*.tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        "zhipuai>=1.0.0",
        "pillow>=9.0.0",
        "aiohttp>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="android testing automation rpa adb ui-analysis ai test-actions",
    project_urls={
        "Bug Reports": "https://github.com/yourorg/fast2common/issues",
        "Source": "https://github.com/yourorg/fast2common",
    },
)
