#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_utils.schema module

This module is used to define custom schema fields
"""

import re
import string

from persistent.list import PersistentList as PersistentListType
from persistent.mapping import PersistentMapping
from zope.interface import Interface, implementer
from zope.schema import Choice, Date, Datetime, Decimal, Dict, List, Password, Text, TextLine, \
    Tuple, ValidationError
from zope.schema.interfaces import IChoice, IDecimal, IDict, IList, IPassword, IText, ITextLine, \
    ITuple

from pyams_utils.interfaces import ENCODINGS_VOCABULARY_NAME, TIMEZONES_VOCABULARY_NAME


__docformat__ = 'restructuredtext'

from pyams_utils import _


#
# Persistent list field
#

class IPersistentListField(IList):
    """Persistent list field marker interface"""


@implementer(IPersistentListField)
class PersistentListField(List):
    """Persistent list field"""

    _type = PersistentListType


#
# Persistent mapping field
#

class IPersistentMappingField(IDict):
    """Persistent mapping field marker interface"""


@implementer(IPersistentMappingField)
class PersistentMappingField(Dict):
    """Persistent mapping field"""

    _type = PersistentMapping


#
# Encoded password field
#

class IEncodedPasswordField(IPassword):
    """Encoded password field interface"""


@implementer(IEncodedPasswordField)
class EncodedPasswordField(Password):
    """Encoded password field"""

    _type = None

    def fromUnicode(self, value):  # pylint: disable=redefined-builtin
        return value

    def constraint(self, value):  # pylint: disable=method-hidden
        return True


#
# HTML field
#

class IHTMLField(IText):
    """HTML field interface"""


@implementer(IHTMLField)
class HTMLField(Text):
    """HTML field"""


#
# JSON dict value field
#

class IJSONDictField(IDict):
    """JSON dict value field interface"""


class IJSONDictFieldsGetter(Interface):
    """Adapter interface used to get JSON value fields list"""

    def get_fields(self, data):
        """Returns an iterator made of tuples

        Each tuple may contain field name, field label and field value
        """


@implementer(IJSONDictField)
class JSONDictField(Dict):
    """JSON dict value field"""

    def __init__(self, key_type=None, value_type=None, **kw):
        super().__init__(key_type=TextLine(),
                         value_type=TextLine(),
                         **kw)


#
# Color field
#

class IColorField(ITextLine):
    """Marker interface for color fields"""


@implementer(IColorField)
class ColorField(TextLine):
    """Color field"""

    def __init__(self, *args, **kw):
        super().__init__(max_length=6, *args, **kw)

    def _validate(self, value):
        if len(value) not in (3, 6):
            raise ValidationError(_("Color length must be 3 or 6 characters"))
        for val in value:
            if val not in string.hexdigits:
                raise ValidationError(_("Color value must contain only valid hexadecimal color "
                                        "codes (numbers or letters between 'A' end 'F')"))
        super()._validate(value)


#
# Pointed decimal field
#

class IDottedDecimalField(IDecimal):
    """Marker interface for dotted decimal fields"""


@implementer(IDottedDecimalField)
class DottedDecimalField(Decimal):
    """Dotted decimal field"""


#
# Dates range field
#

class IBaseRangeField(ITuple):
    """Base range field"""

    from_label = TextLine(title=_("First date label"))

    to_label = TextLine(title=_("To date label"))


class IDatesRangeField(IBaseRangeField):
    """Marker interface for dates range fields"""


@implementer(IDatesRangeField)
class DatesRangeField(Tuple):
    """Dates range field"""

    def __init__(self, value_type=None, unique=False,
                 from_label=None, to_label=None, **kw):
        super().__init__(value_type=Date(required=False),
                         unique=False, min_length=2, max_length=2, **kw)
        self.from_label = from_label or _("from")
        self.to_label = to_label or _("to")


class IDatetimesRangeField(IBaseRangeField):
    """Marker interface for datetimes range fields"""


@implementer(IDatetimesRangeField)
class DatetimesRangeField(Tuple):
    """Datetimes range field"""

    def __init__(self, value_type=None, unique=False,
                 from_label=None, to_label=None, **kw):
        super().__init__(value_type=Datetime(required=False),
                         unique=False, min_length=2, max_length=2, **kw)
        self.from_label = from_label or _("from")
        self.to_label = to_label or _("to")


#
# TextLine list field
#

class ITextLineListField(IList):
    """Marker interface for text line list field"""


@implementer(ITextLineListField)
class TextLineListField(List):
    """TextLine list field"""

    def __init__(self, value_type=None, unique=False, **kw):
        super().__init__(value_type=TextLine(required=True),
                         unique=True, **kw)


#
# Mail address field
#

class IMailAddressField(ITextLine):
    """Marker interface for mail address field"""


EMAIL_REGEX = re.compile(r"^[^ @]+@[^ @]+\.[^ @]+$")


class InvalidEmail(ValidationError):
    """Invalid email validation error"""

    __doc__ = _(
        "Email address must be entered as « name@domain.name », without '<' and '>' characters")


@implementer(IMailAddressField)
class MailAddressField(TextLine):
    """Mail address field"""

    def _validate(self, value):
        super()._validate(value)
        if not EMAIL_REGEX.match(value):
            raise InvalidEmail(value)


#
# Timezone field
#

class ITimezoneField(IChoice):
    """Marker interface for timezone field"""


@implementer(ITimezoneField)
class TimezoneField(Choice):
    """Timezone choice field"""

    def __init__(self, **kw):
        if 'vocabulary' in kw:
            kw.pop('vocabulary')
        if 'values' in kw:
            del kw['values']
        if 'source' in kw:
            kw.pop('source')
        if 'default' not in kw:
            kw['default'] = 'UTC'
        super().__init__(vocabulary=TIMEZONES_VOCABULARY_NAME, **kw)


#
# Encoding field
#

class IEncodingField(IChoice):  # pylint: disable=too-many-ancestors
    """Encoding field interface"""


@implementer(IEncodingField)
class EncodingField(Choice):
    """Encoding schema field"""

    def __init__(self, **kw):
        if 'vocabulary' in kw:
            kw.pop('vocabulary')
        if 'values' in kw:
            del kw['values']
        if 'source' in kw:
            del kw['source']
        super().__init__(vocabulary=ENCODINGS_VOCABULARY_NAME, **kw)


#
# HTTP method field
# This field combines an HTTP method (GET, POST...) and an URL
#

class IHTTPMethodField(ITuple):
    """HTTP method field marker interface"""


@implementer(IHTTPMethodField)
class HTTPMethodField(Tuple):
    """HTTP method getter field

    This schema field is made of two elements which are the HTTP method (GET, POST...) and
    the service URL.
    """

    def __init__(self, **kw):
        super().__init__(value_type=TextLine(),
                         min_length=2,
                         max_length=2,
                         **kw)
