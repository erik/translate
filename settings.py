# -*- coding: utf-8; -*-

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
    }
}

# Configuration for the various translation backends
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
        'key': 'foobar'
    },

    # Daisy-chained translation server
    'translate_backend': {
        'active': False,
        # Hostname of the translation server to use
        'host': '0.0.0.0',
        # Port of the translation server
        'port': 12345
    }
}
