#!/usr/bin/env python3

# This software is copyrighted and licensed under the terms of the MIT
# license.  See the LICENSE file found in the top-level directory of this
# distribution for copyright information and license terms.

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
