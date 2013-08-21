User Guide
==========

.. toctree::
   :maxdepth: 2

This is the guide you should follow if you plan to set up your own instance of
the translate server.

The process is relatively straightforward, and doesn't have too many
dependencies, so it should be pretty simple to set up in many environments.

If you have an issue setting this up, or something isn't clear, please open an
issue on the tracker_ so I can try to address it.

.. _tracker: https://github.com/boredomist/translate/issues/new

Installation
------------

Dependencies
############

Currently, the server and client are tested against Python 2.6 and 2.7. Python
3 support is feasible, as the dependencies all support it, but has not been
tested or implemented yet. If this is important to you, let me know and I'll
try to get it working.

I would recommend that you set this up in a virtualenv, so that global
dependency management isn't a nightmare. There isn't any difference in the rest
of the setup if you don't use a virtualenv however. In our case, it would be::

  $ virtualenv -p python2.7 env
  $ source env/bin/activate

Next, use pip to install the dependencies::

  $ pip install -r requirements.txt

You should customize :code:`settings.py` at this point so that it makes sense
for your setup. The file itself documents all the options that are available
for configuration, so it shouldn't be too difficult to modify.

.. literalinclude:: ../../../settings.py
   :language: python

And finally, use :code:`setup.py` to install the code::

  $ python setup.py install

You should now have :code:`translate` and :code:`translate-client` on your
path.


Running the Server
------------------

There are many ways you could run the server. It uses the WSGI protocol, which
is supported by a ton of application servers and configurations. I'll just
highlight two easy ways to do it here, and hopefully the concept will carry
over.

Standalone
##########

Since the translate server uses Flask to handle all of the HTTP stuff, the
server can be run very simply on the command line using Flask's bundled
Werkzeug server. To do this, use the :code:`translate` executable that should
have been installed during the setup. ::

  $ translate [--debug]

That's it! If you include the :code:`--debug` flag, you'll see some detailed
information printed to the console.

**Note:** wsgiref (the server that Werkzeug uses) has `some issues
<http://stackoverflow.com/a/481952>`_, and probably shouldn't be used for
production use. There is also a tendency for it to be somewhat slower than
other WSGI servers.

If you'd like, you can set up a reverse proxy to the translate server using
nginx, Apache, ..., but I won't document that process here. Checkout out some
of these links for information:

* http://wiki.nginx.org/HttpProxyModule
* http://stackoverflow.com/questions/4859956/lighttpd-as-reverse-proxy
* https://httpd.apache.org/docs/2.2/mod/mod_proxy.html

uWSGI
#####

A slightly more complicated setup runs the translate server using uWSGI, which
is an application server for WSGI.

More documentation on uWSGI is `here
<http://uwsgi-docs.readthedocs.org/en/latest/>`_

Translate comes with a sample uWSGI configuration file in
:code:`translate.uwsgi`, which you can edit to fit your needs:

.. literalinclude:: ../../../translate.uwsgi
   :language: ini

Setting up uWSGI to use a port rather than a socket for communication is
slightly easier, and may fit your use better.

Once you've customized this to your satisfaction, you can run uWSGI like so::

  $ uwsgi --ini /path/to/translate.uwsgi

*Note: if you're using setuid (like the example does), you will very likely
have to run as root.*

Reverse Proxy with nginx
~~~~~~~~~~~~~~~~~~~~~~~~

I'm only detailing nginx here, but the same principle should apply to almost
all webservers. See the links I included above for details.

Assuming you go with the same setup as the base configuration (using
:code:`socket = /path/to/socket.sock`), nginx configuration is as simple as
including this in your :code:`/etc/nginx/nginx.conf`::

  server {
    server_name translate.example.com;

    location / { try_files $uri @translate; }
    location @translate {
      include uwsgi_params;
      uwsgi_pass unix:///path/to/socket.sock;
    }
  }

*Note: Make sure you have socket permissions correct! nginx will refuse to
start if the user/group aren't correct (which is the point of the
:code:`ch{own,grp,mod}-socket` configuration options).*
