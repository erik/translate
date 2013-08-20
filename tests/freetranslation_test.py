from translate.backends.freetranslation import FreeTranslationBackend, API_URL

import os
import requests
import json

try:
    # If this times out, just give up with the test
    r = requests.get(API_URL, timeout=5)

    class TestFreeTranslation:

        def setup_class(self):
            self.backend = FreeTranslationBackend()

        def test_init(self):
            api_key = os.environ.get('FREETRANSLATION_KEY')

            assert self.backend.activate({'key': api_key,
                                          'active': True})
            assert len(self.backend.language_pairs) != 0

        def test_translate(self):
            pair = self.backend.language_pairs[0]

            trans = self.backend.translate('hello', pair[0], pair[1])
            assert trans is not None

except:
    print('Skipping apertiumweb backend tests')
