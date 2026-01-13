
===========================
PyAMS_utils timezone module
===========================

Datetimes are often quite hard to store and handle correctly when timezones are used.
A good approach is to store all datetimes in UTC, and to just display them using a correct
user's timezone.

PyAMS is proposing a server timezone utility, which allows to assign a static timezone to the
web application server; this "local" timezone is then used to render all datetimes. An alternate
solution would be to let users choose their own timezone, so that datimes are displayed in their
own timezone instead of server's one.

Other extensions could provide a user's profile setting allowing any registered user to assign
a specific timezone to his own profile and display datetimes using this timezone; this should
require a custom adapter between :py:class:`IRequest <pyramid.interfaces.IRequest>` and
:py:class:`ITZInfo <zope.interface.common.idatetime.ITZInfo>` to handle this specification.
Other systems can also get timezone from source IP address (see, for example,
`https://ip-api.com/').

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)

    >>> request = DummyRequest()
    >>> from zope.interface.common.idatetime import ITZInfo
    >>> ITZInfo(request)
    <UTC>

    >>> from datetime import datetime, timezone
    >>> from pyams_utils.timezone import tztime, gmtime, localgmtime

"tztime" is used to check timezone of provided datetime; if no timezone is associated, the
provided datetime is localized in UTC:

    >>> now = datetime.utcnow()
    >>> now.tzinfo is None
    True
    >>> now = datetime.now(timezone.utc)
    >>> now.tzinfo
    datetime.timezone.utc
    >>> tztime(now)
    datetime.datetime(..., tzinfo=<UTC>)
    >>> tztime(None) is None
    True
    >>> tztime('string')
    'string'

    >>> from pyams_utils.interfaces.timezone import IServerTimezone
    >>> from pyams_utils.timezone.utility import ServerTimezoneUtility
    >>> tz = ServerTimezoneUtility()
    >>> tz.timezone = 'Europe/Paris'
    >>> tz.timezone
    'Europe/Paris'

    >>> config.registry.registerUtility(tz, IServerTimezone, name='')
    >>> from pyams_utils.registry import query_utility
    >>> stz = query_utility(IServerTimezone)
    >>> stz
    <...ServerTimezoneUtility object at 0x...>
    >>> stz.timezone
    'Europe/Paris'
    >>> stz is tz
    True

    >>> ITZInfo(request)
    <DstTzInfo 'Europe/Paris' ... STD>

"gmtime" is used to convert provided datetime to UTC:

    >>> tznow = tztime(now)
    >>> tznow
    datetime.datetime(..., tzinfo=<DstTzInfo 'Europe/Paris' ...>)
    >>> gmtime(tznow)
    datetime.datetime(..., tzinfo=<UTC>)
    >>> gmtime(None) is None
    True
    >>> gmtime('string')
    'string'

"localgmtime" function is used to convert a value to UTC; but input value is assumed to be
in server's timezone:

    >>> localgmtime(now)
    datetime.datetime(..., tzinfo=<UTC>)
    >>> localgmtime(tznow)
    datetime.datetime(..., tzinfo=<UTC>)
    >>> localgmtime(None) is None
    True
    >>> localgmtime('string')
    'string'


Tests cleanup:

    >>> tearDown()
