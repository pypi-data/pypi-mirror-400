from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="pawser",
    version="1.0.1",
    packages=find_packages(),
    python_requires=">=3.10",
    author="komoriiwakura",
    author_email="k0mori@proton.me",
    description="A Python module for parsing and rendering PawML",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/komoriiwakura/pawser",
    license="All rights reserved; educational/personal use only",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
)
