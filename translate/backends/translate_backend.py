# -*- coding: utf-8 -*-

from translate import log
from translate.backend import IBackend, TranslationException

import requests
import json

import logging
logging.basicConfig(level=logging.DEBUG)


class TranslateBackend(IBackend):
    """This backend is simply a proxy to another instance of the translate
    server, and will forward any possible requests to it.
    """

    name = "Translate"
    description = "Interface to another instance of the translate server"
    url = 'https://github.com/boredomist/translate'
    preference = 10
    language_pairs = []

    def activate(self, config):
        self.config = config

        self.timeout = self.config.get('timeout', 5)

        if not self.config.get('active', True):
            return False

        if self.config.get('host') is None:
            logging.error("Don't know which host to use! aborting.")
            return False

        if self.config.get('port') is None:
            self.config['port'] = 5151

            logging.warning("Don't know which port to use, defaulting to {0}"
                            .format(self.config['port']))

        self.api_url = 'http://{0}:{1}/api/v1/'.format(self.config['host'],
                                                       self.config['port'])

        try:
            pairs = self.api_request('pairs').get('pairs', [])

            # JSON gives us 2 elem arrays instead of tuples
            self.language_pairs = [(p[0], p[1]) for p in pairs]

            if len(self.language_pairs) == 0:
                log.error('No language pairs available, aborting')
                return False

        except requests.exceptions.RequestException:
            log.error('Failed to load pairs, aborting.')
            return False

        return True

    def deactivate(self):
        pass

    def translate(self, text, from_lang, to_lang):

        try:
            params = {'from': from_lang, 'to': to_lang, 'text': text}

            resp = self.api_request('translate', **params)
            translated = resp.get('result')

            if translated is None:
                raise TranslationException('Server returned bad data: {0}'
                                           .format(resp))

            return translated

        except requests.exceptions.RequestException as exc:
            raise TranslationException('Request failed: {0}'.format(exc))

    def api_request(self, method, **kwargs):
        try:
            # TODO: handle 400 errors
            req = requests.get(self.api_url + method, params=kwargs,
                               timeout=self.timeout)
            return json.loads(req.text)

        except requests.exceptions.RequestException as exc:
            log.error('Translate API request {0}, params={1} failed!'
                      .format(method, kwargs))
            log.error(repr(exc))
            raise
