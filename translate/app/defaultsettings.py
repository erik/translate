# -*- coding: utf-8; -*-

SERVER = {
    'bind': '127.0.0.1',
    'port': 5000,

    'ratelimit': {
        'enabled': False,
        'limit': 0,
        'per': 0
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
        'timeout': 5
    },

    'translate_backend': {
        'active': False
    },

    'yandex': {
        'active': False
    }
}
