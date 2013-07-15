# -*- coding: utf-8 -*-

# TODO: Write documentation

import json

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class TranslateException(Exception):
    """Mostly empty base class for exceptions relating to translate"""

    @classmethod
    def from_response(cls, resp):
        """Generate a proper exception from the given requests response object
        and return it.
        """

        if resp.status_code == 429:
            return RateLimitException.from_response(resp)
        elif resp.status_code == 452:
            return TranslationException.from_response(resp)
        elif resp.status_code == 453:
            return TranslatorException.from_response(resp)
        elif resp.status_code == 454:
            return BadLanguagePairException.from_response(resp)

        return cls("Unknown error occured: " + resp.data)


class RateLimitException(TranslateException):
    """Exception raised when a client goes over the ratelimit."""

    def __init__(self, limit, per, reset):
        self.limit = limit
        self.per = per
        self.reset = reset

    @classmethod
    def from_response(cls, resp):
        try:
            obj = json.loads(resp.data)
            details = obj.get('details', {})

            return cls(limit=details['limit'], per=details['per'],
                       reset=details['reset'])

        except (ValueError, KeyError):
            log.error("Received invalid JSON: " + resp.data)
            return cls(limit=0, per=0, reset=0)

    def __str__(self):
        return "Rate limit exceeded: {0} reqs / {1}s. Try again at {2}".format(
            self.limit, self.per, self.reset)


class TranslationException(TranslateException):
    """Returned on bad parameters to /translate"""

    @classmethod
    def from_response(cls, resp):
        try:
            obj = json.loads(resp.data)
            msg = obj['message']

            return cls("Bad parameters to translate API method: " + msg)
        except (ValueError, KeyError):
            log.error("Received invalid JSON: " + resp.data)
            return cls("Bad parameters to translate API method.")


class TranslatorException(TranslateException):

    def __init__(self, lang_pair, tried):
        self.lang_pair = lang_pair
        self.tried = tried

    @classmethod
    def from_response(cls, resp):
        try:
            obj = json.loads(resp.data)
            details = obj['details']

            pair = (details['from'], details['to'])
            return cls(lang_pair=pair, tried=details['tried'])

        except (ValueError, KeyError):
            log.error("Received invalid JSON: " + resp.data)

            return cls(lang_pair=('unknown', 'unknown'), tried=['unknown'])

    def __str__(self):
        return "Failed to translate {0} (tried: {1})".format(self.lang_pair,
                                                             self.tried)


class BadLanguagePairException(TranslateException):

    def __init__(self, lang_pair):
        self.lang_pair = lang_pair

    @classmethod
    def from_response(cls, resp):
        try:
            obj = json.loads(resp.data)
            details = obj['details']

            return cls(lang_pair=(details['from'], details['to']))

        except (ValueError, KeyError):
            log.error("Received invalid JSON: " + resp.data)

            return cls(lang_pair=('unknown', 'unknown'))

    def __str__(self):
        return "Unsupported language pair: {0}".format(self.lang_pair)
