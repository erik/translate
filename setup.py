#!/usr/bin/env python

import translate

from setuptools import setup

packages = [
    'translate'
]

requires = []

setup(name='translate',
      version=translate.__version__,
      description="A pluggable translation server.",
      long_description=open('README.rst').read(),
      author='Erik Price',
      packages=packages,
      install_requires=requires,
      license=open('LICENSE').read())
