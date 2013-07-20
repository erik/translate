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

- **batch**

  **Note**: *batch* is an HTTP POST method.

  :Description:
     Perform multiple API requests at once and return the results as a single
     JSON object. Do note that this still takes rate limiting into account.
  :Parameters:
     :urls:
        Array of URL strings to request at once. Should be formatted as a JSON
        array, e.g.::

          POST /api/v1/batch
          urls=["/api/v1/foo", "/api/v1/bar", ...]
  :Returns:
     Unless there is an error with the batch call itself, this method will
     always return HTTP status 200 with a body in the form of a JSON array of
     dicts containing the response data for the specified API calls. Order is
     maintained, of course.
     ::

        [
          {
            "status": status code for this request,
            "url": api url requested,
            "headers": {
              Any HTTP headers returned by the request e.g.:
              "X-RateLimit-Remaining": "20",
              ...
            },
            "data": JSON object returned by API call (should be a dict)
          },
          ...
        ]

- **ratelimit**

  :Description:
     Returns current ratelimit status, the number of requests remaining for
     each API endpoint.
  :Parameters:
     None
  :Returns:
     ::
        {
          "limit": API rate limit,
          "per":   Rate limit window,
          "reset": Unix timestamp (seconds) when old requests will stop
                   counting against ratelimit,
          "methods": {
            "/api/v1/METHOD": number of requests remaining for METHOD,
            ...
          }
        }

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
     :exclude:
        Optional parameter to specify translation backends that should never be
        used for this request, ignoring if they can translate the text or
        not. Can be included multiple times to ignore multiple
        translators. Do note that the names must be exactly as specified by the
        server::
          GET /api/v1/translate?exclude=foo&exclude=bar&...
  :Returns:
     ::

      {
        "from": "from-language",
        "to": "to-language",
        "result": "Text translated into 'to' language",
        "translator": "Name of translator that created this translation"
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

:X-RateLimit-Reset:
   Timestamp (seconds since epoch) of when the current rate limiting window
   will expire.

Errors
~~~~~~

Errors can occur when parameters are omitted or incorrect, the rate limit (if
activated) is exceeded, or a failure with the backend translators occurs.

The general scheme for errors is pretty simple::

    {
      "status": "HTTP Status message",
      "url": "example.com/api/v1/api-method-that-failed",
      "message": "Message explaining what went wrong",
      "code": HTTP Status (int),
      "details": {
        optional additional data
      }
    }


Custom HTTP Status Codes
########################

:429 Too many requests:
   Returned when the API ratelimit is exceeded. ::

      "details": {
        "limit": request limit (int),
        "per": length in seconds that requests count against limit,
        "reset": time stamp when rate limit will reset for each client
      }

:452 Translation error:
   Returned when bad parameters are passed to the :code:`translate` API
   method. The :code:`message` key will give you a human readable form of what
   you're missing.

:453 Translator error:
   Returned when all of the possible translation services fail to translate the
   given text. This is likely indicative of a much larger issue, or a terrible
   case of bad luck. ::

      "details": {
        "from": "from lang",
        "to": "to lang",
        "text": "text to translate",
        "tried": [ names of backends that attempted to translate this text ]
      }

:454 Bad language pair:
   Returned when a request to translate using a nonexistent language pair is
   made. ::

      "details": {
        "from": "from lang",
        "to": "to lang",
        "text": "text to translate",
      }
