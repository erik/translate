# -*- coding: utf-8; -*-

SERVER = {
    'bind': '127.0.0.1',
    'port': 5000,

    'ratelimit': {
        'enabled': False,
        'limit': 0,
        'per': 0
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

    'translate_backend': {
        'active': False
    },

    'yandex': {
        'active': False
    }
}
