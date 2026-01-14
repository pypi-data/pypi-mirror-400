#!/usr/bin/env python3
"""
TypeFast - Terminal-based Adaptive Typing Practice
Setup script for PyPI distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="typefast",
    version="1.0.0",
    author="Will Isackson",
    author_email="seikixtc@gmail.com",
    description="Terminal-based adaptive typing practice with progressive key learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seikixtc/typefast",
    packages=find_packages(),
    py_modules=["typefast"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: Console :: Curses",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Education",
        "Topic :: Games/Entertainment",
        "Topic :: Terminals",
        "Typing :: Typed",
    ],
    keywords="typing practice tutor keyboard skills learning adaptive terminal cli",
    python_requires=">=3.6",
    install_requires=[
        "asciichartpy>=1.5.25",
    ],
    entry_points={
        "console_scripts": [
            "typefast=typefast:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/seikixtc/typefast/issues",
        "Source": "https://github.com/seikixtc/typefast",
        "Documentation": "https://github.com/seikixtc/typefast#readme",
    },
    include_package_data=True,
    zip_safe=False,
)
