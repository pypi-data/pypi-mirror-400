===================
PyAMS_utils package
===================

.. contents::


What is PyAMS?
==============

PyAMS (Pyramid Application Management Suite) is a small suite of packages written for applications
and content management with the Pyramid framework.

**PyAMS** is actually mainly used to manage web sites through content management applications (CMS,
see PyAMS_content package), but many features are generic and can be used inside any kind of web
application.

All PyAMS documentation is available on `ReadTheDocs <https://pyams.readthedocs.io>`_; source code
is available on `Gitlab <https://gitlab.com/pyams>`_ and pushed to `Github
<https://github.com/py-ams>`_.


What is PyAMS_utils?
====================

PyAMS_utils is a large set of small generic modules used to handle PyAMS applications.

These modules provide several decorators used to declare object factories, adapters, utilities
and vocabularies; they also provide a large set of adapters, utilities and predicates related to
many common operations like caching, dates management, data API, text conversions, request
properties..., as well as custom schema fields.

When included into Pyramid's configuration, this package also register several Zope packages
through ZCML, typically to automatically inclure DublinCore extensions or IntIDs management.

Most PyAMS_utils modules are documented using doctests in the /doctests/ sub-directory.
