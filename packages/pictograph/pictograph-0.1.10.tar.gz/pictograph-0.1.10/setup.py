"""
Pictograph Python SDK - Setup configuration
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="pictograph",
    version="0.1.10",
    description="Official Python SDK for Pictograph Context Engine - Computer Vision Annotation Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pictograph.cloud",
    author="Pictograph",
    author_email="support@pictograph.cloud",
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
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    keywords="computer-vision annotation labeling dataset machine-learning ai",
    packages=find_packages(exclude=["tests", "docs", "examples"]),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "Pillow>=10.0.0",
        "tqdm>=4.65.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    project_urls={
        "Documentation": "https://pictograph.cloud/docs",
        "Bug Reports": "https://github.com/pictograph-labs/pictograph-sdk/issues",
        "Source": "https://github.com/pictograph-labs/pictograph-sdk",
    },
)
