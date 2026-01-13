from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent


README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="rag-scrubber",
    version="0.1.3",
    description="Auto-removes headers, footers, and noise from PDF text for RAG apps.",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[],
    author="MUGESH KUMAR M",
)