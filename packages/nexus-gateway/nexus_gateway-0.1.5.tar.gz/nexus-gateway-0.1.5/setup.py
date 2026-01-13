from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="nexus-gateway",
    version="0.1.5", 
    description="The Python SDK for Nexus Gateway",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sunny Anand",
    author_email="asunny583@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    # <--- THIS IS THE MAGIC PART --->
    entry_points={
        'console_scripts': [
            'nexus=nexus_gateway.cli:main',
        ],
    },
    # <--- END MAGIC PART --->
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)