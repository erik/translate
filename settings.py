# -*- coding: utf-8; -*-

import os

# Customize this file if necessary. (Hopefully) sane defaults are applied
# automatically (from translate/app/defaultsettings.py), and any settings
# here take preference over those.
#
# By default, all backends are disabled, so make sure you explicitly indicate
# those that you want to enable by setting the relevant 'active' key to True

# Configuration options to manage the server's functionality.
SERVER = {
    # The 'host', 'port', and 'ssl' settings are only useful when standalone
    # server is launched via the bin/translate executable.

    # Hostname to listen on. 0.0.0.0 makes this server available to everyone
    'host': '0.0.0.0',
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

    # Specify SSL key and certificates to use, for use with bin/translate. It's
    # probably better to use a front end server (nginx etc.) to do this for
    # you.
    #
    # This requires 'pyopenssl' (pip install pyopenssl)
    #
    # To create private key / certificate:
    #
    #   $ openssl genrsa 2048 > ssl.key
    #   $ openssl req -new -x509 -nodes -sha1 -days 365 -key ssl.key > ssl.cert
    'ssl': {
        'enabled': False,
        'key': 'ssl.key',
        'cert': 'ssl.cert'
    },

    # Limits for size (in bytes) for texts to translate (defaults to off)
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
# other possibilities. Higher preferences indicate a higher priority to try to
# use that backend when possible.
BACKENDS = {
    # Dummy backend, doesn't do anything useful (translates between en-en), for
    # testing purposes only.
    'dummy': {
        'active': False
    },

    # Local apertium service. You must have `apertium` on the PATH.
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
        'key': os.environ.get('APERTIUM_KEY')
    },

    # Backend using freetranslation.com
    'freetranslation': {
        'active': True,
        # Number of seconds to wait for connections to complete
        'timeout': 5,
        # Mandatory API key. You can sign up for a key here:
        # https://www.beglobal.com/developers/sign-up/
        'key': os.environ.get('FREETRANSLATION_KEY')
    },

    # Backend using frengly. Sign up for an account at frengly.com
    # WARNING: frengly currently seems to have pretty subpar results. Check if
    #          it works for your needs first.
    'frengly': {
        'active': True,
        # Number of seconds to wait for connections to complete
        'timeout': 5,
        # Email and password for account (these are unfortunately sent in the
        # URL as plain text)
        'email': os.environ.get('FRENGLY_EMAIL'),
        'password': os.environ.get('FRENGLY_PASSWORD')
    },

    # Daisy-chained translation server. Use this to fallback to a second
    # translate server when this one can't handle the given request.
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
        'key': os.environ.get('YANDEX_KEY'),
        # Timeout after which to give up on request
        'timeout': 5
    }
}
