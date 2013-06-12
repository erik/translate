import translate.backend

class TestBackend:
    name = "Test Backend"
    description = "A test backend"
    priority = 100

    def language_pairs(self): return [('en', 'en')]

    def translate(self, _from, _to, text):
        return text
