# -*- coding: utf-8; -*-

# Customize this file if necessary

# These are only useful when standalone server is launched via bin/translate
SERVER = {
    'bind': '0.0.0.0',
    'port': 5005,

    'ratelimit': {
        'enabled': True,
        'limit': 10,
        'per': 30
    }
}

BACKENDS = {
    'dummy': {
        'active': False
    },

    'apertium': {
        'active': True
    },

    'apertiumweb': {
        'active': True,
        'timeout': 5,
        'key': 'foobar'
    },

    'translate_backend': {
        'active': False,
        'host': '0.0.0.0',
        'port': 12345
    }
}
