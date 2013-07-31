# -*- coding: utf-8 -*-

"""
translate.client
~~~~~~~~~~~~~~~~

Python client for translate server. Provides a simple wrapper around the HTTP
interface.
"""

__title__ = 'client'
__version__ = '0.0.0'
__author__ = 'Erik Price'
__copyright__ = 'Copyright 2013 Erik Price'

__all__ = ['Client', 'ServerInformation']

from translate.client.client import Client, ServerInformation
