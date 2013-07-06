from translate.backends.yandex import YandexBackend

import requests
import json
import os

api_key = os.environ.get('YANDEX_KEY')

if api_key is None:
    print("Don't have an API key for yandex, not continuing...")
else:
    class TestYandex:

        def setup_class(self):
            self.backend = YandexBackend()

        def test_init(self):
            assert self.backend.activate({'key': api_key})
            assert len(self.backend.language_pairs) != 0

        def test_translate(self):
            pair = self.backend.language_pairs[0]

            trans = self.backend.translate('hello', pair[0], pair[1])
            assert trans is not None
