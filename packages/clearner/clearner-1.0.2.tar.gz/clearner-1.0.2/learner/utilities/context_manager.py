from contextlib import contextmanager
from collections import namedtuple

"""Implement some helper context manager functions.

"""
AttributeChange = namedtuple('AttributeChange', ['obj', 'attr', 'value'])


@contextmanager
def temporary_attrs(changes):
    """Accept a list of AttributeChange named tuples (see the top of the module) to temporarily change the attribute of some objects
    within a context.

    :param changes: a list of AttributeChange named tuples
    :return: None
    """
    # Save original values
    originals = {
        (change.obj, change.attr): getattr(change.obj, change.attr)
        for change in changes
    }
    try:
        # Apply temporary changes
        for change in changes:
            setattr(change.obj, change.attr, change.value)
        yield
    finally:
        # Restore originals
        for (obj, attr), original_value in originals.items():
            setattr(obj, attr, original_value)
