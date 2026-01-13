"""Setup script for far-search-autogpt."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="far-search-autogpt",
    version="1.0.0",
    author="Daniel Chang",
    author_email="yschang@blueskylineassets.com",
    description="AutoGPT plugin for Federal Acquisition Regulations (FAR) search",
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
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=[
        "autogpt",
        "far",
        "federal-acquisition-regulations",
        "government-contracting",
        "plugin",
        "ai-agent",
        "compliance",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.28.0",
    ],
)

