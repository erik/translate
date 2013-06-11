# -*- coding: utf-8 -*-

from translate.backend import IBackend


class DummyBackend(IBackend):
    """This dummy backend is a temporary test of translator abilities until
    some real backends are implemented.
    """

    def name(self):
        return "Dummy"

    def description(self):
        return "A dummy implementation of a translation backend"

    def preference(self):
        return 0

    def translate(self, text, from_lang, to_lang):
        return text

    def language_pairs(self):
        return [('en', 'en')]