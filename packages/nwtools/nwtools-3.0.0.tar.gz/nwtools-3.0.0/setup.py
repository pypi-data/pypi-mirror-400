#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取 README.md 作为长描述
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="nwtools",
    version="3.0.0",
    author="ruin321",
    author_email="",
    description="A Python package for negatively optimizing your Windows/Linux system performance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Benchmark",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
    install_requires=[
        "psutil>=5.8.0",
        "requests>=2.25.1",
        "colorama>=0.4.4",
        "pyyaml>=5.4.1",
    ],
    entry_points={
        "console_scripts": [
            "nwtools=nwtools.cli:main",
            "nwtools-tui=nwtools.tui:main",
            "nwtools-simple-tui=nwtools.simple_tui:main",
            "nwtools-stable-tui=nwtools.stable_tui:main",
        ],
    },
    include_package_data=True,
)
