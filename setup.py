#!/usr/bin/env python

import translate

import subprocess

from setuptools import setup, Command


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.check_call(['py.test', 'tests/'])

packages = [
    'translate'
]

requires = []


setup(name='translate',
      version=translate.__version__,
      description="A pluggable translation server.",
      long_description=open('README.rst').read(),
      author='Erik Price',
      tests_require=['pytest'],
      cmdclass= {'test': PyTest},
      test_suite='nose.collector',
      install_requires=requires,
      license=open('LICENSE').read())
