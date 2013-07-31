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
translate.backends.yandex
~~~~~~~~~~~~~~~~~~~~~~~~~

Backend for Yandex's free online translation service. Support is mostly for
Slavic languages, with a few large European languages also available.
API documentation, as well as information on getting an API key (which is
required) can be found in the developer documentation:

http://api.yandex.com/translate/
"""

from translate import log
from translate.backend import IBackend
from translate.exceptions import TranslationException

import translate.utils

import requests
import json

API_URL = 'https://translate.yandex.net/api/v1.5/tr.json/'
API_TIMEOUT = 5
API_ERRORS = {
    -1:  'Request timed out',
    401: 'Invalid API key',
    402: 'API key has been blocked',
    403: 'Daily request limit has been reached',
    404: 'Daily data limit has been reached',
    413: 'Text size exceeds the maximum allowed',
    422: 'Text could not be translated',
    501: 'Specified translation direction is not supported'
}
# Yandex claims to only translate 10k bytes at a time, but seems to 500 on
# texts that size, so try 8k instead.
API_SIZE_LIMIT = 8 * 1000


class YandexBackend(IBackend):
    name = "Yandex"
    description = "Free online translation service from Yandex"
    url = "http://api.yandex.com/translate/"
    preference = 40
    language_pairs = []

    def activate(self, config):
        self.config = config

        if not config.get('active', True):
            return False

        if config.get('key') is None:
            log.warning("Can't use Yandex service without an API key...")
            return False

        self.key = config['key']
        self.timeout = config.get('timeout', API_TIMEOUT)

        js, _ = self.api_request('getLangs', ui='en')

        pairs = []
        for pair in js.get('dirs', []):
            langs = pair.split('-')
            pairs.append((langs[0], langs[1]))

        pairs = list(set(pairs))

        if len(pairs) == 0:
            log.warning("Yandex supports no translation pairs? Something is\
wrong.")
            return False

        self.language_pairs = pairs
        return True

    def deactivate(self):
        pass

    def translate(self, text, from_lang, to_lang):

        results = []
        # Split up requests into blocks of proper size
        # FIXME: Bytesize vs charsize.
        for chunk in translate.utils.chunk_string(text, API_SIZE_LIMIT):
            pair = "{0}-{1}".format(from_lang, to_lang)
            js, req = self.api_request('translate', text=chunk, lang=pair)

            if js.get('code', -1) != 200:
                error = API_ERRORS.get(js.get('code', -1), "Unknown error!")

                if error is None:
                    raise TranslationException(repr(req))
                else:
                    raise TranslationException(repr(error))

            # Returns an array, so join with new lines
            results.append('\n'.join(js.get('text')))

        return '\n'.join(results)

    def api_request(self, method, **kwargs):
        kwargs['key'] = self.key

        try:
            req = requests.get(API_URL + method, params=kwargs,
                               timeout=self.timeout)
            return json.loads(req.text), req
        except requests.exceptions.RequestException as exc:
            log.error('API request {0} params={1} failed'.
                      format(method, kwargs))
            log.error(repr(exc))

            return {}, exc
