"""
Setup configuration for the parameter optimizer package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="parameter-optimizer",
    version="1.0.0",
    author="Parameter Optimizer Team",
    author_email="contact@parameter-optimizer.dev",
    description="A reusable parameter optimization package for systematic testing of parameter combinations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/parameter-optimizer/parameter-optimizer",
    project_urls={
        "Bug Tracker": "https://github.com/parameter-optimizer/parameter-optimizer/issues",
        "Documentation": "https://github.com/parameter-optimizer/parameter-optimizer#readme",
        "Source Code": "https://github.com/parameter-optimizer/parameter-optimizer",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
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
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Benchmark",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psutil>=5.8.0",  # For memory monitoring and resource management
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "hypothesis>=6.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "test": [
            "pytest>=7.0.0",
            "hypothesis>=6.0.0",
            "pytest-cov>=3.0.0",
        ],
    },
)
