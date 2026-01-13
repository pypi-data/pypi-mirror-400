"""Setup script for far-search (core SDK)."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="far-search",
    version="1.0.0",
    author="Daniel Chang",
    author_email="yschang@blueskylineassets.com",
    description="Lightweight SDK for Federal Acquisition Regulations (FAR) search - no LangChain required",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blueskylineassets/far-search-tool",
    project_urls={
        "Homepage": "https://github.com/blueskylineassets/far-search-tool",
        "Documentation": "https://github.com/blueskylineassets/far-search-tool#readme",
        "RapidAPI": "https://rapidapi.com/yschang/api/far-rag-federal-acquisition-regulation-search",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=[
        "far",
        "federal-acquisition-regulations",
        "government-contracting",
        "semantic-search",
        "rag",
        "compliance",
        "procurement",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
    ],
)

