#!/usr/bin/env python3

# Copyright (C) 2021 NTA, Inc.

from setuptools import setup, find_packages

setup(
    name="ticli",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        #"fire", # optional
        "pydantic",
        "makefun",
        "decopatch",
    ],
)
