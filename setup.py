#!/usr/bin/env python3

# See LICENSE file in top-level directory for copyright and license terms.
# Author: Jeff Webb <jeff.webb@codecraftsmen.org>

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
