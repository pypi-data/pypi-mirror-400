
Changelog
=========

2.8.2
-----
 - removed CORS headers checkers (imported from PyAMS_security)

2.8.1
-----
 - updated package dependencies

2.8.0
-----
 - added monitoring interfaces and REST API
 - added Fanstatic "IncludedResource" class to include a CSS or JS resource directly into HTML content
 - added Fanstatic helper to inject resources into an existing HTML content generated outside of a request/response
 - updated create_request/check_request helpers
 - updated doctests to include Swagger package

2.7.7
-----
 - added argument to disable automatic conversion to GMT in date parser

2.7.6
-----
 - packaging issue

2.7.5
-----
 - added "param" text renderer to extract value from provided objects mapping

2.7.4
-----
 - added lists helpers
 - updated Gitlab-CI configuration for Python 3.12

2.7.3
-----
 - added "escape_dict" helper function to escape all mapping values (including inner dicts, lists or sets)
   in a single call

2.7.2
-----
 - added REST decimal schema type converter

2.7.1
-----
 - updated doctest for Python 3.12

2.7.0
-----
 - added "unique_iter_max" function in *list* module to extract unique items
   sharing the same "identity" from an iterator
 - updated doctests
 - added support for Python 3.12

2.6.1
-----
 - allow usage of event form context in "context_selector" subscriber predicate

2.6.0
-----
 - added new factory to handle internal requests

2.5.1
-----
 - small code refactoring

2.5.0
-----
 - switch default timezone from GMT to UTC
 - replaced calls to datetime.utcnow() with datetime.now(timezone.utc)

2.4.4
-----
 - temporary drop of Python 3.12 support...

2.4.3
-----
 - updated Python 3.12 support

2.4.2
-----
 - updated Python 3.12 support

2.4.1
-----
 - updated Python 3.12 support

2.4.0
-----
 - added "grouped_iter" function to get iterator items by groups
 - added support for SonarCloud
 - added support for Python 3.12

2.3.2
-----
 - updated HTTP proxy information class

2.3.1
-----
 - added helper to get next item from any iterable

2.3.0
-----
 - added helper to get interface base name
 - updated parent getter, and added new getter to get parents from context until a given interface
   is found

2.2.0
-----
 - updated base container mixin class
 - moved finding helpers to new module

2.1.0
-----
 - added text function to get sub-parts from input string
 - added helper to load object from ZODB from it's OID

2.0.3
-----
 - added helper to IUniqueID interface getter

2.0.2
-----
 - updated local utilities title getter

2.0.1
-----
 - updated Buildout configuration

2.0.0
-----
 - migrated to Pyramid 2.0

1.17.0
------
 - added TALES extensions for date formatting
 - added ISO countries mapping and vocabulary
 - added support for HTTP proxy schema field
 - added Colander "StringArraySchema" type to handle inputs which can be provided as strings using a
   given separator, or as arrays
 - added support for parameters in absolute and canonical URL adapters
 - updated base CORS requests handler
 - add result to current connection when creating annotation adapter
 - updated local utilities vocabulary terms title factory
 - converted cache key adapters to use hexadecimal values

1.16.2
------
 - added REST API helpers, types converters and base responses
 - moved Swagger/OpenAPI specifications to *PyAMS_zmi* package

1.16.1
------
 - added constant for "missing" string
 - updated date and datetime range schema fields interfaces

1.16.0
------
 - added new "isodate" formatter to *timestamp* TALES extension, to only get date instead of
   datetime in ISO format
 - added "boolean_dict" helper to check that a mapping has at least one key which doesn't
   have an empty value

1.15.1
------
 - added support for Python 3.11
 - added a few types hints

1.15.0
------
 - added new text renderers interfaces and support; the goal of these interfaces is to be able
   to include dynamic fragments into a static string which will be evaluated at runtime; this
   string can be, for example, an SQL query or a JSON object which could be used to provide
   arguments to a REST service, and is actually usable by PyAMS tasks scheduler

1.14.0
------
 - added RPC protocols helper module
 - added object factory helper function

1.13.1
------
 - updated CORS request handler interface to be able to specify supported HTTP methods when
   REST service is not based on Cornice

1.13.0
------
 - added custom interface and default adapter to handle CORS requests

1.12.3
------
 - updated CORS headers support

1.12.2
------
 - updated Gitlab-CI configuration

1.12.1
------
 - added support helpers for CORS preflight OPTIONS verb used by REST services

1.12.0
------
 - removed Pypy3 support from Gitlab-CI because of build issues with Twine and Cryptography
 - added small "is not None" filter helper
 - added text renderers for vocabulary-based properties
 - removed unused Pygments resource

1.11.6
------
 - updated Pypy 3 support

1.11.5
------
 - updated Pypy 3 support

1.11.4
------
 - added support for Python 3.10 and Pypy 3

1.11.3
------
 - check if provided argument is an interface in object factory getter
 - added volatile property setter

1.11.2
------
 - added helper function in *factory* module to get all registered factories
   for a given interface
 - catch RuntimeError in boolean iterator checker to handle Python 3.7+ use case where
   a StopIteration raised from inside a generator is transformed into a RuntimeError
   (see PEP 479)
 - catch NotYet exception in IIntIds object remove subscriber
 - updated class properties management
 - updated local utilities vocabulary
 - updated Gitlab-CI configuration

1.11.1
------
 - updated imports

1.11.0
------
 - added arguments to container module to be able to get depth of found objects inside a
   container

1.10.0
------
 - added 'transaction' module
 - handler sets in dicts merging
 - Pylint improvements

1.9.2
-----
 - updated path getter of external Fanstatic resources

1.9.1
-----
 - locales and translations updates

1.9.0
-----
 - added simple container class to handle internal sequence
 - added mappings marging function
 - updated unique ID adapter
 - updated Pygments resources management

1.8.1
-----
 - updated custom Fanstatic resource manager to handle resources with data correctly in
   production mode

1.8.0
-----
 - updated Venusian decorator callbacks category to "pyramid" for compatibility
   with Pyramid 2.0
 - added registry helper to do adapters lookups

1.7.1
-----
 - added missing interface translation

1.7.0
-----
 - remove support for Python < 3.7
 - added global OpenAPI specification view
 - added simple Cornice schema fields and converters
 - added custom handling of newlines character in "br" TALES extension

1.6.1
-----
 - updated Gitlab-CI configuration

1.6.0
-----
 - added ILocation copy hook (copied from "zope.location" package)
 - added base class for local utilities vocabulary

1.5.2
-----
 - removed Travis-CI configuration

1.5.1
-----
 - translation update

1.5.0
-----
 - updated "get_duration" function to directly accept a timedelta object
 - added dict formatter function (mainly used for tests)
 - use keywords arguments in "request.has_permission" call to use request cache

1.4.3
-----
 - updated doctests for last Pygments release

1.4.2
-----
 - package version mismatch

1.4.1
-----
 - make "object_data" TALES extension return None instead of an empty string when no
   data is available

1.4.0
-----
 - added Beaker's cache management functions and vocabulary
 - always make a registered utility class to provide it's registered interface
 - added HTTPMethodField schema field, a tuple used to combine an HTTP method and an URL in
   a single property

1.3.8
-----
 - updated Gitlab-CI settings to remove Travis-CI

1.3.7
-----
 - updated Travis configuration

1.3.6
-----
 - updated WSGI environment decorator to prevent storing null values into request environment

1.3.5
-----
 - updated request's WSGI property decorator to be able to handle caching functions with
   arguments
 - extracted object data renderer into a dedicated function
 - updated adapter_config decorator arguments names

1.3.4
-----
 - always add "context" attribute to request when creating a new request

1.3.3
-----
 - changed format of "capture*" context managers to also get result of initial function call

1.3.2
-----
 - renamed testing decorator caller argument

1.3.1
-----
 - added testing requirement for Pyramid ZCML

1.3.0
-----
 - updated PyAMS registry management to only use Pyramid registry (using "hook_zca")
 - local registry should only be used to handle local utilities, and not any kind of
   components!
 - updated doctests to use hooked ZCA

1.2.8
-----
 - updated doctests

1.2.7
-----
 - updated doctests

1.2.6
-----
 - updated doctests

1.2.5
-----
 - updated doctests

1.2.4
-----
 - added distribution check

1.2.3
-----
 - small refactoring to add "get_timestamp" function to "pyams_utils.date" module
 - small updates in "url" and "zodb" modules
 - added venusian decorators testing helpers
 - completed doctests

1.2.2
-----
 - Pylint upgrade

1.2.1
-----
 - updated doctest

1.2.0
-----
 - added Fanstatic resource type to define link "data" attributes, with new doctests
 - added new "data" function to format data attributes
 - Pylint code cleanup

1.1.4
-----
 - updated doctests
 - when registering a class adapter, automatically make this class implement the adapter
   "provided" interface
 - added testing helpers

1.1.3
-----
 - added doctests

1.1.2
-----
 - renamed arguments and variables to avoid shadowing arguments names
 - updated private Gitlab integration

1.1.1
-----
 - added synonyms to "adapter_config" arguments names ('required' and 'adapts' for 'context', and
   'provided' for 'provides')

1.1.0
-----
 - corrected "timestamp" TALES extension
 - added generic *IDataManager* interface definition to PyAMS_utils, so it can be used in any
   package without using PyAMS_form

1.0.0
-----
 - initial release
