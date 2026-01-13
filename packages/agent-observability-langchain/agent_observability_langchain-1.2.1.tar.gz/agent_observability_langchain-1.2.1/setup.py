"""Setup script for agent-observability-langchain."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agent-observability-langchain",
    version="1.2.1",
    author="Agent Observability Team",
    author_email="hello@agentobs.io",
    description="LangChain integration for Agent Observability - structured logging, cost tracking, and compliance for AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://api-production-0c55.up.railway.app",
    project_urls={
        "Homepage": "https://api-production-0c55.up.railway.app",
        "Documentation": "https://api-production-0c55.up.railway.app/docs",
        "Pricing": "https://api-production-0c55.up.railway.app/pricing.json",
        "OpenAPI": "https://api-production-0c55.up.railway.app/openapi.json",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Logging",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: AsyncIO",
    ],
    keywords=[
        "langchain",
        "agent",
        "observability",
        "logging",
        "compliance",
        "audit",
        "ai-agent",
        "llm",
        "cost-tracking",
        "monitoring",
        "analytics",
        "structured-logging",
    ],
    python_requires=">=3.9",
    install_requires=[
        "agent-observability>=1.1.0",
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
)

