#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="linkpreview-cli",
    version="1.0.0",
    author="Yoel Frischoff",
    author_email="yoel.frischoff@gmail.com",
    description="Generate beautiful link previews from any URL with smart image detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yoel-frischoff/linkpreview-cli",
    project_urls={
        "Bug Tracker": "https://github.com/yoel-frischoff/linkpreview-cli/issues",
        "Documentation": "https://github.com/yoel-frischoff/linkpreview-cli/wiki",
        "Source": "https://github.com/yoel-frischoff/linkpreview-cli",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
        ]
    },
    entry_points={
        "console_scripts": [
            "linkpreview=linkpreview_cli:main",
        ],
    },
    include_package_data=True,
    keywords="link preview, open graph, metadata, url, social media, image generation, pdf, png",
    zip_safe=False,
)