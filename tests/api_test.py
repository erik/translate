# -*- coding: utf-8 -*-

import json
import time

from translate.app import app, views
from translate.app.ratelimit import RateLimit
from translate.backend import BackendManager


class TestAPIv1():

    def setup_class(self):
        views.manager = BackendManager({})
        app.config['TESTING'] = True
        self.client = app.test_client()

    def teardown_class(self):
        pass

    def test_jsonp(self):
        for path in ['/api/v1/pairs?callback=foo',
                     '/api/v1/translators?callback=foo',
                     '/api/v1/translate?callback=foo',
                     '/api/v1/ratelimit?callback=foo']:
            resp = self.client.get(path)
            assert resp.data.startswith('foo(')

            # Strip jsonp (doesn't parse here)
            assert json.loads(resp.data[4:-1]) is not None

    def test_pairs_good_input(self):
        for path in ['/api/v1/pairs']:
            resp = self.client.get(path)
            assert resp.status_code == 200
            js = json.loads(resp.data)
            assert js is not None
            assert 'pairs' in js

    def test_translators_good_input(self):
        for path in ['/api/v1/translators']:
            resp = self.client.get(path)
            assert resp.status_code == 200
            js = json.loads(resp.data)
            assert js is not None
            assert 'backends' in js

    def test_translate_bad_input(self):
        for params in ['', 'from=foo&to=bar&text=baz', 'to=bar&text=baz',
                       'text=baz', 'from=en&text=foo&to=bad-lang',
                       'from=en&to=en&text=']:
            resp = self.client.get('/api/v1/translate?' + params)

            assert resp.status_code != 200

            js = json.loads(resp.data)

            assert js is not None

    def test_errors(self):
        """Make sure API functions return proper error codes/information"""

        # Kill the limiter for now
        RateLimit.enabled = False

        # Test format of error messages
        resp = self.client.get('/api/v1/translate')
        assert resp.status_code == 452
        js = json.loads(resp.data)

        assert js is not None

        for pair in [('status', 'Translation error'),
                     ('url', 'http://localhost/api/v1/translate'),
                     ('code', 452),
                     ('details', {})]:
            assert js[pair[0]] == pair[1]

        # Bad params
        for params in ['', 'from=foo&to=bar', 'from=foo&to=bar&text=',
                       'from=foo&text=bar']:
            resp = self.client.get('/api/v1/translate?' + params)
            assert resp.status_code == 452
            assert resp.status == "452 Translation error"

            js = json.loads(resp.data)
            assert js is not None

        # No translators
        resp = self.client.get('/api/v1/translate?from=foo&to=bar&text=foobar')
        assert resp.status_code == 454

        js = json.loads(resp.data)
        assert js['details']['from'] == 'foo'
        assert js['details']['to'] == 'bar'
        assert js['details']['text'] == 'foobar'

        # No translators (due to exclusion)
        resp = self.client.get('/api/v1/translate?from=en&to=en&text=foobar&\
exclude=Dummy')

        js = json.loads(resp.data)
        assert js['details']['from'] == 'en'
        assert js['details']['to'] == 'en'
        assert js['details']['text'] == 'foobar'

        assert resp.status_code == 454

    def test_batch_empty(self):
        resp = self.client.post('/api/v1/batch',
                                data={'urls': json.dumps([])})

        print(resp.data)

        assert json.loads(resp.data) == []
        assert resp.status_code == 200

    def test_batch_good(self):
        urls = ['/api/v1/pairs', '/api/v1/translators',
                '/api/v1/pairs']

        resp = self.client.post('/api/v1/batch',
                                data={'urls': json.dumps(urls)})

        js = json.loads(resp.data)
        assert len(js) == 3
        assert resp.status_code == 200

        assert js[0]['status'] == 200
        assert js[1]['status'] == 200
        assert js[2]['status'] == 200

    def test_batch_mixed(self):
        urls = ['/api/v1/pairs', '/api/v1/translate?from=bad',
                '/api/v1/translators']

        resp = self.client.post('/api/v1/batch',
                                data={'urls': json.dumps(urls)})

        js = json.loads(resp.data)
        assert len(js) == 3
        assert resp.status_code == 200

        assert js[0]['status'] == 200
        assert js[1]['status'] == 452
        assert js[2]['status'] == 200

    def test_ratelimit_info(self):
        RateLimit.limit_dict = {}
        RateLimit.enabled = True
        RateLimit.limit = 5
        RateLimit.per = 5

        reset = time.time() + 100
        RateLimit.reset = reset

        resp = self.client.get('/api/v1/ratelimit')

        assert resp.status_code == 200
        assert json.loads(resp.data) == {
            'reset': reset,
            'limit': 5,
            'per': 5,
            'methods': {}
        }

        for _ in xrange(6):
            self.client.get('/api/v1/translate')
            self.client.get('/api/v1/translators')

        self.client.get('/api/v1/pairs')

        resp = self.client.get('/api/v1/ratelimit')
        assert resp.status_code == 200

        js = json.loads(resp.data)
        assert js['limit'] == 5
        assert js['per'] == 5
        assert js['reset'] == reset
        assert js['methods'] == {
            '/api/v1/translate': 0,
            '/api/v1/translators': 0,
            '/api/v1/pairs': 4
        }
