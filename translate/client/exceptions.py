# -*- coding: utf-8 -*-


class TranslateException(Exception):
    """Mostly empty base class for exceptions relating to translate"""

    @classmethod
    def from_response(cls, resp):
        """Generate a proper exception from the given requests response object
        and return it.
        """

        if resp.status_code == 429:
            pass
        elif resp.status_code == 452:
            pass
        elif resp.status_code == 453:
            pass
        elif resp.status_code == 454:
            pass

        return cls("TODO: writeme " + repr(resp))


class RatelimitException(TranslateException):
    """Exception raised when a client goes over the ratelimit."""
    pass
