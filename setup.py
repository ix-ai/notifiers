#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" setup.py for pypi """

import setuptools
from ix_notifiers import constants

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ix-notifiers",
    version=f"{constants.VERSION}.{constants.BUILD}",
    author="ix.ai",
    author_email="docker@ix.ai",
    description="A python library for notifiers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT License',
    url="https://gitlab.com/ix.ai/notifiers",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'python-telegram-bot>=13.1',
        'requests>=2.25.0',
    ],
)
