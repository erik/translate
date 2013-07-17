# -*- coding: utf-8 -*-

import json
import time

from translate.app import app
from translate.app import views
from translate.app.ratelimit import RateLimit
from translate.backend import BackendManager


class TestRateLimit():

    reset = 0

    def setup_class(self):
        views.manager = BackendManager({})
        app.config['TESTING'] = True

        # 5 reqs / 1 sec
        # Do this two different ways so when test is run as a standalone, still
        # works. Probably indicative of bad design, but works for purposes of
        # this test.
        RateLimit.enable(limit=5, per=1)
        app.config['SERVER']['ratelimit'] = {
            'enabled': True,
            'limit': 5,
            'per': 1
        }

        self.client = app.test_client()

    def teardown_class(self):
        RateLimit.enabled = False
        RateLimit.limit_dict = {}

    def test_returns_limit_headers(self):
        for path in ['/api/v1/pairs',
                     '/api/v1/translators',
                     '/api/v1/translate']:
            resp = self.client.get(path)

            js = json.loads(resp.data)
            assert js is not None

            for header in ['X-RateLimit-Remaining', 'X-RateLimit-Limit',
                           'X-RateLimit-Duration', 'X-RateLimit-Reset']:
                assert header in resp.headers

    def test_under_limit(self):
        # Wait for current window to expire
        secs = RateLimit.reset - time.time()
        if secs > 0:
            print("Sleeping for " + str(secs))
            time.sleep(secs)

        reset = RateLimit.reset + RateLimit.per

        for i in xrange(RateLimit.limit):
            assert time.time() < reset
            resp = self.client.get('/api/v1/pairs')

            js = json.loads(resp.data)
            assert js is not None

            assert int(resp.headers['X-RateLimit-Duration']) == RateLimit.per
            assert float(resp.headers['X-RateLimit-Reset']) == reset
            assert int(resp.headers['X-RateLimit-Remaining']) == \
                RateLimit.limit - (i + 1)

        TestRateLimit.reset = reset

        resp = self.client.get('/api/v1/pairs')
        assert json.loads(resp.data) is not None
        assert resp.status_code == 429

    def test_over_limit(self):
        assert time.time() < TestRateLimit.reset
        resp = self.client.get('/api/v1/pairs')

        assert resp.status_code == 429
        js = json.loads(resp.data)
        assert js is not None

        assert js['details']['limit'] == RateLimit.limit
        assert js['details']['per'] == RateLimit.per
        assert js['details']['reset'] == RateLimit.reset

    def test_others_not_over_limit(self):
        # Make sure we can still access other methods while throttled for
        # /pairs
        assert time.time() < TestRateLimit.reset
        resp = self.client.get('/api/v1/translators')

        assert resp.status_code == 200

    def test_limit_clear(self):
        # wait until old requests expire
        secs = RateLimit.reset - time.time()

        if secs > 0:
            print("Sleeping for " + str(secs))
            time.sleep(secs)

        TestRateLimit.reset = RateLimit.reset + RateLimit.per

        for i in xrange(RateLimit.limit):
            assert time.time() < TestRateLimit.reset

            resp = self.client.get('/api/v1/pairs')
            print(repr(resp.headers))
            assert json.loads(resp.data) is not None
            assert int(resp.headers['X-RateLimit-Remaining']) ==\
                RateLimit.limit - (i + 1)

        resp = self.client.get('/api/v1/pairs')
        assert json.loads(resp.data) is not None
        assert resp.status_code == 429

    def test_batch_over_limit(self):
        # wait until old requests expire
        secs = RateLimit.reset - time.time()

        if secs > 0:
            print("Sleeping for " + str(secs))
            time.sleep(secs)

        TestRateLimit.reset = RateLimit.reset + RateLimit.per

        urls = ['/api/v1/pairs'] * (RateLimit.limit + 1)
        resp = self.client.post('/api/v1/batch',
                                data={'urls': json.dumps(urls)})

        assert resp.status_code == 200

        js = json.loads(resp.data)

        assert len(js) == len(urls)

        for i in xrange(RateLimit.limit):
            rem = int(js[i]['headers']['X-RateLimit-Remaining'])

            assert rem == RateLimit.limit - (i + 1)
            assert js[i]['status'] == 200

        assert js[RateLimit.limit]['status'] == 429
