# setup.py

from setuptools import setup, find_packages
from pathlib import Path

# Read in the long description from your README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="secretverify",
    version="0.7.0",
    description="Terminal-based tool to quickly validate leaked secrets across multiple providers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Mark Graziano",
    author_email="mgraziano@twilio.com",
    url="https://github.com/markgraziano-twlo/secretverify",
    license="MIT",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.7",
        "requests>=2.31.0",
        "boto3>=1.26.151",
        "google-auth>=2.23.0",
    ],
    entry_points={
        "console_scripts": [
            "secretverify=secretverify.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
