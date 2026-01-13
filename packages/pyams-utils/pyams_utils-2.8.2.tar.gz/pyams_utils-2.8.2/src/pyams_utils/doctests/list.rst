
=======================
PyAMS_utils list module
=======================

This small module provides a few helpers to handle lists and iterators.


Getting unique elements of a list
---------------------------------

The "unique" function returns a list containing unique elements of an input list, in their
original order:

    >>> from pyams_utils.list import unique

    >>> mylist = [1, 2, 3, 2, 1]
    >>> unique(mylist)
    [1, 2, 3]

    >>> mylist = [3, 2, 2, 1, 4, 2]
    >>> unique(mylist)
    [3, 2, 1, 4]

You can also set an 'id' function applied on each element:

    >>> mylist = [1, 2, 3, '2', 4]
    >>> unique(mylist, key=str)
    [1, 2, 3, 4]

    >>> mylist = ['A', 'B', 'b', '2', 4]
    >>> unique(mylist, key=lambda x: str(x).lower())
    ['A', 'B', '2', 4]

The "unique_iter" functions is doing the same thing, but is working with iterators:

    >>> from pyams_utils.list import unique_iter

    >>> mylist = [1, 2, 3, 2, 1]
    >>> list(unique_iter(mylist))
    [1, 2, 3]

    >>> mylist = [3, 2, 2, 1, 4, 2]
    >>> list(unique_iter(mylist))
    [3, 2, 1, 4]

You can also set an 'id' function applied on each element:

    >>> mylist = [1, 2, 3, '2', 4]
    >>> list(unique_iter(mylist, key=str))
    [1, 2, 3, 4]

    >>> mylist = ['A', 'B', 'b', '2', 4]
    >>> list(unique_iter(mylist, key=lambda x: str(x).lower()))
    ['A', 'B', '2', 4]


Getting last elements of unique iterator lists
----------------------------------------------

The "unique_iter_last" is used to extract items from an iterator; if several items from this iterator
share the same identity key, only the "last" one (based on a provided sorting function) is returned:

    >>> from pyams_utils.list import unique_iter_max

    >>> mylist = [1.0, 2.0, 1.1, 2.0, 2.1, 2.2, 3, 4]
    >>> list(unique_iter_max(mylist, key=round))
    [1.1, 2.2, 3, 4]

    >>> class Item:
    ...     def __init__(self, value, label):
    ...         self.value = value
    ...         self.label = label
    ...     def __repr__(self):
    ...         return f"{self.value}: '{self.label}'"

    >>> mylist = [
    ...     Item(1.0, '1.0'),
    ...     Item(1.1, '1.1'),
    ...     Item(2.0, '2.0'),
    ...     Item(2.1, '2.1'),
    ...     Item(2.2, '2.2'),
    ...     Item(3, '3'),
    ...     Item(4, '4'),
    ... ]
    >>> list(unique_iter_max(mylist, key=lambda x: round(x.value), sort_key=lambda x: x.label))
    [1.1: '1.1', 2.2: '2.2', 3: '3', 4: '4']


List random iterator
--------------------

The "random_iter" returns an iterator over elements of an input iterable, selected in random
order:

    >>> from pyams_utils.list import random_iter

    >>> mylist = [1, 2, 3, 2, 1]
    >>> list(random_iter(mylist, 2))
    [..., ...]


Checking iterators for elements
-------------------------------

It's sometimes required to know if an iterator will return at least one element; it's the goal
of the "boolean_iter" function:

    >>> from pyams_utils.list import boolean_iter

    >>> def empty(input):
    ...     yield from input
    >>> mylist = empty(())
    >>> check, myiter = boolean_iter(mylist)
    >>> check
    False
    >>> list(myiter)
    []
    >>> mylist = empty((1,2,3))
    >>> check, myiter = boolean_iter(mylist)
    >>> check
    True
    >>> list(myiter)
    [1, 2, 3]
    >>> list(myiter)
    []

This function can also be used from a Chameleon template with a TALES extension:

    >>> from pyams_utils.list import BooleanIterCheckerExpression
    >>> mylist = empty(())
    >>> expression = BooleanIterCheckerExpression(mylist, None, None)
    >>> expression.render()
    (False, <generator object ... at 0x...>)

    >>> mylist = empty(())
    >>> expression = BooleanIterCheckerExpression(mylist, None, None)
    >>> expression.render(mylist)
    (False, <generator object ... at 0x...>)

    >>> mylist = empty((1,2,3))
    >>> expression = BooleanIterCheckerExpression(mylist, None, None)
    >>> expression.render()
    (True, <generator object ... at 0x...>)

This helper also handles StopIteration; with Python starting from 3.7,
please note that a StopIteration raised from inside an iterator is transformed
into a RuntimeError:

    >>> def custom(value):
    ...     if not value:
    ...         raise StopIteration
    ...     yield value
    >>> check, myiter = boolean_iter(custom([]))
    >>> check
    False


List grouped iterator
---------------------

The "grouped_iter" returns an iterator over elements of an input iterable, making sub-groups of
a given length:

    >>> from pyams_utils.list import grouped_iter

    >>> mylist = [1, 2, 3, 4, 5]
    >>> list(grouped_iter(mylist, 3))
    [(1, 2, 3), (4, 5, None)]
    >>> list(grouped_iter(mylist, 4, -1))
    [(1, 2, 3, 4), (5, -1, -1, -1)]

This function can also be used from a Chameleon template with a TALES extension:

    >>> from pyams_utils.list import GroupedIterCheckerExpression
    >>> mylist = empty(())
    >>> expression = GroupedIterCheckerExpression(mylist, None, None)
    >>> expression.render()
    <itertools.zip_longest object at 0x...>
    >>> list(expression.render())
    []

    >>> mylist = empty((1, 2, 3, 4, 5))
    >>> expression = GroupedIterCheckerExpression(mylist, None, None)
    >>> list(expression.render(length=4))
    [(1, 2, 3, 4), (5, None, None, None)]


Tee iterator TALES expression
-----------------------------

This TALES expression can be used when you have to create a tee on a given iterator:

    >>> from pyams_utils.list import IterValuesTeeExpression
    >>> mylist = empty((1, 2, 3, 4, 5))
    >>> myiter = iter(mylist)
    >>> expression = IterValuesTeeExpression(myiter, None, None)
    >>> results = expression.render()
    >>> results
    (<itertools._tee object at 0x...>, <itertools._tee object at 0x...>)
    >>> list(results[0])
    [1, 2, 3, 4, 5]
    >>> list(results[1])
    [1, 2, 3, 4, 5]


Getting next sequence value
---------------------------

    >>> from pyams_utils.list import next_from

    >>> next_from(None) is None
    True
    >>> next_from({'first'})
    'first'
    >>> next_from(('first', 'second'))
    'first'


List pagination
---------------

You can create subsets of an incoming list of any size:

    >>> from pyams_utils.list import paginate
    >>> mylist = [1, 2, 3, 4, 5]
    >>> list(paginate(mylist, 2))
    [[1, 2], [3, 4], [5]]
