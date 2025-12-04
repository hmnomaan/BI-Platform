"""
Setup script for BI Platform package.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
def read_requirements(file_path):
    """Read requirements from file."""
    req_file = Path(__file__).parent / file_path
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="bi-platform",
    version="1.0.1",
    author="BI Platform Team",
    author_email="support@bi-platform.com",
    description="Business Intelligence Platform with API Integration Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/bi-platform",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements/base.txt"),
    extras_require={
        "api": read_requirements("requirements/api.txt"),
        "bi": read_requirements("requirements/bi.txt"),
        "dev": read_requirements("requirements/dev.txt"),
        "database": read_requirements("requirements/database.txt"),
        "all": (
            read_requirements("requirements/base.txt") +
            read_requirements("requirements/api.txt") +
            read_requirements("requirements/bi.txt") +
            read_requirements("requirements/dev.txt")
        ),
        "full": (
            read_requirements("requirements/base.txt") +
            read_requirements("requirements/api.txt") +
            read_requirements("requirements/bi.txt") +
            read_requirements("requirements/dev.txt") +
            read_requirements("requirements/database.txt")
        ),
    },
    include_package_data=True,
    package_data={
        "": ["configs/**/*.yaml", "configs/**/*.json"],
    },
    entry_points={
        "console_scripts": [
            "bi-dashboard=bi_dashboard.app:main",
            "bi-api-server=api_engine.http_service:main",
        ],
    },
    zip_safe=False,
)
