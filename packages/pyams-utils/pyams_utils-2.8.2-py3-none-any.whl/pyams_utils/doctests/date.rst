
=======================
PyAMS utils date module
=======================

Dates functions are used to convert dates from/to string representation:

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)

    >>> import pytz
    >>> from datetime import datetime, timezone
    >>> from pyams_utils import date
    >>> utc = pytz.timezone('UTC')
    >>> now = datetime.fromtimestamp(1205000000, utc)
    >>> now
    datetime.datetime(2008, 3, 8, 18, 13, 20, tzinfo=<UTC>)

You can get an unicode representation of a date in ASCII format using 'unidate' fonction ; date is
converted to UTC:

    >>> udate = date.unidate(now)
    >>> udate
    '2008-03-08T18:13:20+00:00'

'parse_date' can be used to convert ASCII format into datetime:

    >>> ddate = date.parse_date(udate)
    >>> ddate
    datetime.datetime(2008, 3, 8, 18, 13, 20, tzinfo=<UTC>)

'date_to_datetime' can be used to convert a 'date' type to a 'datetime' value ; if a 'datetime' value
is used as argument, it is returned 'as is':

    >>> ddate.date()
    datetime.date(2008, 3, 8)
    >>> date.date_to_datetime(ddate)
    datetime.datetime(2008, 3, 8, 18, 13, 20, tzinfo=<UTC>)
    >>> date.date_to_datetime(ddate.date())
    datetime.datetime(2008, 3, 8, 0, 0)


Timestamp TALES extension
-------------------------

The *timestamp* TALES extension can be used to include an object timestamp into a Chameleon
template:

    >>> from pyramid_chameleon.zpt import renderer_factory
    >>> config.add_renderer('.pt', renderer_factory)

    >>> import os, tempfile
    >>> temp_dir = tempfile.mkdtemp()

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zope.dublincore.interfaces import IZopeDublinCore
    >>> from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
    >>> config.registry.registerAdapter(ZDCAnnotatableAdapter, (IAttributeAnnotatable, ),
    ...                                 IZopeDublinCore)

    >>> template = os.path.join(temp_dir, 'timestamp.pt')
    >>> with open(template, 'w') as file:
    ...     _ = file.write("<div>${structure:tales:timestamp(context)}</div>")

    >>> from zope.interface import implementer, Interface
    >>> class IMyContent(Interface):
    ...     """Custom marker interface"""

    >>> @implementer(IMyContent, IAttributeAnnotatable)
    ... class MyContent:
    ...     """Custom class"""
    >>> my_content = MyContent()

    >>> zdc = IZopeDublinCore(my_content)
    >>> zdc.modified = zdc.created = datetime.now(timezone.utc)

    >>> from pyramid.renderers import render
    >>> output = render(template, {'context': my_content, 'request': DummyRequest()})
    >>> output == '<div>{}</div>'.format(zdc.modified.timestamp())
    True

    >>> template = os.path.join(temp_dir, 'timestamp-iso.pt')
    >>> with open(template, 'w') as file:
    ...     _ = file.write("<div>${structure:tales:timestamp(context, 'iso')}</div>")

    >>> output = render(template, {'context': my_content, 'request': DummyRequest()})
    >>> output == '<div>{}</div>'.format(zdc.modified.isoformat())
    True

Using this TALES extension on an object which doesn't support dublincore interface just returns
current timestamp:

    >>> content = object()
    >>> render(template, {'request': DummyRequest(context=content)})
    '<div>...-...-...T...:...:...+00:00</div>'


Timezones handling
------------------

Timezones handling gave me headaches at first. I finally concluded that the best way (for me !) to handle
TZ data was to store every datetime value in UTC.
As far as I know, there is no easy way to know the user's timezone from his request settings. So you can:
- store this timezone in user's profile,
- define a static server's timezone
- create and register a ServerTimezoneUtility to handle server default timezone.

My current default user's timezone is set to 'Europe/Paris'; you should probably update this setting in
'timezone.py' if you are located elsewhere.

    >>> from pyams_utils import timezone
    >>> timezone.tztime(ddate)
    datetime.datetime(2008, 3, 8, 18, 13, 20, tzinfo=<UTC>)

'gmtime' function can be used to convert a datetime to UTC:

    >>> timezone.gmtime(now)
    datetime.datetime(2008, 3, 8, 18, 13, 20, tzinfo=<UTC>)


TALES extensions
----------------

Several TALES extensions are provided to handle date, time and datetime rendering.

    >>> from pyams_utils.date import ISOFormatTalesAdapter

    >>> request = DummyRequest(context=my_content)
    >>> renderer = ISOFormatTalesAdapter(None, request, None)
    >>> renderer.render(now)
    '2008-03-08T18:13:20+00:00'

    >>> from pyams_utils.date import DateTalesAdapter
    >>> renderer = DateTalesAdapter(None, request, None)
    >>> renderer.render()
    '--'
    >>> renderer.render(now)
    'on 08/03/2008'
    >>> renderer.render(now, put_prefix=False)
    '08/03/2008'

    >>> from pyams_utils.date import TimeTalesAdapter
    >>> renderer = TimeTalesAdapter(None, request, None)
    >>> renderer.render()
    '--'
    >>> renderer.render(now)
    'at 18:13'
    >>> renderer.render(now, put_prefix=False)
    '18:13'

    >>> from pyams_utils.date import DatetimeTalesAdapter
    >>> renderer = DatetimeTalesAdapter(None, request, None)
    >>> renderer.render()
    '--'
    >>> renderer.render(now)
    'on 08/03/2008 at 18:13'
    >>> renderer.render(now, put_prefix=False)
    '08/03/2008 - 18:13'


Text renderers
--------------

It's sometimes required to include dynamic contents into an otherwise "static" string. For example,
how could we provide the current execution date in a JSON string which must be provided to a
REST web service?

You can use *text renderers* for this purpose; these renderers have to be registered as named
multi-adapters providing *ITextRenderer* interface to string and request. These renderers are
then called using a simple *${{renderer}}* syntax, where *renderer* is the name of the registered
adapter; if this renderer require arguments, the syntax is *${{renderer:args1,arg2}}* and
arguments will be provided as strings to the adapter's *render* method. If the provided renderer
can't be found, the result is an empty string:

    >>> from pyams_utils.text import render_text

    >>> render_text(None) is None
    True
    >>> render_text('')
    ''
    >>> render_text("String without renderer")
    'String without renderer'

    >>> render_text("String with a ${{missing}} renderer")
    'String with a  renderer'

Let's try to create a sample renderer, which will render itself as a static value:

    >>> from pyams_utils.adapter import ContextRequestAdapter

    >>> class StaticTextRenderer(ContextRequestAdapter):
    ...     def render(self, *args):
    ...         return 'STATIC'

    >>> from pyramid.interfaces import IRequest
    >>> from pyams_utils.interfaces.text import ITextRenderer

    >>> config.registry.registerAdapter(StaticTextRenderer, (str, IRequest),
    ...                                 ITextRenderer, name='static')

    >>> render_text("String with a ${{static}} renderer")
    'String with a STATIC renderer'

Another renderer will use provided arguments:

    >>> class DynamicTextRenderer(ContextRequestAdapter):
    ...     def render(self, *args):
    ...         return ' '.join(args)

    >>> config.registry.registerAdapter(DynamicTextRenderer, (str, IRequest),
    ...                                 ITextRenderer, name='dynamic')

    >>> render_text("String with a ${{dynamic}} renderer")
    'String with a  renderer'

    >>> render_text("String with a ${{dynamic:value}} renderer")
    'String with a value renderer'

    >>> render_text("String with a ${{dynamic:multiple,values}} renderer")
    'String with a multiple values renderer'

We can, of course, include several renderers in the same input string:

    >>> render_text("String with a ${{static}} and ${{dynamic:multiple,values,dynamic}} renderers")
    'String with a STATIC and multiple values dynamic renderers'

A simple text renderer is provided by PyAMS; it allows to include current server datetime
into generated text in standard localized format:

    >>> render_text("Current date: ${{now}}")
    'Current date: ...'

This renderer can also receive arguments to define formatting string:

    >>> render_text("Current date: ${{now:%Y-%m-%d}}")
    'Current date: ...-...-...'


Tests cleanup:

    >>> tearDown()
