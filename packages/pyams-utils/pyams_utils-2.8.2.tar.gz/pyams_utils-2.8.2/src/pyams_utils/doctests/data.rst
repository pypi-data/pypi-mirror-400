
=======================
PyAMS_utils data module
=======================

The IObjectData interface can be used to assign custom data to any object:

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)

Let's try to format a mapping as data attributes:

    >>> from collections import OrderedDict
    >>> mapping = OrderedDict((('attr1', 'value1'), ('attr2', 2)))

    >>> from pyams_utils.data import format_data
    >>> format_data(mapping)
    'data-attr1="value1" data-attr2="2"'


IObjectData interface
---------------------

    >>> from pyams_utils.interfaces.data import IObjectData, IObjectDataRenderer
    >>> from pyams_utils.data import ObjectDataManagerMixin

    >>> class MyContent(ObjectDataManagerMixin):
    ...     """Content class"""

    >>> content = MyContent()
    >>> content.object_data = mapping

    >>> renderer = config.registry.getAdapter(content, IObjectDataRenderer)
    >>> renderer.get_object_data()
    '{"attr1": "value1", "attr2": 2}'


Object data TALES extension
---------------------------

An "object_data" TALES extension is available to get access to object data:

    >>> from pyams_utils.interfaces.tales import ITALESExtension
    >>> extension = config.registry.getMultiAdapter((content, None, None), ITALESExtension,
    ...                                             name='object_data')
    >>> extension.render()
    '{"attr1": "value1", "attr2": 2}'
    >>> extension.render(content)
    '{"attr1": "value1", "attr2": 2}'

Using this extension on an object which doesn't support IOBjectData interface returns None:

    >>> extension = config.registry.getMultiAdapter((object(), None, None), ITALESExtension,
    ...                                             name='object_data')
    >>> extension.render() is None
    True


Tests cleanup:

    >>> tearDown()
