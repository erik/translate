import translate.backend


class TestBackend(translate.backend.IBackend):
    name = "Test Backend"
    description = "A test backend"
    preference = 1000
    language_pairs = [('en', 'en')]

    def activate(self, config):
        return True

    def deactivate(self):
        pass

    def translate(self, _from, _to, text):
        return text
