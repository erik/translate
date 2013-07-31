# -*- coding: utf-8 -*-

# This file is part of translate.
#
# translate is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# translate is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# translate.  If not, see <http://www.gnu.org/licenses/>.

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
