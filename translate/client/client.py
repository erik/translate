# -*- coding: utf-8 -*-

import json
import requests
import urllib

import translate.client.exceptions
from translate.client.exceptions import TranslateException,\
    BadLanguagePairException

import logging
logging.basicConfig()
log = logging.getLogger(__name__)

# TODO: Handle rate limiting
# TODO: More (i.e. some) error handling


class Client(object):
    """A client for interacting with translate server v1 API"""

    def __init__(self, host, port=5000, scheme='http', timeout=5, **kwargs):
        """TODO: Write me"""
        self.host = host
        self.scheme = scheme
        self.port = port
        self.timeout = timeout
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

    def translate(self, text, from_lang, to_lang, refresh=False):
        """Translate a given string of text between languages."""

        # Check that we're translating between valid languages
        if (from_lang, to_lang) not in self.language_pairs(refresh=refresh):
            raise BadLanguagePairException(lang_pair=(from_lang, to_lang))

        try:
            kwargs = {'from': from_lang, 'to': to_lang, 'text': text}
            obj = self._request('translate', **kwargs)

            return obj['result']

        except TranslateException as exc:
            log.error("Failed to translate text (%s-%s): %s",
                      from_lang, to_lang, exc)
            raise exc

    def batch_translate(self, params):
        """Translate multiple texts and language pairs in a single
        call. Returns a list of strings containing the resulting translated
        texts, or an Exception object, if the request failed.

        This function won't raise any exceptions explicitly, so it's important
        to check the results.

        XXX: Is this Pythonic or even good API design? Not sure how else to
             handle it.
        XXX: Should timeout change? It definitely takes longer for this (with
             good reason)

        params is a list of (text, from_lang, to_lang).
        """

        urls = []

        # TODO: could do client-side checking to see if lang pair
        #       supported. I doubt it would help much of anything.
        for tupl in params:
            if len(tupl) != 3:
                raise ValueError("Badly formed argument, expected tuple \
of (text, from, to), got " + repr(tupl))

            text = urllib.quote(tupl[0], safe='')
            from_lang = urllib.quote(tupl[1], safe='')
            to_lang = urllib.quote(tupl[2], safe='')

            urls.append("/api/v1/translate?from={0}&to={1}&text={2}"
                        .format(from_lang, to_lang, text))

        results = []

        try:
            objs = self._post_request('batch', urls=json.dumps(urls))

            for obj in objs:
                if obj['status'] != 200:
                    # TODO: Handle errors
                    results.append(None)
                else:
                    results.append(obj['data']['result'])

        except TranslateException as exc:
            log.error("Failed batch translate: %s", str(exc))
            raise exc

        return results

    def can_translate(self, from_lang, to_lang, refresh=False):
        """Returns whether or not the translate server supports the given
        language pair
        """

        return (from_lang, to_lang) in self.language_pairs(refresh=refresh)

    def _request(self, method, **kwargs):
        """Convenience function to call an API function for the given client
        and return parsed JSON, or raise a TranslateException on error.
        """

        url = self.base_url + method

        try:
            req = requests.get(url, timeout=self.timeout, params=kwargs)
        except requests.exceptions.RequestException as exc:
            raise translate.client.exceptions.HTTPException(repr(exc))

        if req.status_code != 200:
            raise TranslateException.from_response(req)

        obj = json.loads(req.text)

        return obj

    def _post_request(self, method, **kwargs):
        """Similar """

        url = self.base_url + method

        try:
            req = requests.post(url, timeout=self.timeout, data=kwargs)
        except requests.exceptions.RequestException as exc:
            raise translate.client.exceptions.HTTPException(repr(exc))

        if req.status_code != 200:
            raise TranslateException.from_response(req)

        obj = json.loads(req.text)

        return obj
