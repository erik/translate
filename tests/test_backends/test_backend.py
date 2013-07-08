import translate.backend


class TestBackend(translate.backend.IBackend):
    name = "Test Backend"
    description = "A test backend"
    url = 'example.com'
    preference = 0
    language_pairs = [('en', 'en')]

    def activate(self, config):
        assert config['foo'] == 'bar'
        return True

    def deactivate(self):
        pass

    def translate(self, text, from_lang, to_lang):

        if (from_lang, to_lang) not in self.language_pairs:
            raise translate.backend.TranslationException('Bad data')

        return text
