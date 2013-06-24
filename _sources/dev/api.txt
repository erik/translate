API Documentation
=================

translate provides a very straightforward API using rather simple URLs. All API
calls are HTTP GETs, returning JSON data.

URL scheme :code:`/api/v<version>/<method>?<params...>`

For each URL, the parameter :code:`?callback=jsonp` can be used to wrap the
returned JSON data using the name `jsonp`. For example::

  GET /api/v1/translators?callback=foo

  foo({...})


API Version 1
-------------

Base URL :code:`/api/v1/<method>?<params...>`

Methods
~~~~~~~

- **translators**

  :Description:
     Returns information on all the available translation backends that this
     server can support.
  :Parameters:
     None
  :Returns:
     ::

        {
          "backends": [
          {
            "pairs": [
              [
                "from-lang",
                "to-lang"
              ], ...
            ],
            "name": "Backend Name",
            "preference": 999,
            "description": "Description of this backend"
          }, ...
          ]
        }

- **pairs**

  :Description:
     Returns a list of every pair of (source language, destination language)
     that this server can handle.
  :Parameters:
     None
  :Returns:
     ::

      {
        "pairs": [
          [
            "from-language",
            "to-language"
          ],
        ]
      }

- **translate**

  :Description:
     Translate a block of text between two languages.
  :Parameters:
     :from:
        Language text to be translated is in
     :to:
        Language to translate text to
     :text:
        Text to translate from the `from` language to the `to` language.
  :Returns:
     ::

      {
        "from": "from-language",
        "to": "to-language",
        "result": "Text translated into 'to' language"
      }

Rate Limiting
~~~~~~~~~~~~~

translate provides optional per-method rate limiting for the API, that will be
reported through HTTP headers.

If active, the following HTTP headers will be included in every API call:

:X-RateLimit-Remaining:
   The number of requests remaining before rate limiting kicks in.

:X-RateLimit-Limit:
   The number of requests to allow with a within the specified time limit.

:X-RateLimit-Duration:
   The length in time (in seconds) that each request will be counted against the
   API limit.


Errors
~~~~~~

Errors can occur when parameters are omitted or the rate limit (if activated) is
exceeded. The HTTP status code for errors is 400. The general scheme for errors
is rather simple::

  {
    "method": "API method (or 'ratelimit') that caused the error"
    "message": "(hopefully) human-readable description of error"
  }
