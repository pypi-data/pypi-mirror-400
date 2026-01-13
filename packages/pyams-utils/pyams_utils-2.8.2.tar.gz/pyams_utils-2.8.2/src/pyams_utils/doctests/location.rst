===========================
PyAMS_utils location module
===========================

Objects implementing ILocation interface need a custom hook on copy, to avoid copying their
"__parent__" attribute value!

This test is copied from "zope.location" package, from which this hook is copied:

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)

    >>> from pyams_utils.tests import MyFolder, MyTestContent

    >>> parent = MyFolder()
    >>> child = MyTestContent()
    >>> parent['child'] = child

    >>> child.__parent__ is parent
    True

    >>> from zope.copy import copy
    >>> child2 = copy(child)

    >>> child2.__parent__ is parent
    False


Tests cleanup:

    >>> tearDown()
