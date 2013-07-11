# -*- coding: utf-8 -*-


class TranslateException(Exception):
    """Empty base class for exceptions relating to translate"""

    @classmethod
    def from_json(obj):
        """Generate a proper exception from the given JSON response object and
        return it.
        """
        return TranslateException("TODO: writeme " + repr(obj))
