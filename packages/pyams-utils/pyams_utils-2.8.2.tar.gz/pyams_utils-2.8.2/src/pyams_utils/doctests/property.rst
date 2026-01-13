
===========================
PyAMS_utils property module
===========================

This module provides a small set of decorators which can be used to define several kinds of
cached properties.


Cached properties
-----------------

These read-only properties are evaluated only once; the property value is stored into
object's attributes, and so should be freed with the object (so it should behave like a
Pyramid's "reify" decorator, but we have kept it for compatibility of existing code)

    >>> from pyams_utils.property import cached_property

    >>> class ClassWithCache:
    ...     '''Class with cache'''
    ...     @cached_property
    ...     def cached_value(self):
    ...         print("This is a cached value")
    ...         return 1

    >>> obj = ClassWithCache()
    >>> obj.cached_value
    This is a cached value
    1

On following calls, cached property method shouldn't be called again:

    >>> obj.cached_value
    1

Value is stored into instance dictionnary:

    >>> obj.__dict__['cached_value']
    1


Class properties
----------------

This decorator is working like a classic property, but can be assigned to a
class; to support class properties, this class also have to be decorated with the
"classproperty_support" decorator:

Class properties are used to define properties on class level:

    >>> from pyams_utils.property import classproperty, ClassPropertyType

    >>> class ClassWithProperties(metaclass=ClassPropertyType):
    ...     '''Class with class properties'''
    ...
    ...     class_attribute = 1
    ...
    ...     @classproperty
    ...     def my_class_property(cls):
    ...         return cls.class_attribute

    >>> obj = ClassWithProperties()
    >>> obj.my_class_property
    1

    >>> obj.my_class_property = 2
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute

We can define a setter as usual:

    >>> class OtherClassWithProperties(metaclass=ClassPropertyType):
    ...     '''Class with class properties'''
    ...
    ...     __class_attribute = 1
    ...
    ...     @classproperty
    ...     def my_class_property(cls):
    ...         return cls.__class_attribute
    ...
    ...     @my_class_property.setter
    ...     def my_class_property(cls, value):
    ...         cls.__class_attribute = value

    >>> OtherClassWithProperties.my_class_property
    1

    >>> OtherClassWithProperties.my_class_property = 2
    >>> OtherClassWithProperties.my_class_property
    2

Please note that setting a class property from an instance of the class doesn't affect the
class, but only the instance:

    >>> obj = OtherClassWithProperties()
    >>> obj.my_class_property
    2

    >>> obj.my_class_property = 3
    >>> obj.my_class_property
    3

    >>> obj2 = OtherClassWithProperties()
    >>> obj2.my_class_property
    2

    >>> OtherClassWithProperties.my_class_property = 4
    >>> OtherClassWithProperties.my_class_property
    4
    >>> obj.my_class_property
    3
    >>> obj2.my_class_property
    4
