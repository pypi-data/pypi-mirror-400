#!/usr/bin/env python

from setuptools import setup, find_packages
from pathlib import Path


BASE_DIR = Path(__file__).parent


setup(
    name="androidkit",
    version="0.1.0",
    description="Swiss army knife library for interacting with android things",
    author="Leo Feradero Nugraha",
    author_email="leoferaderonugraha@gmail.com",
    python_requires=">=3.11",
    package_dir={"": "lib"},
    packages=find_packages(where="lib"),
    include_package_data=True,
    install_requires=[
        "requests>=2.32.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Libraries",
    ],
    keywords='android,apk'
)
