from setuptools import setup, find_packages
from pathlib import Path

# Get long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="stellr-sdk",
    version="0.0.1",
    description="SDK for creating and registering custon Orrin apps",  # short description
    long_description=long_description,  # full description shown on PyPI
    long_description_content_type="text/markdown",  # important if your README is Markdown
    packages=find_packages(),
    python_requires=">=3.9",
    author="Aidan White",
    author_email="ceo@stellr-company.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
