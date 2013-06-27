# -*- coding: utf-8 -*-

from translate.backend import IBackend, TranslationException


class DummyBackend(IBackend):
    """This dummy backend is a temporary test of translator abilities until
    some real backends are implemented.
    """

    name = "Dummy"
    description = "A dummy implementation of a translation backend"
    preference = 0
    language_pairs = [('en', 'en')]

    def activate(self, config):
        self.config = config

        return self.config.get('active', False)

    def deactivate(self):
        pass

    def translate(self, text, from_lang, to_lang):
        if (from_lang, to_lang) not in self.language_pairs:
            raise TranslationException('Bad input')

        return text
