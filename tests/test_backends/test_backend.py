import translate.exceptions

import tests.backend_test

class TestBackend(translate.backend.IBackend):
    DEACTIVATE_WAS_CALLED = False

    name = "Test Backend"
    description = "A test backend"
    url = 'example.com'
    preference = 0
    language_pairs = [('en', 'en')]

    def activate(self, config):
        assert config['foo'] == 'bar'
        return True

    def deactivate(self):
        # Just so we know it was called.
        tests.backend_test.DEACTIVATE_WAS_CALLED = True

    def translate(self, text, from_lang, to_lang):

        if (from_lang, to_lang) not in self.language_pairs:
            raise translate.exceptions.TranslationException('Bad data')

        return text
