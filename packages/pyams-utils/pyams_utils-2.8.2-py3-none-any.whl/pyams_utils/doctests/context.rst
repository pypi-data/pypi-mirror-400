
==========================
PyAMS_utils context module
==========================

PyAMS_utils "context" module provides a "context_selector" predicate as well as a few custom
context managers:

    >>> from pyramid.testing import setUp, tearDown
    >>> config = setUp(hook_zca=True)

    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)


Capturing context managers
--------------------------

PyAMS provides context managers which can be used to capture standard output and standard
error output:

    >>> import sys
    >>> from pyams_utils.context import capture, capture_stderr, capture_all

    >>> def print_stdout():
    ...     print("This is a standard output")

    >>> def print_stderr():
    ...     print("This is a standard error", file=sys.stderr)

    >>> def print_all():
    ...     print_stdout()
    ...     print_stderr()

    >>> with capture(print_stdout) as (result, output):
    ...     printed = output
    >>> printed
    'This is a standard output\n'

    >>> with capture_stderr(print_stderr) as (result, errors):
    ...     printed = errors
    >>> printed
    'This is a standard error\n'

    >>> with capture_all(print_all) as (result, output, errors):
    ...     printed = (output, errors)
    >>> printed
    ('This is a standard output\n', 'This is a standard error\n')


Context selection predicate
---------------------------

This predicate can be used to filter events based on their context object:

    >>> from zope.interface import implementer, Interface
    >>> class IMyInterface(Interface):
    ...     """Custom marker interface"""

    >>> @implementer(IMyInterface)
    ... class MyContent:
    ...     """Content class"""

    >>> content = MyContent()

    >>> from pyams_utils.context import ContextSelector
    >>> selector = ContextSelector(IMyInterface, config)
    >>> selector.text()
    'context_selector = (<InterfaceClass ...IMyInterface>,)'

    >>> from zope.lifecycleevent import ObjectModifiedEvent
    >>> event = ObjectModifiedEvent(content)
    >>> selector(event)
    True

You can also use classes to filter contexts:

    >>> selector = ContextSelector(MyContent, config)
    >>> selector(event)
    True

Of course not matching objects should return a false value:

    >>> event = ObjectModifiedEvent(object())
    >>> selector(event)
    False

You can also filter events based on form events context:

    >>> class Form:
    ...     def __init__(self, context):
    ...         self.context = context

    >>> class DataExtractedEvent:
    ...     def __init__(self, context):
    ...         self.form = Form(context)

    >>> event = DataExtractedEvent(content)
    >>> selector(event)
    True

    >>> event = DataExtractedEvent(object())
    >>> selector(event)
    False


Tests cleanup:

    >>> tearDown()
