
=========================
PyAMS_utils schema module
=========================

PyAMS_utils "schema" module provides several custom schema fields.


Persistent lists and mappings
-----------------------------

    >>> from zope.interface import Interface
    >>> from pyams_utils.schema import PersistentListField, PersistentMappingField

    >>> class IMyInterface(Interface):
    ...     my_list = PersistentListField(title='List field')
    ...     my_dict = PersistentMappingField(title='Dict field')

    >>> from zope.schema.fieldproperty import FieldProperty
    >>> class MyContent:
    ...     my_list = FieldProperty(IMyInterface['my_list'])
    ...     my_dict = FieldProperty(IMyInterface['my_dict'])

    >>> content = MyContent()
    >>> content.my_list = []
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: ([], <class 'persistent.list.PersistentList'>, 'my_list')

    >>> content.my_dict = {}
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: ({}, <class 'persistent.mapping.PersistentMapping'>, 'my_dict')

    >>> from persistent.list import PersistentList
    >>> from persistent.mapping import PersistentMapping

    >>> content.my_list = PersistentList([1, 2, 3])
    >>> content.my_dict = PersistentMapping({'a': 1, 'b': 2})

    >>> type(content.my_list)
    <class 'persistent.list.PersistentList'>

    >>> type(content.my_dict)
    <class 'persistent.mapping.PersistentMapping'>


Encoded password fields
-----------------------

These fields can be used to store encoded passwords:

    >>> from zope.schema import Password
    >>> from pyams_utils.schema import EncodedPasswordField

    >>> Password().fromUnicode('encoded password with éàç'.encode('utf-8'))
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: (b'encoded password with \xc3\xa9\xc3\xa0\xc3\xa7', <class 'str'>, '')

    >>> EncodedPasswordField().fromUnicode('encoded password with éàç')
    'encoded password with éàç'
    >>> EncodedPasswordField().validate('encoded password with éàç'.encode('utf-8'))


HTML text fields
----------------

HTML text fields are just using a marker interface over normal text fields, to be able to
use custom form widgets.


JSON dict fields
----------------

This schema field type is provided to be able to display JSON attributes in a easy way:

    >>> from pyams_utils.schema import JSONDictField
    >>> field = JSONDictField(title='JSON dict')

Please note that this schema field only allows strings as keys and values:

    >>> field.validate({'key': 'value'})
    >>> field.validate({'key': 1})
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongContainedType: ([WrongType(1, <class 'str'>, '')], '')


Color fields
------------

This schema field is used to store color values as hexadecimal strings, without the leading #:

    >>> from pyams_utils.schema import ColorField
    >>> field = ColorField()
    >>> field.validate('short')
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.ValidationError: Color length must be 3 or 6 characters

    >>> field.validate('string')
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.ValidationError: Color value must contain only valid hexadecimal color codes (numbers or letters between 'A' end 'F')

    >>> field.validate('12a')
    >>> field.validate('00ff00')


Dotted decimal fields
---------------------

This schema field can be used as a normal decimal schema field, but using only dots as decimal
separator instead of locale one. It's up to a dedicated PyAMS_form data manager adapter to
handle this...


Dates and datetimes range fields
--------------------------------

Dates range fields are used to store a tuple made of two dates or datetimes:

    >>> from datetime import date, datetime
    >>> from pyams_utils.schema import DatesRangeField, DatetimesRangeField
    >>> field = DatesRangeField()
    >>> field.validate((1, ))
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.TooShort: ((1,), 2)

    >>> field.validate((1, 2))
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongContainedType: ([WrongType(1, <class 'datetime.date'>, ''), WrongType(2, <class 'datetime.date'>, '')], '')

    >>> field.validate((date.today(), date.today()))
    >>> field.validate((date.today(), None))
    >>> field.validate((None, date.today()))
    >>> field.validate((None, None))

    >>> field = DatetimesRangeField()
    >>> field.validate((1, ))
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.TooShort: ((1,), 2)

    >>> field.validate((1, 2))
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongContainedType: ([WrongType(1, <class 'datetime.datetime'>, ''), WrongType(2, <class 'datetime.datetime'>, '')], '')

    >>> field.validate((datetime.now(), datetime.now()))
    >>> field.validate((None, datetime.now()))
    >>> field.validate((datetime.now(), None))
    >>> field.validate((None, None))


Textline list fields
--------------------

Testline list fields are used to store a list of unique non-empty text lines:

    >>> from pyams_utils.schema import TextLineListField
    >>> field = TextLineListField()

    >>> field.validate('value')
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongType: ('value', <class 'list'>, '')

    >>> field.validate([1, 2, 3])
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongContainedType: ([WrongType(1, <class 'str'>, ''), WrongType(2, <class 'str'>, ''), WrongType(3, <class 'str'>, '')], '')

    >>> field.validate(['1', '2', '3'])
    >>> field.validate(['1', None, '3'])
    Traceback (most recent call last):
    ...
    zope.schema._bootstrapinterfaces.WrongContainedType: ([RequiredMissing('')], '')

    >>> field.validate(['1', '2', '1'])
    Traceback (most recent call last):
    ...
    zope.schema.interfaces.NotUnique: 1


Mail address fields
-------------------

The mail address field is used to store... mail address!

    >>> from pyams_utils.schema import MailAddressField, InvalidEmail
    >>> field = MailAddressField()

    >>> field.validate('value')
    Traceback (most recent call last):
    ...
    pyams_utils.schema.InvalidEmail: value

    >>> try:
    ...     field.validate('John Doe <john.doe@example.com>')
    ... except InvalidEmail as e:
    ...     print(e.__doc__)
    Email address must be entered as « name@domain.name », without '<' and '>' characters

    >>> field.validate('john.doe@example.com')


Timezones choice fields
-----------------------

This schema field can be used to handle timezone selection:

    >>> from pyams_utils.schema import TimezoneField
    >>> field = TimezoneField()
    >>> field.default
    'UTC'

Timezone vocabulary is forced:

    >>> field = TimezoneField(vocabulary='My vocabulary')
    >>> field.vocabularyName
    'pyams_utils.timezones'

    >>> field = TimezoneField(values=[])
    >>> field.vocabularyName
    'pyams_utils.timezones'

    >>> field = TimezoneField(source='My source')
    >>> field.vocabularyName
    'pyams_utils.timezones'


Encodings choice fields
-----------------------

This schema field can be used to handle encoding selection:

    >>> from pyams_utils.schema import EncodingField
    >>> field = EncodingField()

Encodings vocabulary is forced:

    >>> field.vocabularyName
    'pyams_utils.encodings'

    >>> field = EncodingField(vocabulary='My vocabulary')
    >>> field.vocabularyName
    'pyams_utils.encodings'

    >>> field = EncodingField(values=[])
    >>> field.vocabularyName
    'pyams_utils.encodings'

    >>> field = EncodingField(source='My source')
    >>> field.vocabularyName
    'pyams_utils.encodings'


HTTP method schema fields
-------------------------

An HTTP method schema field is a tuple combining an HTTP verb (GET, POST...) and an URL.

    >>> from pyams_utils.schema import HTTPMethodField
    >>> field = HTTPMethodField()
    >>> field.value_type
    <zope.schema._bootstrapfields.TextLine object at 0x...>
    >>> field.min_length
    2
    >>> field.max_length
    2
