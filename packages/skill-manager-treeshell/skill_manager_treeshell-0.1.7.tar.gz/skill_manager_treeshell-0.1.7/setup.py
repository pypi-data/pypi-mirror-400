#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="custom-treeshell",
    version="1.0.0",
    author="TreeShell Developer",
    description="Custom TreeShell library",
    packages=find_packages(),
    install_requires=[
        "heaven-tree-repl>=0.1.0",
    ],
    python_requires=">=3.8",
)
