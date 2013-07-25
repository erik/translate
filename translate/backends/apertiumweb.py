# -*- coding: utf-8 -*-

from translate.backend import IBackend
from translate.exceptions import TranslationException

import requests
import json

import logging
log = logging.getLogger(__name__)


API_URL = 'http://api.apertium.org/json/'
API_TIMEOUT = 5
API_ERRORS = {
    -1:  'Request timed out',
    400: 'Bad parameters',
    451: 'Not supported language pair',
    452: 'Not supported format',
    500: 'Server error (500)',
    552: 'Traffic limit reached'
}


class ApertiumWebBackend(IBackend):
    name = "Apertium Web"
    description = "Web translation API using the free/open-source machine\
translation platform Apertium"
    url = 'http://api.apertium.org'
    preference = 40
    language_pairs = []

    def activate(self, config):
        self.config = config

        if not self.config.get('active', True):
            return False

        self.key = self.config.get('key')
        self.timeout = self.config.get('timeout', API_TIMEOUT)

        response, _ = self.api_request('listPairs')

        if response.get('responseStatus') != 200:
            log.warning('Apertium Web API request failed, bailing out')
            return False

        self.language_pairs = []

        for pair in response.get('responseData', {}):
            source = pair.get('sourceLanguage')
            dest = pair.get('targetLanguage')

            if source is None or dest is None:
                log.error('Badly formatted responseData, skipping')
                continue

            self.language_pairs.append((source, dest))

        # Just in case the API returns duplicates for whatever reason
        self.language_pairs = list(set(self.language_pairs))

        if len(self.language_pairs) == 0:
            log.error('Got zero translation pairs, aborting.')
            return False

        return True

    def translate(self, text, from_lang, to_lang):
        langpair = "{0}|{1}".format(from_lang, to_lang)

        resp, req = self.api_request('translate', q=text, langpair=langpair,
                                     format="txt")

        status = resp.get('responseStatus', -1)
        if status != 200:
            try:
                error = API_ERRORS[status]
            # Unknown status
            except KeyError:
                error = "Unknown error occurred: %d".format(status)

            log.error(error)

            raise TranslationException(repr(error))

        return resp.get('responseData').get('translatedText')

    def deactivate(self):
        pass

    def api_request(self, method, **kwargs):
        if self.key is not None:
            kwargs['key'] = self.key

        try:
            r = requests.get(API_URL + method, params=kwargs,
                             timeout=self.timeout)
            return json.loads(r.text), r

        except requests.exceptions.RequestException as exc:
            log.error('API request {0} params={1} failed!'
                      .format(method, kwargs))
            log.error(repr(exc))

            return dict(), exc
