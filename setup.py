#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: rjayapalan
Created: March 11, 2022
"""
from setuptools import setup
import os


def get_long_desc() -> str:

    if not os.path.isfile("README.rst"):
        return ""

    with open("README.rst") as f:
        desc = f.read()

    return desc


setup(
    name="filesplit",
    version="4.0.0",
    description="Python module that is capable of splitting files and merging it back.",
    long_description=get_long_desc(),
    author="Ramprakash Jayapalan",
    author_email="ramp16888@gmail.com",
    url="https://github.com/ram-jayapalan/filesplit",
    download_url="https://github.com/ram-jayapalan/filesplit/archive/refs/tags/v4.0.0.tar.gz",
    keywords="file split, filesplit, split file, splitfile",
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
    ],
    package_dir={'filesplit': 'src'},
    packages=['filesplit', 'filesplit.common'],
    python_requires='>=3, <4',
    project_urls={
        'Bug Reports': 'https://github.com/ram-jayapalan/filesplit/issues',
        'Source': 'https://github.com/ram-jayapalan/filesplit',
    },
)
