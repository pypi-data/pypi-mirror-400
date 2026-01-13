"""
Setup script for Debt-Based Optimization Framework
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="debt-optimization",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A novel optimization framework based on debt-paying mechanics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Arya1718/debt-optimization",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
    ],
    extras_require={
        "accurate": ["torch>=1.9.0"],
        "viz": ["matplotlib>=3.3.0"],
        "full": ["torch>=1.9.0", "matplotlib>=3.3.0"],
    },
    entry_points={
        "console_scripts": [
            "debt-optimize-demo=debt_optimization.examples.demo:main",
        ],
    },
)