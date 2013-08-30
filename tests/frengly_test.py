from translate.backends.frengly import FrenglyBackend, API_URL

import os
import requests
import json

try:
    # If this times out, just give up with the test
    r = requests.get(API_URL, timeout=5)

    class TestFrengly:

        def setup_class(self):
            self.backend = FrenglyBackend()

        def test_init(self):
            email, passw = os.environ.get('FRENGLY_EMAIL'), \
                           os.environ.get('FRENGLY_PASSWORD')

            assert self.backend.activate({'email': email, 'password': passw,
                                          'active': True})

        def test_translate(self):
            # get pairs that are english -> ?
            pairs = filter(lambda p: p[0] == 'en', self.backend.language_pairs)

            trans = self.backend.translate('hello', pairs[0][0], pairs[0][1])
            assert trans

except:
    print('Skipping frengly backend tests')
