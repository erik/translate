#!/usr/bin/env python

import translate

import subprocess

from setuptools import setup, find_packages, Command


class PyLint(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        subprocess.check_call(['flake8', 'translate', 'bin'])


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
      author_email='erik@erikprice.net',
      url='https://github.com/boredomist/translate',
      tests_require=['pytest'],
      cmdclass={'test': PyTest, 'lint': PyLint},
      install_requires=requires,
      license='GPLv3',
      packages = find_packages(),
      include_package_data = True,
      scripts=['bin/translate'])
