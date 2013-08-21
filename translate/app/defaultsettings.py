# -*- coding: utf-8; -*-

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
translate.app.defaultsettings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module defines the default settings that the translation server will use
if not overridden by the user's preferences.
"""

SERVER = {
    'bind': '127.0.0.1',
    'port': 5000,

    'ratelimit': {
        'enabled': False,
        'limit': 0,
        'per': 0
    },

    'ssl': {
        'enabled': False,
        'key': 'ssl.key',
        'cert': 'ssl.cert'
    },

    # Only allow 10k characters to be translated at once. Larger requests will
    # be rejected.
    'sizelimit': {
        'enabled': False,
        'limit': 10 * 1024
    }
}

BACKENDS = {
    'dummy': {
        'active': False
    },

    'apertium': {
        'active': False
    },

    'apertiumweb': {
        'active': False,
        'timeout': 5
    },

    'freetranslation': {
        'active': False,
        'timeout': 5
    },

    'translate_backend': {
        'active': False
    },

    'yandex': {
        'active': False
    }
}
