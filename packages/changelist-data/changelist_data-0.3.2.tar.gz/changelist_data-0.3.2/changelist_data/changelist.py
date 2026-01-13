""" The Changelist Data container.

**Properties:**
 - id (str): The unique id of the changelist.
 - name (str): The name of the changelist.
 - changes (list[FileChange]): The list of FileChange data objects.
 - comment (str): The comment associated with the changelist. Default: Empty String.
 - is_default (bool): Whether this is the active changelist. Default: False.
"""
from collections import namedtuple
from typing import Iterable


Changelist = namedtuple(
    'Changelist',
    ('id', 'name', 'changes', 'comment', 'is_default'),
    defaults=('', False),
)


def get_default_cl(
    changelists: list[Changelist] | Iterable[Changelist],
) -> Changelist | None:
    """ Find the Default Changelist, or the first Changelist.
- Returns None if collection argument is empty.
- Handles list arguments slightly differently from Iterables.

**Parameters:**
 - changelists (list | Iterable[Changelist]): The collection of Changelist data objects.

**Returns:**
 Changelist? - The Default, or first CL, or None if the collection was empty.
    """
    if isinstance(changelists, list):
        try:
            return filter(lambda x: x.is_default, changelists).__next__()
        except StopIteration:
            pass
        try:
            return changelists[0]
        except IndexError:
            return None
    elif isinstance(changelists, Iterable) and not isinstance(changelists, Changelist):
        try:
            iterator = changelists.__iter__()
            if (first := iterator.__next__()).is_default:
                return first
            try:
                return filter(lambda x: x.is_default, iterator).__next__()
            except StopIteration:
                return first
        except StopIteration:
            return None
    else:
        raise TypeError(type(changelists))


def compute_key(cl_name: str) -> str:
    """ Compute a Key to use for a given Changelist Name.
 - computation is a sequence of reduction operations

**Parameters:**
 - cl_name (str): The Changelist Name to use in key computation.

**Returns:**
 str - A Key that can be used for changelist lookups, or an empty str.
    """
    if len(cl_name) == 0:
        return ''
    translator = str.maketrans('', '', ' :/\\')
    words = cl_name.translate(translator).split()
    return ''.join(w.lower() for w in words)
