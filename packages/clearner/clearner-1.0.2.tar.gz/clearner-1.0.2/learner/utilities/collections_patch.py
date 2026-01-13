"""
Compatibility patch for Python 3.12 collections module
"""
import collections
import collections.abc

# Patch collections module for Python 3.12 compatibility
if not hasattr(collections, 'Sequence'):
    collections.Sequence = collections.abc.Sequence
    collections.Mapping = collections.abc.Mapping
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Iterable = collections.abc.Iterable
    collections.Iterator = collections.abc.Iterator
    collections.Callable = collections.abc.Callable
    collections.Set = collections.abc.Set
    collections.MutableSet = collections.abc.MutableSet
    collections.MutableSequence = collections.abc.MutableSequence
