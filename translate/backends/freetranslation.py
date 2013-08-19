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


from translate.backend import IBackend
from translate.exceptions import TranslationException

import requests
import json

import logging
log = logging.getLogger(__name__)


API_URL = 'https://api.beglobal.com/'
API_TIMEOUT = 5
API_ERRORS = {
    401: 'Unauthorized: bad API key',
    420: 'Request failed',
    422: 'Semantic error within request',
    500: 'Internal server error'
}

# API key is passed in a request header: "Authorization: BeGlobal apiKey=KEY"


class FreeTranslationBackend(IBackend):
    name = "FreeTranslation"
    description = "Web translation service from freetranslation.com"
    url = 'http://freetranslation.com'
    preference = 30
    language_pairs = []

    def activate(self, config):
        self.config = config

        if not self.config.get('active', False):
            return False

        if 'key' not in config:
            log.error("Don't have an API key, can't proceed")
            return False

        self.key = config['key']
        self.timeout = self.config.get('timeout', API_TIMEOUT)

        resp, _ = self._api_request('languages', quality='Q1')

        self.language_pairs = []

        for obj in resp['languageExpertise']['Q1']:
            # XXX: This is ISO 639 (3 char), not 2.
            from_lang = obj['languagePair']['from']['code']
            to_lang = obj['languagePair']['to']['code']

            self.language_pairs.append((from_lang, to_lang))

        # Just in case the API returns duplicates for whatever reason
        self.language_pairs = list(set(self.language_pairs))

        if len(self.language_pairs) == 0:
            log.error('Got zero translation pairs, aborting')
            return False

        return True

    def translate(self, text, from_lang, to_lang):
        # TODO
        raise TranslationException('Not implemented yet')

    def deactivate(self):
        pass

    def _api_request(self, method, **kwargs):
        try:
            r = requests.get(API_URL + method, params=kwargs,
                             headers={'Authorization', self.auth_header},
                             timeout=self.timeout)
            return json.loads(r.text), r

        except ValueError as exc:
            log.error('API request {0} params={1} returned bad JSON'.format(
                method, kwargs))

            return dict(), exc

        except requests.exceptions.RequestException as exc:
            log.error('API request {0} params={1} failed!'
                      .format(method, kwargs))
            log.error(repr(exc))

            return dict(), exc

    def _api_post_request(self, path, **params):
        # TODO
        pass
