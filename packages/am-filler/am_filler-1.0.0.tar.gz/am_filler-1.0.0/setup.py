"""
AM_filler Setup Configuration

Install with: pip install -e .
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="am_filler",
    version="1.0.0",
    author="Mudassar Hussain",
    author_email="mudassarjutt65030@gmail.com",
    description="Intelligent, automatic missing value imputation library for pandas datasets with context-aware text handling.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MudassarGill/AM_filler",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "scipy>=1.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "ml": [
            "scikit-learn>=1.0.0",
        ],
    },
    keywords="missing values, imputation, data cleaning, pandas, machine learning, preprocessing",
    project_urls={
        "Bug Reports": "https://github.com/MudassarGill/AM_filler/issues",
        "Source": "https://github.com/MudassarGill/AM_filler",
    },
)
