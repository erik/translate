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

import translate.client

from translate.backend import IBackend
from translate.exceptions import TranslationException

import logging
log = logging.getLogger(__name__)


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

        try:
            self.client = translate.client.Client(config['host'],
                                                  port=self.config['port'])

            self.language_pairs = self.client.language_pairs()
        except translate.client.exceptions.TranslateException as exc:
            log.error("Failed to setup client: " + str(exc))
            return False

        if len(self.language_pairs) == 0:
            log.error('No language pairs available, aborting')
            return False

        return True

    def deactivate(self):
        pass

    def translate(self, text, from_lang, to_lang):

        if not self.client.can_translate(from_lang, to_lang):
            raise TranslationException("Can't translate given pair ({0},{1})"
                                       .format(from_lang, to_lang))

        try:
            return self.client.translate(text, from_lang, to_lang)

        except translate.client.exceptions.TranslateException as exc:
            raise TranslationException("Server failed to translate text: "
                                       + repr(exc))
