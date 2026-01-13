from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="nexus-gateway",
    version="0.1.2",  # <--- BUMPED VERSION (Crucial!)
    description="The Python SDK for Nexus Gateway - AI Semantic Caching Layer",
    long_description=long_description,  # <--- This puts the README on PyPI
    long_description_content_type="text/markdown", # <--- This tells PyPI it's Markdown
    author="Sunny Anand",
    author_email="your_email@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)