import translate
import translate.backend

mgr = None


def setup_module():
    global mgr
    mgr = translate.backend.BackendManager()


class TestBackendManager:

    def setup_class(self):
        self.mgr = mgr

    def test_default_loads(self):
        assert len(self.mgr.backends) == 1
        assert self.mgr.backends[0].__module__ == 'translate.backends.dummy'

    def test_load_extra(self):
        before = self.mgr.backends[:]
        self.mgr.load_backends('tests/test_backends')
        diff = set(self.mgr.backends) - set(before)

        assert len(diff) == 1
        assert list(diff)[0].__module__ == 'tests.test_backends.test_backend'

    def test_find_best(self):
        backend = self.mgr.find_best('en', 'en')

        assert backend.name == 'Test Backend'
