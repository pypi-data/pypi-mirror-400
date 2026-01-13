from pathlib import Path
from setuptools import setup, find_packages

# Read the README file for long_description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="spay",
    version="3.0.0",
    author="Saba Pardazesh",
    author_email="info@spay.ir",
    description="Python SDK for Spay internet gateway",
    packages=["spay"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    install_requires=["requests>=2.31.0"],
)
