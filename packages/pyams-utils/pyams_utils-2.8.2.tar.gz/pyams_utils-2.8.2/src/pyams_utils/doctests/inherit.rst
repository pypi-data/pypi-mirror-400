
==========================
PyAMS_utils inherit module
==========================

This PyAMS module is used to handle inheritance between a parent object and a child which can
"inherit" from some of it's properties, as long as they share the same "target" interface.

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp(hook_zca=True)

    >>> from zope.interface import implementer, Interface, Attribute
    >>> from zope.schema import TextLine
    >>> from zope.schema.fieldproperty import FieldProperty

    >>> from pyams_utils.adapter import adapter_config
    >>> from pyams_utils.interfaces.inherit import IInheritInfo
    >>> from pyams_utils.inherit import BaseInheritInfo, InheritedFieldProperty

Let's start by creating a "content" interface, and a marker interface for objects for which we
want to provide this interface:

    >>> class IMyInfoInterface(IInheritInfo):
    ...     '''Custom interface'''
    ...     value = TextLine(title="Custom attribute")

    >>> class IMyTargetInterface(Interface):
    ...     '''Target interface'''

    >>> @implementer(IMyInfoInterface)
    ... class MyInfo(BaseInheritInfo):
    ...     target_interface = IMyTargetInterface
    ...     adapted_interface = IMyInfoInterface
    ...
    ...     _value = FieldProperty(IMyInfoInterface['value'])
    ...     value = InheritedFieldProperty(IMyInfoInterface['value'])

Please note that for each field of the interface which can be inherited, you must define to
properties: one using "InheritedFieldProperty" with the name of the field, and one using a classic
"FieldProperty" with the same name prefixed by "_"; this property is used to store the "local"
property value, when inheritance is unset.

The adapter is created to adapt an object providing IMyTargetInterface to IMyInfoInterface;
please note that the adapter *must* attach the created object to it's parent by setting
__parent__ attribute:

    >>> @adapter_config(required=IMyTargetInterface, provides=IMyInfoInterface)
    ... def my_info_factory(context):
    ...     info = getattr(context, '__info__', None)
    ...     if info is None:
    ...         info = context.__info__ = MyInfo()
    ...         info.__parent__ = context
    ...     return info

Adapter registration is here only for testing; the "adapter_config" decorator may do the job in
a normal application context:

    >>> registry = config.registry
    >>> registry.registerAdapter(my_info_factory, (IMyTargetInterface, ), IMyInfoInterface)

We can then create classes which will be adapted to support inheritance:

    >>> @implementer(IMyTargetInterface)
    ... class MyTarget:
    ...     '''Target class'''
    ...     __parent__ = None
    ...     __info__ = None

    >>> parent = MyTarget()
    >>> parent_info = IMyInfoInterface(parent)
    >>> parent.__info__
    <pyams_utils.tests.test_utils...MyInfo object at ...>
    >>> parent_info.value = 'parent'
    >>> parent_info.value
    'parent'
    >>> parent_info.can_inherit
    False

As soon as a parent is defined, the child object can inherit from it's parent:

    >>> child = MyTarget()
    >>> child.__parent__ = parent
    >>> child_info = IMyInfoInterface(child)
    >>> child.__info__
    <pyams_utils.tests.test_utils...MyInfo object at ...>

    >>> child_info.can_inherit
    True
    >>> child_info.inherit
    True
    >>> child_info.value
    'parent'

Setting child value while inheritance is enabled donesn't have any effect:

    >>> child_info.value = 'child'
    >>> child_info.value
    'parent'
    >>> child_info.inherit_from == parent
    True

You can disable inheritance and define your own value:

    >>> child_info.inherit = False
    >>> child_info.value = 'child'
    >>> child_info.value
    'child'
    >>> child_info.inherit_from == child
    True

Using the reverse inherit option is also possible:

    >>> child_info.no_inherit = False
    >>> child_info.inherit
    True
    >>> child_info.no_inherit
    False
    >>> child_info.inherit_from == parent
    True

Please note that parent and child in this example share the same class, but this is not a
requirement; they just have to implement the same marker interface, to be adapted to the same
content interface.


Tests cleanup:

    >>> tearDown()
