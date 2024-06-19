# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='pyvisca',
    version='0.0.3',
    packages=find_packages(),
    include_package_data=False,
    install_requires=[],
)

# Compile with:
# python setup.py sdist upload -r pypi
