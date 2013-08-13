# -*- coding: utf-8; -*-

import os

# Customize this file if necessary. (Hopefully) sane defaults are applied
# automatically, and any settings here take preference over those.

# These server settings are only useful when standalone server is launched via
# bin/translate
SERVER = {
    # Hostname to listen on. 0.0.0.0 makes this server available to everyone
    'bind': '0.0.0.0',
    # Port to listen on
    'port': 5005,

    # Rate limiting options (defaults to off)
    'ratelimit': {
        # Should we enable rate limiting?
        'enabled': True,
        # Maximum number of requests to server per timeframe per IP
        'limit': 10,
        # Timeframe for rate limiting. Requests are counted against limit for
        # this many seconds
        'per': 30
    },

    # Limits for size (in bytes) for texts to translate
    'sizelimit': {
        # Should we enable size limits?
        'enabled': True,
        # Force texts to be less than or equal to this number of
        # bytes. Backends (especially web services) may have different limits
        # and should automatically split up requests into multiple requests
        # under their limit (not counted individually toward ratelimit).
        'limit': 10 * 1024
    }
}

# Configuration for the various translation backends
#
# Each backend has a preset preference that can be overridden using the
# 'preference' key here. Use this if you want to try a specific backend before
# other possibilities.
BACKENDS = {
    # Dummy backend, doesn't do anything useful (translates between en-en)
    'dummy': {
        'active': False
    },

    # Local apertium service
    'apertium': {
        'active': True
    },

    # Apertium web service (api.apertium.org)
    'apertiumweb': {
        'active': True,
        # Timeout (seconds) for requests to web service
        'timeout': 5,
        # API key (optional) for webservice. Find more information on
        # api.apertium.org
        'key': os.environ.get('APERTIUM_KEY', None)
    },

    # Daisy-chained translation server
    'translate_backend': {
        'active': False,
        # Hostname of the translation server to use
        'host': '0.0.0.0',
        # Port of the translation server
        'port': 12345
    },

    # Yandex free translation service
    'yandex': {
        'active': True,
        # Sign up for a key at https://translate.yandex.com/apikeys
        'key': os.environ.get('YANDEX_KEY', None),
        # Timeout afterwhich to give up on request
        'timeout': 5
    }
}
