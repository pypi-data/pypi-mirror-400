from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openjobs",
    version="0.1.0",
    author="OpenJobs Contributors",
    description="Open source job scraper using Firecrawl + Gemini AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/openjobs",
    packages=find_packages(),
    package_data={
        "openjobs": ["config/*.json"],
    },
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
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
        "tenacity>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openjobs=openjobs.scraper:main",
        ],
    },
)
