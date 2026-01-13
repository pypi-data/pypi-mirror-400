from setuptools import setup, find_packages

setup(
    name="rag-scrubber",
    version="0.1.1",
    description="Auto-removes headers, footers, and noise from PDF text for RAG apps.",
    packages=find_packages(),
    python_requires=">=3.7",
)