from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cryzen",
    version="0.1.4",
    author="Mahadi bin Iqbal",
    author_email="islammdmahadi943@gmail.com",
    description="A powerful & modular toolkit for modern cryptography and hashing.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mahadi99900/cryzen",
    project_urls={
        "Bug Tracker": "https://github.com/mahadi99900/cryzen/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
    ],
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.7",
    install_requires=[
        "pycryptodome>=3.10.1"
    ],
)
