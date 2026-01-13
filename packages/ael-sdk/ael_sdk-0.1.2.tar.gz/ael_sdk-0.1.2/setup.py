from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ael-sdk",
    version="0.1.2",
    author="Vinay Badhan",
    author_email="vinay.badhan21.work@gmail.com",
    description="Python SDK for Agent Execution Ledger - Audit trail for AI agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vinayb21-work/Agent-Execution-Ledger",
    project_urls={
        "Bug Tracker": "https://github.com/vinayb21-work/Agent-Execution-Ledger/issues",
        "Documentation": "https://github.com/vinayb21-work/Agent-Execution-Ledger#readme",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "httpx>=0.26.0",
        "pydantic>=2.5.0",
    ],
    extras_require={
        "google-adk": ["google-genai>=0.3.0"],
    },
    keywords="ai agents audit logging llm observability",
)
