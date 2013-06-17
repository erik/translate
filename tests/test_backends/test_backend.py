import translate.backend

class TestBackend(translate.backend.IBackend):
    name = "Test Backend"
    description = "A test backend"
    preference = 1000

    def __init__(self, config):
        pass

    def language_pairs(self): return [('en', 'en')]

    def translate(self, _from, _to, text):
        return text
