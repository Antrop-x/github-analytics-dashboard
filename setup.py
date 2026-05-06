"""
Setup configuration for GitHub Analytics Dashboard.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            requirements.append(line)

setup(
    name="github-analytics-dashboard",
    version="1.0.0",
    author="GitHub Analytics Team",
    author_email="team@github-analytics.com",
    description="A comprehensive dashboard for analyzing GitHub repository data and metrics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/github-analytics-dashboard",
    packages=find_packages(exclude=["tests*", "docs*"]),
    py_modules=["app", "cli"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "pylint>=3.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "github-analytics=cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)