import pytest

import translate
import translate.backend

mgr = None


def setup_module():
    global mgr
    mgr = translate.backend.BackendManager({
        'dummy': {'active': True},
        'test_backend': {'foo': 'bar'}
    })


class TestBackendManager:

    def setup_class(self):
        self.mgr = mgr

    def test_default_loads(self):
        assert len(self.mgr.backends) != 0
        modules = [m.__module__ for m in self.mgr.backends]
        assert 'dummy' in modules

    def test_bad_backend(self):
        from tests.test_backends.bad_backend import BadBackend

        # it's a subclass, but doesn't implement all methods, so it's not an
        # instance
        assert issubclass(BadBackend, translate.backend.IBackend)

        # ABCMeta should stop this from being instantiated
        backend = None
        with pytest.raises(TypeError):
            backend = BadBackend()

        assert not isinstance(backend, translate.backend.IBackend)

    def test_load_extra(self):
        before = self.mgr.backends[:]
        self.mgr.load_backends('tests/test_backends')
        diff = set(self.mgr.backends) - set(before)

        assert 'bad_backend' not in [m.__module__ for m in self.mgr.backends]

        assert len(diff) != 0

        modules = [m.__module__ for m in list(diff)]

        assert 'test_backend' in modules

    def test_find_best(self):
        backend = self.mgr.find_best('en', 'en')

        assert backend.name == 'Test Backend'

    def test_find_all(self):
        backends = self.mgr.find_all('en', 'en')

        assert 'Test Backend' in [b.name for b in backends]
        assert 'Dummy' in [b.name for b in backends]

        prefs = [b.preference for b in backends]
        assert sorted(prefs) == prefs
