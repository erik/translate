import subprocess

from translate.backends.apertium import ApertiumBackend


# Only run these tests if apertium exectutable exists

try:
    subprocess.check_call(['which', 'apertium'])

    backend = None

    def test_init():
        global backend
        backend = ApertiumBackend()
        assert backend.activate(dict())
        assert backend.preference != -1
        assert len(backend.language_pairs) != 0

    def test_translate():
        pair = backend.language_pairs[0]

        trans = backend.translate('hello', pair[0], pair[1])
        assert trans is not None

except subprocess.CalledProcessError:
    print('Skipping apertium backend')
