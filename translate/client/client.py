# -*- coding: utf-8 -*-

import json
import requests

from translate.client.exceptions import TranslateException

# TODO: Handle rate limiting
# TODO: More (i.e. some) error handling


class Client(object):
    """A client for interacting with translate server v1 API"""

    def __init__(self, host, port=5005, scheme='http', **kwargs):
        """TODO: Write me"""
        self.host = host
        self.scheme = scheme
        self.port = port
        self.options = kwargs

        self.base_url = "{0}://{1}:{2}/api/v1/".format(self.scheme, self.host,
                                                       self.port)
        self.backends = None
        self.pairs = None

    def language_pairs(self, refresh=False):
        """Get the list of supported language pairs. If refresh is True, will
        ignore previously cached results and hit the server again.
        """

        if refresh or (self.pairs is None):
            obj = self._request('pairs')
            self.pairs = [(p[0], p[1]) for p in obj['pairs']]

        return self.pairs

    def translators(self, refresh=False):
        """Returns a dict containing names of translation services available
        and some basic info about them
        """

        if refresh or (self.backends is None):
            obj = self._request('translators')

            self.backends = {}

            for b in obj['backends']:
                # Convert arrays to tuples
                b['pairs'] = [(p[0], p[1]) for p in b['pairs']]
                self.backends[b['name']] = b

            # Make sure these don't get out of sync by forcing language pairs
            # to regenerate as well
            self.pairs = None

        return self.backends

    def translate(self, text, from_lang, to_lang):
        """Translate a given string of text between languages."""

        # Check that we're translating between valid languages
        # TODO: This could be out of date if the language pairs change between
        #       requests.
        if (from_lang, to_lang) not in self.language_pairs(refresh=False):
            raise TranslateException("Bad language pair ({0}, {1})".
                                     format(from_lang, to_lang))

        try:
            params = {'from': from_lang, 'to': to_lang, 'text': text}
            obj = self._request('translate', **params)

            return obj['result']
        except TranslateException:
            pass

    def _request(self, method, **kwargs):
        """Convenience function to call an API function for the given client
        and return parsed JSON, or raise a TranslateException on error.
        """

        url = self.base_url + method

        req = requests.get(url, params=kwargs)
        obj = json.loads(req.text)

        if req.status_code != 200:
            raise TranslateException.from_json(obj)

        return obj
