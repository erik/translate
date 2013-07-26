# -*- coding: utf-8 -*-

"""
translate.exceptions
~~~~~~~~~~~~~~~~~~~~

Custom Exception classes for use by the translation server.
"""

import flask


class APIException(Exception):
    """Exception used for errors in API calls. Raised instances of this class
    (and instances of subclasses) will be caught by the flask app and
    rendered using APIException.jsonify
    """

    # Format:
    #   HTTP code: (HTTP status message, message)
    API_ERRORS = {
        429: ('Too many requests', 'You went over the ratelimit'),
        431: ('Text too large', 'Given text was too large for this server'),
        452: ('Translation error', 'Bad params to /translate'),
        453: ('Translator error', 'Failed to translate text'),
        454: ('Bad language pair',
              'No translator can handle this language pair')
    }

    def __init__(self, status_code, status, message, details={}):
        self.status_code = status_code
        self.status = status
        self.message = message
        self.details = details
        self.url = flask.request.url

    def jsonify(self):
        """Return a flask Response object containing a JSON representation of
        the instance of this class. This should set everything necessary for
        the request
        """
        resp = flask.jsonify(code=self.status_code, status=self.status,
                             url=self.url, message=self.message,
                             details=self.details)

        resp.status_code = self.status_code
        resp.status = "%s %s" % (self.status_code, self.status)
        resp.mimetype = 'application/javascript'

        return resp

    @classmethod
    def ratelimit(cls, limit, per, reset):
        """Class method to construct an APIException for going over the
        ratelimit. The optional msg and details parameters can be used to add
        additional information to the error.
        """
        tupl = APIException.API_ERRORS[429]
        return cls(429, tupl[0], tupl[1],
                   {'limit': limit,
                    'per': per,
                    'reset': reset})

    @classmethod
    def pair(cls, from_lang, to_lang, text):
        """Class method to construct an APIException for bad language pairs
        given to the translate API method.
        """
        tupl = APIException.API_ERRORS[454]
        return cls(454, tupl[0], tupl[1],
                   {'from': from_lang,
                    'to': to_lang,
                    'text': text})

    @classmethod
    def translator(cls, from_lang, to_lang, text, tried):
        """Class method to construct an APIException for cases where each
        possible translation backend fails to translate a given piece of text.
        """
        tupl = APIException.API_ERRORS[453]
        return cls(453, tupl[0], tupl[1],
                   {'from': from_lang,
                    'to': to_lang,
                    'text': text,
                    'tried': tried})

    @classmethod
    def translate(cls, msg=None, details={}):
        """Class method to construct an APIException for translate related API
        errors. The optional msg and details parameters can be used to add
        additional information to the error.
        """
        tupl = APIException.API_ERRORS[452]
        return cls(452, tupl[0], msg or tupl[1], details)

    @classmethod
    def sizelimit(cls, len, limit):
        """Class method to construct an APIException for /translate requests
        that are too large for the server to handle.
        """
        tupl = APIException.API_ERRORS[431]
        return cls(431, tupl[0], tupl[1],
                   {'given': len,
                    'limit': limit})


class TranslationException(Exception):
    """Exception to be raised when a translation backend fails to translate a
    given block of text for whatever reason.
    """
    pass
