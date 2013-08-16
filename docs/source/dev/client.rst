Client Documentation
--------------------

Part of translate is the client implementation, also written in Python. It
provides a very simple interface to a translate server, and relies only on the
requests library (:code:`pip install requests`).::

   from translate.client import Client

   c = Client('my.translate.server.com', port=80)

   c.can_connect() #=> True
   c.language_pairs() #=> [('en', 'es'), ('it', 'ru'), ...]
   c.translate('Hello', 'en', 'es') #=> "Hola"


Code Documentation
==================
.. automodule:: translate.client
   :members:

.. automodule:: translate.client.exceptions
   :members:
