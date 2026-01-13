"""Setup script for agent-observability-autogpt."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-observability-autogpt",
    version="1.2.1",
    author="Agent Observability Team",
    author_email="hello@agentobs.io",
    description="AutoGPT plugin for Agent Observability - automatic logging, cost tracking, and compliance",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://api-production-0c55.up.railway.app",
    project_urls={
        "Homepage": "https://api-production-0c55.up.railway.app",
        "Documentation": "https://api-production-0c55.up.railway.app/docs",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=[
        "autogpt",
        "agent",
        "observability",
        "plugin",
        "logging",
        "compliance",
        "ai-agent",
        "cost-tracking",
    ],
    python_requires=">=3.10",
    install_requires=[
        "agent-observability>=1.1.0",
    ],
)

