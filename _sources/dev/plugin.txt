Plugin Documentation
====================

If you'd like to add an additional translation system to translate, the process
is rather simple.

In short, each of the functions and class members described in the code
documentation below must be implemented in your plugin class.

Plugin Loading
--------------

Plugins live in :code:`/translate/backends/<backendname>.py`. Technically, they
can be stored and loaded from anywhere, but the backend manager currently only
acknowledges the "official" plugin directory. At some later point, it will be
possible to specify a custom directory.

Plugin Lifecycle
~~~~~~~~~~~~~~~~

On server startup, the `BackendManager` class iterates through the plugin
directory, loading each Python module it finds, and builds a list of classes
within these modules that subclass `translate.backend.IBackend`.

The manager then attempts to construct each of these classes, skipping to the
next if the `__init__` method throws an error (likely due to a missing member).

After this, the `activate` method is called, and is passed a dict containing the
plugin's configuration. The plugin should set the `language_pairs` class member
here if it could not be established statically.

*Do note that the class should still have a :code:`language_pairs=[]` line
regardless*

If the method returns `True`, the plugin is considered active and is added to
the list of valid plugins.

From here on, the plugin will be sent various requests for translating text.

It is excepted that a plugin will raise a TranslationException when the
:code:`translate` function is called with bad input, or the request otherwise
fails.

On server shutdown, each active plugin will have its `deactivate` method called,
where it should do any cleanup, if required.

Code Documentation
------------------
.. autoclass:: translate.backend.IBackend
   :members:
