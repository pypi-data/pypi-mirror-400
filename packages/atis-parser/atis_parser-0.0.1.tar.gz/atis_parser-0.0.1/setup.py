"""Setup script for atis-parser package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="atis-parser",
    version="0.0.1",
    author="Ryder Damen",
    author_email="ryder@planes.fyi",
    description="A regex-based parser for ATIS, METAR, and TAF aviation weather reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/planesfyi/atis_parser",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
    ],
)

