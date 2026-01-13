#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

def get_version() -> str:
    """ Get the version string from environment variables.

    Raises:
        RuntimeError: If neither VERSION nor CI_COMMIT_TAG is set in environment variables

    Returns:
        str: version string
    """
    tag = os.environ.get('VERSION') or os.environ.get('CI_COMMIT_TAG')
    if tag is None or tag == '':
        raise RuntimeError("VERSION or CI_COMMIT_TAG environment variable must be set")
    return tag[1:] if tag.startswith('v') else tag

setup(
    name='zaguan',
    version=get_version(),
    author='Luis Andres Giordano',
    author_email='agiordano@msa.com.ar',
    packages=['zaguan'],
    scripts=[],
    url='http://pypi.python.org/pypi/zaguan/',
    license='LICENSE.txt',
    description='Front end framework to develop apps with webkit an pygtk',
    long_description=open('README.txt').read(),
    install_requires=[],
    classifiers=[]
)
