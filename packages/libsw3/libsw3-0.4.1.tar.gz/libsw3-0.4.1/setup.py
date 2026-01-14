#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools,distutils,shutil,re,os

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="libsw3",
    version="0.4.1",
    author="Chen chuan",
    author_email="kcchen@139.com",
    description="libsw3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://svn2.rtfund.com/svn/libsw3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    entry_points={
        'console_scripts':  [
            'sw=libsw3.sw:main',
        ],
    },
)
