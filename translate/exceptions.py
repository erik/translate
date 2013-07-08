# -*- coding: utf-8 -*-

import flask


class APIException(Exception):

    # Format:
    #   HTTP code: (HTTP status message, message)
    API_ERRORS = {
        429: ('Too many requests', 'You went over the ratelimit'),
        452: ('Translation error', 'Bad params')

    }

    def __init__(self, status_code, status, message, details={}):
        self.status_code = status_code
        self.status = status
        self.message = message
        self.details = details

    def jsonify(self):
        resp = flask.jsonify(code=self.status_code, status=self.status,
                             url=flask.request.url, message=self.message,
                             details=self.details)

        resp.status_code = self.status_code
        resp.status = "%s %s" % (self.status_code, self.status)
        resp.mimetype = 'application/javascript'

        return resp

    @classmethod
    def ratelimit(cls, msg=None, details={}):
        tupl = APIException.API_ERRORS[429]
        return cls(429, tupl[0], msg or tupl[1], details)

    @classmethod
    def translate(cls, msg=None, details={}):
        tupl = APIException.API_ERRORS[452]
        return cls(452, tupl[0], msg or tupl[1], details)


class TranslationException(Exception):
    """Exception to be raised when a translation backend fails to translate a
    given block of text for whatever reason.
    """
    pass
