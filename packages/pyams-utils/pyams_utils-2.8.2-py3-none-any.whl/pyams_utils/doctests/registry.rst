
===========================
PyAMS_utils registry module
===========================

Pyramid provides a components registry, but this one is "hidden" and doesn't always have to be used
by Pyramid application developers.

In it's components model, PyAMS has made the choice to heavilly use the components registry to
register adapters and utilities!

And in addition to the "global" components registry, which is generally feed on application
startup, PyAMS defines a "local" registry, which allows to use components (generally persistent
utilities) which are stored into the ZODB!

So PyAMS provides custom functions which allows, for example, to look for utilities into the local
registry before looking into the global one; the local registry is generally set during request
traversing (when using PyAMS own traverser) by a subscriber to IBeforeTraverseEvent on any
object providing ISite:

    >>> import pprint

    >>> from pyramid.testing import setUp, tearDown, DummyRequest
    >>> config = setUp(hook_zca=True)
    >>> config.registry
    <Registry testing>

    >>> from zope.component import getSiteManager
    >>> getSiteManager()
    <Registry testing>

We are going to initialize registry using ZCML files; this will initialize our components
registry with *zope.component* and *zope.dublincore* packages components:

    >>> from pyramid_zcml import includeme as include_zcml
    >>> include_zcml(config)
    >>> from cornice import includeme as include_cornice
    >>> include_cornice(config)
    >>> from cornice_swagger import includeme as include_swagger
    >>> include_swagger(config)
    >>> from pyams_utils import includeme as include_utils
    >>> include_utils(config)

    >>> from pyams_utils.registry import get_local_registry, set_local_registry
    >>> from pyams_utils.registry import get_registries, get_current_registry

    >>> get_current_registry()
    <Registry testing>
    >>> get_local_registry() is None
    True

Using a local registry requires a site:

    >>> from zope.site import LocalSiteManager
    >>> from zope.site.folder import Folder

    >>> root = Folder()
    >>> lsm = LocalSiteManager(root, default_folder=False)
    >>> root.setSiteManager(lsm)
    >>> root.getSiteManager() is lsm
    True

Let's now create a new request and handle traversing:

    >>> from zope.traversing.interfaces import BeforeTraverseEvent
    >>> from pyramid.events import NewRequest
    >>> from pyramid.threadlocal import manager
    >>> from pyams_utils.registry import handle_new_request, handle_site_before_traverse

    >>> request = DummyRequest(context=root)
    >>> handle_new_request(NewRequest(request))
    >>> handle_site_before_traverse(BeforeTraverseEvent(root, request))
    >>> pprint.pprint(manager.stack)
    [{'registry': <Registry testing>, 'request': None}]
    >>> get_local_registry() is lsm
    True
    >>> get_current_registry() is lsm
    False

We can get the list of available registries:

    >>> list(get_registries())
    [<LocalSiteManager ++etc++site>, <Registry testing>]

We create a custom registry for testing, but while running into Pyramid the global registry is
always Pyramid's global components registry (so that direct interfaces adapters always work without
requiring the registry); the "current" registry is not the local registry: it's the last registry
registered into Pyramid's stack:

    >>> get_current_registry()
    <Registry testing>

Let's now look for utilities; we will use a server timezone utility for this, which is defined
into PyAMS_utils package:

    >>> from zope.schema.vocabulary import getVocabularyRegistry
    >>> from pyams_utils.interfaces import TIMEZONES_VOCABULARY_NAME
    >>> from pyams_utils.timezone.vocabulary import TimezonesVocabulary
    >>> getVocabularyRegistry().register(TIMEZONES_VOCABULARY_NAME, TimezonesVocabulary)

    >>> from pyams_utils.interfaces.timezone import IServerTimezone
    >>> from pyams_utils.timezone.utility import ServerTimezoneUtility
    >>> tz = ServerTimezoneUtility()
    >>> tz.timezone
    'UTC'

We can register this utility into our local registry:

    >>> lsm['server_timezone'] = tz
    >>> lsm.registerUtility(tz, IServerTimezone, name='')

    >>> from pyams_utils.registry import registered_utilities, query_utility, get_utility, \
    ...                                  get_utilities_for, get_all_utilities_registered_for

    >>> list(registered_utilities())
    [UtilityRegistration(<LocalSiteManager ++etc++site>, IServerTimezone, '', server_timezone, None, ''), ...]
    >>> query_utility(IServerTimezone)
    <...ServerTimezoneUtility object at 0x...>
    >>> get_utility(IServerTimezone)
    <...ServerTimezoneUtility object at 0x...>
    >>> list(get_utilities_for(IServerTimezone))
    [('', <...ServerTimezoneUtility object at 0x...>)]
    >>> list(get_all_utilities_registered_for(IServerTimezone))
    [<...ServerTimezoneUtility object at 0x...>]

You can of course add several utilities for a same interface, as long as they are registered with
different names:

    >>> tz2 = ServerTimezoneUtility()
    >>> tz2.timezone = 'Europe/Paris'
    >>> lsm['tz2'] = tz2
    >>> lsm.registerUtility(tz2, IServerTimezone, name='tz2')

    >>> query_utility(IServerTimezone, name='tz2')
    <...ServerTimezoneUtility object at 0x...>
    >>> get_utility(IServerTimezone, name='tz2')
    <...ServerTimezoneUtility object at 0x...>
    >>> sorted(get_utilities_for(IServerTimezone))
    [('', <...ServerTimezoneUtility object at 0x...>), ('tz2', <...ServerTimezoneUtility object at 0x...>)]
    >>> list(get_all_utilities_registered_for(IServerTimezone))
    [<...ServerTimezoneUtility object at 0x...>, <...ServerTimezoneUtility object at 0x...>]

Looking for an unknown utility raises a ComponentLookupError:

    >>> from zope.intid.interfaces import IIntIds
    >>> get_utility(IIntIds)
    Traceback (most recent call last):
    ...
    zope.interface.interfaces.ComponentLookupError: (<InterfaceClass zope.intid.interfaces.IIntIds>, '')


Registering utilities
---------------------

A "utility_config" decorator is available to register a utility into global registry:

    >>> from zope.interface import Interface
    >>> from pyams_utils.registry import utility_config

    >>> class IMyUtility(Interface):
    ...     """Utility marker interface"""

    >>> class Utility:
    ...     """Utility class"""

You can then simulate a venusian decorator call:

    >>> from pyams_utils.testing import call_decorator

    >>> call_decorator(config, utility_config, Utility, provides=IMyUtility)
    >>> config.registry.getUtility(IMyUtility)
    <pyams_utils.tests.test_utilsdocs.Utility object at 0x...>

You can also register a utility instance instead of a factory:

    >>> class IMySecondUtility(Interface):
    ...     """Second utility interface"""

    >>> utility = Utility()
    >>> call_decorator(config, utility_config, utility, provides=IMySecondUtility)
    >>> config.registry.getUtility(IMySecondUtility)
    <pyams_utils.tests.test_utilsdocs.Utility object at 0x...>

You cna omit the "provides" argument of "utility_config" if the registered utility is
only implementing a single interface:

    >>> from zope.interface import implementer

    >>> class IMyThirdUtility(Interface):
    ...     """Third utility interface"""

    >>> @implementer(IMyThirdUtility)
    ... class ThirdUtility:
    ...     """Utility class"""

    >>> call_decorator(config, utility_config, ThirdUtility)
    >>> config.registry.getUtility(IMyThirdUtility)
    <pyams_utils.tests.test_utilsdocs.ThirdUtility object at 0x...>

    >>> utility = ThirdUtility()
    >>> call_decorator(config, utility_config, utility, name='third')
    >>> config.registry.getUtility(IMyThirdUtility, name='third')
    <pyams_utils.tests.test_utilsdocs.ThirdUtility object at 0x...>

If more than one interface are implemented, an exception is raised:

    >>> class IMyFourthUtility(Interface):
    ...     """Fourth utility interface"""

    >>> @implementer(IMyThirdUtility, IMyFourthUtility)
    ... class FourthUtility:
    ...     """Utility class"""

    >>> call_decorator(config, utility_config, FourthUtility)
    Traceback (most recent call last):
    ...
    TypeError: Missing 'provides' argument


Tests cleanup:

    >>> manager.pop()
    {...}
    >>> set_local_registry(None)
    >>> tearDown()
