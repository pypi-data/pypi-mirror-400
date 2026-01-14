"""
VerifAI SDK - Production Ready Setup
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="verifai-llm-sdk",
    version="0.1.0",
    description="VerifAI Python SDK for LLM tracing and evaluation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="VerifAI Contributors",
    author_email="hello@verifai.dev",
    url="https://github.com/verifai-ai/verifai-sdk",
    packages=find_packages(exclude=["verifai_backup*", "tests*"]),
    install_requires=[
        "requests>=2.31.0",
        "openai>=1.0.0",
        "opentelemetry-sdk>=1.20.0",
        "opentelemetry-api>=1.20.0",
        "opentelemetry-instrumentation>=0.41b0",
    ],
    extras_require={
        "openai": ["opentelemetry-instrumentation-openai>=0.1.0"],
        "langchain": ["opentelemetry-instrumentation-langchain>=0.1.0"],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai, llm, tracing, evaluation, observability, opentelemetry",
)
