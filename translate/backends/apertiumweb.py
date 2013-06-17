# -*- coding: utf-8 -*-

from translate import log
from translate.backend import IBackend

import requests
import json

API_URL = 'http://api.apertium.org/json/'
API_TIMEOUT = 5
API_ERRORS = {
    400: 'Bad parameters',
    451: 'Not supported language pair',
    452: 'Not supported format',
    500: 'Unexpected error',
    552: 'Traffic limit reached'
}


class ApertiumBackend(IBackend):
    name = "Apertium Web"
    description = """Web translation API using the free/open-source machine
translation platform Apertium"""
    preference = 40

    def __init__(self, config):
        self.config = config.get('apertiumweb', dict())

        self.activated = False

        if not self.config.get('active', True):
            return

        self.key = self.config.get('key')
        self.timeout = self.config.get('timeout', 5)

        response = self.api_request('listPairs')

        if response.get('responseStatus') != 200:
            log.warning('Apertium Web API request failed, bailing out')
            return

        self.pairs = []

        for pair in response.get('responseData'):
            source = pair.get('sourceLanguage')
            dest = pair.get('targetLanguage')

            self.pairs.append((source, dest))

        # just in case the API returns duplicates for whatever reason
        self.pairs = list(set(self.pairs))
        self.activated = True

    def translate(self, text, from_lang, to_lang):
        langpair = "{0}|{1}".format(from_lang, to_lang)

        resp = self.api_request('translate', q=text, langpair=langpair,
                                format="txt")

        # TODO: Actual error handling should go here
        if resp.get('responseStatus') != 200:
            error = API_ERRORS.get(resp.get('responseStatus'), 'Unknown error')
            log.error(error)
            return None

        return resp.get('responseData').get('translatedText')

    def language_pairs(self):
        return self.pairs

    def api_request(self, method, **kwargs):
        if self.key is not None:
            kwargs['key'] = self.key

        r = requests.get(API_URL + method, params=kwargs, timeout=self.timeout)

        return json.loads(r.text)
