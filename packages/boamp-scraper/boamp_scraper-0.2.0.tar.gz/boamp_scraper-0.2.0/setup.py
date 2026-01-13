"""
BOAMP Scraper SDK - Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="boamp-scraper",
    version="0.2.0",
    author="Algora",
    author_email="contact@algora.fr",
    description="Scrape French public tenders (BOAMP) in 3 lines of Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/algora/boamp-scraper",
    project_urls={
        "Bug Tracker": "https://github.com/algora/boamp-scraper/issues",
        "Documentation": "https://github.com/algora/boamp-scraper#readme",
        "Source Code": "https://github.com/algora/boamp-scraper",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "mypy>=1.4.0",
            "ruff>=0.0.285",
        ],
    },
    keywords="boamp scraper france tenders public-procurement marchés-publics",
    include_package_data=True,
)

