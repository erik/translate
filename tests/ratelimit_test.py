# -*- coding: utf-8 -*-

import flask
import json
import time

import translate
from translate.app import app
from translate.app import views
from translate.app.ratelimit import RateLimit
from translate.backend import BackendManager


class TestRateLimit():
    def setup_class(self):
        views.manager = BackendManager({})
        app.config['TESTING'] = True

        # 5 reqs / 1 sec
        RateLimit.enabled = True
        RateLimit.limit = 5
        RateLimit.per = 1

        self.client = app.test_client()

        self.last_req = time.time()

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

            for header in ['X-RateLimit-Remaining', 'X-RateLimit-Limit']:
                assert header in resp.headers

    def test_under_limit(self):
        RateLimit.limit_dict = {}
        self.start = time.time()
        for i in xrange(5):
            assert time.time() < self.start + RateLimit.per
            resp = self.client.get('/api/v1/pairs')

            js = json.loads(resp.data)
            assert js is not None

            assert int(resp.headers['X-RateLimit-Remaining']) == 5 - (i + 1)

        resp = self.client.get('/api/v1/pairs')
        assert json.loads(resp.data) is not None
        assert resp.status_code == 429

        self.last_req = time.time()

    def test_over_limit(self):
        assert time.time() < self.last_req + RateLimit.per
        resp = self.client.get('/api/v1/pairs')

        assert resp.status_code == 429
        js = json.loads(resp.data)
        assert js is not None

        assert js['details']['limit'] == RateLimit.limit
        assert js['details']['per'] == RateLimit.per

    def test_limit_clear(self):
        # wait until old requests expire
        secs = (self.last_req + RateLimit.per + .5) - time.time()

        if secs > 0:
            time.sleep(secs)

        self.start = time.time()
        for i in xrange(5):
            assert time.time() < self.start + RateLimit.per
            resp = self.client.get('/api/v1/pairs')
            print(repr(resp.headers))
            assert json.loads(resp.data) is not None

            # TODO: I'm not sure if this should be 5 - (i + 1)
            assert int(resp.headers['X-RateLimit-Remaining']) == 5 - (i)

        resp = self.client.get('/api/v1/pairs')
        assert json.loads(resp.data) is not None
        assert resp.status_code == 429
