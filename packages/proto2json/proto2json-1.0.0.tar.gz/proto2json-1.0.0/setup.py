#!/usr/bin/env python3
"""
Setup script for proto2json package.

This file provides backward compatibility with older build tools.
Modern installations should use pyproject.toml.
"""
from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="proto2json",
    version="1.0.0",
    author="Liu Jiatian",
    author_email="liujiatian.cool@gmail.com",
    description="Decode protobuf binary data to JSON without schema definition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ljt270864457/proto2json",
    packages=find_packages(exclude=["tests*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    keywords="protobuf json decoder protocol-buffers protobuf-decoder",
    project_urls={
        "Bug Tracker": "https://github.com/ljt270864457/proto2json/issues",
        "Source Code": "https://github.com/ljt270864457/proto2json",
    },
)
