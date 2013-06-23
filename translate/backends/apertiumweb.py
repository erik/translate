# -*- coding: utf-8 -*-

from translate import log
from translate.backend import IBackend

import requests
import json

import logging
logging.basicConfig(level=logging.DEBUG)


API_URL = 'http://api.apertium.org/json/'
API_TIMEOUT = 5
API_ERRORS = {
    400: 'Bad parameters',
    451: 'Not supported language pair',
    452: 'Not supported format',
    500: 'Unexpected error',
    552: 'Traffic limit reached'
}


class ApertiumWebBackend(IBackend):
    name = "Apertium Web"
    description = ("Web translation API using the free/open-source machine" +
                   " translation platform Apertium")
    preference = 40
    language_pairs = []

    def activate(self, config):
        self.config = config

        if not self.config.get('active', True):
            return False

        self.key = self.config.get('key')
        self.timeout = self.config.get('timeout', 5)

        response = self.api_request('listPairs')

        if response.get('responseStatus') != 200:
            log.warning('Apertium Web API request failed, bailing out')
            return False

        self.language_pairs = []

        for pair in response.get('responseData'):
            source = pair.get('sourceLanguage')
            dest = pair.get('targetLanguage')

            self.language_pairs.append((source, dest))

        # just in case the API returns duplicates for whatever reason
        self.language_pairs = list(set(self.language_pairs))
        return True

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

    def deactivate(self):
        pass

    def api_request(self, method, **kwargs):
        if self.key is not None:
            kwargs['key'] = self.key

        try:
            r = requests.get(API_URL + method, params=kwargs,
                             timeout=self.timeout)
        except requests.exceptions.RequestException as exc:
            log.error('API request {0} params={1} failed!'
                      .format(method, kwargs))
            log.error(repr(exc))
            return dict()

        return json.loads(r.text)
