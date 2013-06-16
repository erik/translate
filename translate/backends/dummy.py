# -*- coding: utf-8 -*-

from translate.backend import IBackend


class DummyBackend(IBackend):
    """This dummy backend is a temporary test of translator abilities until
    some real backends are implemented.
    """

    name = "Dummy"
    description = "A dummy implementation of a translation backend"
    preference = 0

    def __init__(self, config):
        self.config = config.get('dummy', dict())
        pass

    def translate(self, text, from_lang, to_lang):
        return text

    def language_pairs(self):
        return [('en', 'en')]
