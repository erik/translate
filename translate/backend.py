# -*- coding: utf-8 -*-

import logging
import inspect

log = logging.getLogger(__name__)


class BackendManager:
    """Handles the loading and management of various translation service
    backends."""

    def __init__(self):
        self.backends = []

        # Load the default backends
        self.load_backends('translate.backends')

    def load_backends(self, module_name):
        """Load all backends from the given module name"""

        def class_filter(klass):
            return inspect.isclass(klass) and issubclass(klass, IBackend) and \
                klass != IBackend

        for name, module in inspect.getmembers(__import__(module_name),
                                               inspect.ismodule):
            print(name + repr(module))
            for _, plugin in inspect.getmembers(module, class_filter):
                print("Loading backend {0}... ".format(plugin.name))

                backend = plugin()
                self.backends.append(backend)

    def find_best(self, src, dst):
        """Find the best backend service for a given language pair"""

        best = (None, -1)

        print(repr(self.backends))

        for backend in self.backends:
            if (src, dst) in backend.language_pairs():
                if backend.preference > best[1]:
                    best = (backend, backend.preference)

        return best[0]


class IBackend:
    """Backend interface definition for any additional backends.

    Every backend must implement inherit IBackend and define the
    members/functions present here.
    """

    def translate(self, text, from_lang, to_lang):
        """Translate the given text from `from_lang` to `to_lang`.

        A backend will only receive this function call if has already specified
        that it can accept the given from,to pair.
        """
        pass

    def language_pairs(self):
        """Return a list of tuples containing ("from-lang", "to-lang") to
        indicate language pair support.

        The languages should be in ISO-639_ format, using ISO-639-1 if possible
        and falling back to ISO-639-2 if necessary.

        .. _ISO-639: http://www.loc.gov/standards/iso639-2/php/English_list.php
        """
        pass

    def preference():
        """Return an integer representing the overall precedence this
        translation backend should use.

        If two backends overlap for a language pair, the one with the highest
        preference is used.

        Higher values indicate a higher precedence.
        """
        pass

    def name():
        """Name of this translation backend."""
        pass

    def description():
        """Short description of this translation backend."""
        pass
