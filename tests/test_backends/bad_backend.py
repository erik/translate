import translate.backend

class BadBackend(translate.backend.IBackend):
    name = "Bad Backend"
    description = "This should fail to load"
    preference = 1000

    def translate(self, _from, _to, text):
        return text
