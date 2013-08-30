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
import itertools

import logging
log = logging.getLogger(__name__)


API_URL = 'http://syslang.com'
API_TIMEOUT = 5

# Account can be freely set up at http://www.frengly.com/
#
# API call is: GET http://syslang.com?src=LANG&dest=LANG&text=STRING&
#                  email=EMAIL&password=PASSWORD&outformat=json
#
# JSON output format is:
#
# {"text":"string to translate", "dest":"lang_code",
#  "translation":"translated string","action":"translateREST",
#  "src":"lang_code"}
# sa9383@adzek.com

# There's no way of requesting this, so hardcode what the site says.
# XXX: Apparently can translate using any of these as the from or to lang, but
#      I'm not sure if they all work.
API_LANGS = ['ar', 'bg', 'hr', 'cs', 'da', 'nl', 'en', 'tl', 'fi', 'fr', 'de',
             'el', 'iw', 'hi', 'hu', 'id', 'ga', 'it', 'ja', 'ko', 'la', 'no',
             'fa', 'pl', 'pt', 'ro', 'ru', 'sr', 'sk', 'es', 'sv', 'th', 'tr',
             'vi', 'zh-CN', 'zh-TW']


class FrenglyBackend(IBackend):
    name = 'Frengly'
    description = 'Free translation service from frengly.com'
    url = 'http://frengly.com'
    # The results seem REALLY wonky (at least en-de), low default preference.
    preference = 1
    # Generate all possible language pairs
    language_pairs = list(itertools.combinations(API_LANGS, 2))

    def activate(self, config):
        self.config = config

        if not self.config.get('active'):
            return False

        if not config.get('email') or not config.get('password'):
            log.error("Don't have a proper email/password set up.")
            return False

        self.timeout = self.config.get('timeout', API_TIMEOUT)

        self.email = config['email']
        self.password = config['password']

        return True

    def deactivate(self):
        pass

    def translate(self, text, from_lang, to_lang):
        params = {'text': text, 'dest': to_lang, 'src': from_lang,
                  'email': self.email, 'password': self.password,
                  'outformat': 'json'}

        try:
            r = requests.get(API_URL, params=params, timeout=self.timeout)
            print(r.text)
            trans = json.loads(r.text)['translation']

            # Service seems to ignore exceptions and just return the same
            # thing on error...
            if trans == text:
                raise TranslationException('Service seems to have failed to \
translate text')

            return trans

        except (ValueError, KeyError):
            raise TranslationException('Server returned bad JSON: %s', r.text)

        except requests.exceptions.RequestException as exc:
            log.error('Translation request (params=%s) failed: %s',
                      repr(params), exc)
            raise TranslationException(exc)
