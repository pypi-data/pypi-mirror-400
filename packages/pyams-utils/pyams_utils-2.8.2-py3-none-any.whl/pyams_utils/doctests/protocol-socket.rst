
=================
PyAMS TCP helpers
=================

PyAMS provides a small helper to check a TCP port:

    >>> from pyams_utils.protocol.tcp import is_port_in_use

    >>> is_port_in_use(59999, 'localhost')
    False
