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

"""PyAMS_utils.data module

The *IObjectData* interface is a generic interface which can be used to assign custom data to any
object. This object data may be any object which can be serialized to JSON, and assigned to any
HTML *data* attribute. It can typically be used to set a *data-ams-data* attribute to objects,
which is afterwards converted to classic *data-* attributes by **MyAMS.js** framework.

For example, for a custom widget in a form:

.. code-block:: python

    def updateWidgets(self):
        super(MyForm, self).updateWidgets()
        widget = self.widgets['mywidget']
        alsoProvides(widget, IObjectData)
        widget.object_data = {'ams-colorpicker-position': 'top left'}

You can then set an attribute in a TAL template like this:

.. code-block:: xml

    <div tal:attributes="data-ams-data extension:object_data(widget)">...</div>

After data initialization by **MyAMS.js**, the following code will be converted to:

.. code-block:: html

    <div data-ams-colorpicker-position="top left">...</div>
"""

import json

from zope.interface import Interface, implementer
from zope.schema.fieldproperty import FieldProperty

from pyams_utils.adapter import ContextAdapter, ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.data import IObjectData, IObjectDataRenderer
from pyams_utils.interfaces.tales import ITALESExtension


__docformat__ = 'restructuredtext'


def format_data(mapping):
    """Format given mapping as HTML "data" attributes

    "-data" prefix is not required for given mapping keys
    """
    return ' '.join((f'data-{k}="{v}"' for k, v in mapping.items()))


@implementer(IObjectData)
class ObjectDataManagerMixin:
    """Object data manager mixin class"""

    object_data = FieldProperty(IObjectData['object_data'])


@adapter_config(required=IObjectData, provides=IObjectDataRenderer)
class ObjectDataRenderer(ContextAdapter):
    """Object data JSON renderer"""

    def get_object_data(self):
        """See :py:class:`IObjectDataRenderer
        <pyams_utils.interfaces.data.IObjectDataRenderer>` interface
        """
        data = IObjectData(self.context)
        return json.dumps(data.object_data) if data is not None else None


def render_object_data(context):
    """Render object data as JSON string"""
    renderer = IObjectDataRenderer(context, None)
    if renderer is not None:
        return renderer.get_object_data()
    return None


@adapter_config(name='object_data',
                required=(Interface, Interface, Interface),
                provides=ITALESExtension)
class ObjectDataExtension(ContextRequestViewAdapter):
    """extension:object_data TALES extension

    This TALES extension is to be used in Chameleon templates to define a custom data attribute
    which stores all object data (see :py:class:`IObjectData
    <pyams_utils.interfaces.data.IObjectData>` interface), like this:

    .. code-block:: xml

        <div tal:attributes="data-ams-data extension:object_data(context)">...</div>
    """

    def render(self, context=None):
        """See :py:class:`ITALESExtension `pyams_utils.interfaces.tales.ITALESExtension`
        interface
        """
        if context is None:
            context = self.context
        return render_object_data(context)
