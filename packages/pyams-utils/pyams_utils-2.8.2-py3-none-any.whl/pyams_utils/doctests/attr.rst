
=======================
PyAMS_utils attr module
=======================

This small PyAMS module is used to define a custom URL traverser, which can be used to get
access to a specific object attribute:

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)

    >>> from zope.interface import implementer, Interface
    >>> @implementer(Interface)
    ... class MyContent:
    ...     value = 1

    >>> content = MyContent()

    >>> from zope.traversing.interfaces import ITraversable
    >>> traverser = config.registry.getAdapter(content, ITraversable, name='attr')
    >>> traverser
    <...AttributeTraverser object at 0x...>

    >>> traverser.traverse('bob')
    Traceback (most recent call last):
    ...
    pyramid.httpexceptions.HTTPNotFound: The resource could not be found.

    >>> traverser.traverse('value')
    1
    >>> traverser.traverse('value.inner')
    1


Tests cleanup:

    >>> tearDown()
