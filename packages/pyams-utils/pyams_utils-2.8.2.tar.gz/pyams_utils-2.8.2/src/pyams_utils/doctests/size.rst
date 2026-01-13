
=======================
PyAMS_utils size module
=======================

Thi smodule is providing a single function to convert size value (given in bytes) in "human"
format:

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from pyramid.threadlocal import manager
    >>> request = DummyRequest(params={'_LOCALE_': 'en'})
    >>> request.locale_name
    'en'

    >>> manager.push({'request': request, 'registry': config.registry})

    >>> from pyams_utils.size import get_human_size

    >>> get_human_size(256)
    '256 bytes'

    >>> get_human_size(256, request)
    '256 bytes'
    >>> get_human_size(3678, request)
    '3.6 Kb'
    >>> get_human_size(6785342, request)
    '6.47 Mb'
    >>> get_human_size(3674815342, request)
    '3.422 Gb'

    >>> request = DummyRequest(params={'_LOCALE_': 'fr'})
    >>> request.locale_name
    'fr'
    >>> get_human_size(256, request)
    '256 bytes'
    >>> get_human_size(3678, request)
    '3,6 Kb'
    >>> get_human_size(6785342, request)
    '6,47 Mb'
    >>> get_human_size(3674815342, request)
    '3,422 Gb'

    >>> request = DummyRequest(params={'_LOCALE_': 'xxx'})
    >>> request.locale_name
    'xxx'
    >>> get_human_size(256, request)
    '256 bytes'


Tests cleanup:

    >>> manager.pop()
    {...}
    >>> tearDown()
