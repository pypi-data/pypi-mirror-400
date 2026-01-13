"""Setup configuration for WIBA Python client."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="wiba",
    version="0.2.0",
    author="WIBA Research Team",
    author_email="airan002@ucr.edu",
    description="Official Python client library for WIBA argument mining API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WIBA-ORG/wiba-python-client",
    project_urls={
        "Homepage": "https://wiba.dev",
        "Documentation": "https://wiba.dev/docs",
        "Repository": "https://github.com/WIBA-ORG/wiba-python-client",
        "Bug Reports": "https://github.com/WIBA-ORG/wiba-python-client/issues",
    },
    packages=find_packages(),
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
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wiba=wiba.cli:main",
        ],
    },
    keywords=[
        "argument mining",
        "natural language processing",
        "nlp",
        "text analysis",
        "computational argumentation",
        "topic extraction",
        "stance detection",
    ],
    zip_safe=False,
    include_package_data=True,
)