# -*- coding: utf-8 -*-

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
translate.client.exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are exception classes that are used by translate.client.Client. Most of
these classes are simple wrappers, just to differentiate different types of
errors. They can be constructed from a requests response object, or JSON
,returned from an API call.
"""

import json

import logging
log = logging.getLogger(__name__)


class TranslateException(Exception):
    """Mostly empty base class for exceptions relating to translate.

    This class is used as a catch-all for exceptions thrown by the server. If
    possible, a more specific subclass of this exception will be used.
    """

    @classmethod
    def from_json(cls, obj, status_code=400):
        """Return the proper exception class from the JSON object returned from
        the server.
        """

        exceptions = {
            429: RateLimitException,
            431: SizeLimitException,
            452: TranslationException,
            453: TranslatorException,
            454: BadLanguagePairException
        }

        try:
            code = obj['code'] if ('code' in obj) else status_code

            klass = exceptions[code]
            return klass.from_json(obj)

        except KeyError:
            return cls("Unknown error occured: " + repr(obj))

    @classmethod
    def from_response(cls, resp):
        """Generate a proper exception from the given requests response object
        and return it.
        """

        try:
            obj = json.loads(resp.text)
            return TranslateException.from_json(obj, resp.status_code)
        except ValueError:
            log.error("Was given invalid JSON, bailing...")
            return TranslateException.from_json({}, resp.status_code)


class HTTPException(TranslateException):
    """Raised when an error occurs with the HTTP connection to the server
    (e.g. host is not available, doesn't respond, etc.)
    """

    pass


class RateLimitException(TranslateException):
    """Exception raised when a client goes over the ratelimit."""

    def __init__(self, limit, per, reset):
        self.limit = limit
        self.per = per
        self.reset = reset

    @classmethod
    def from_json(cls, obj):
        try:
            details = obj.get('details', {})

            return cls(limit=details['limit'], per=details['per'],
                       reset=details['reset'])

        except KeyError:
            log.error("Received invalid JSON: " + repr(obj))
            return cls(limit=0, per=0, reset=0)

    def __str__(self):
        return "Rate limit exceeded: {0} reqs / {1}s. Try again at {2}".format(
            self.limit, self.per, self.reset)


class SizeLimitException(TranslateException):
    """Exception raised when a client tries to translate a text that is over
    the server's size limit.
    """

    def __init__(self, len, limit):
        self.len = len
        self.limit = limit

    @classmethod
    def from_json(cls, obj):
        try:
            details = obj['details']
            return cls(len=details['len'], limit=details['limit'])

        except KeyError:
            log.error("Received invalid JSON: %s", repr(obj))
            return cls(len=0, limit=0)

    def __str__(self):
        return "Specified text was too large: %d bytes. Maximum is %d bytes"\
            .format(self.len, self.limit)


class TranslationException(TranslateException):
    """Returned on bad parameters to /translate"""

    @classmethod
    def from_json(cls, obj):
        try:
            msg = obj['message']

            return cls("Bad parameters to translate API method: " + msg)
        except KeyError:
            log.error("Received invalid JSON: " + repr(obj))
            return cls("Bad parameters to translate API method.")


class TranslatorException(TranslateException):
    """Returned when bad parameters are passed to the /translate method. (This
    probably indicates some kind of API / Client bug.)
    """

    def __init__(self, lang_pair, tried):
        self.lang_pair = lang_pair
        self.tried = tried

    @classmethod
    def from_json(cls, obj):
        try:
            details = obj['details']

            pair = (details['from'], details['to'])
            return cls(lang_pair=pair, tried=details['tried'])

        except KeyError:
            log.error("Received invalid JSON: " + repr(obj))

            return cls(lang_pair=('unknown', 'unknown'), tried=['unknown'])

    def __str__(self):
        return "Failed to translate {0} (tried: {1})".format(self.lang_pair,
                                                             self.tried)


class BadLanguagePairException(TranslateException):
    """Raised when the client tried to translate using a language pair not
    supported by the server
    """

    def __init__(self, lang_pair):
        self.lang_pair = lang_pair

    @classmethod
    def from_json(cls, obj):
        try:
            details = obj['details']

            return cls(lang_pair=(details['from'], details['to']))

        except KeyError:
            log.error("Received invalid JSON: " + repr(obj))

            return cls(lang_pair=('unknown', 'unknown'))

    def __str__(self):
        return "Unsupported language pair: {0}".format(self.lang_pair)
