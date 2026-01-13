# Copyright (c) 2026 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from collections import deque
from typing import Callable, List, Tuple


class FSPathVerb(object): pass


class Root(FSPathVerb):
    """Step to the root directory `root`."""
    __slots__ = ('root',)

    def __init__(
            self,
            root,  # type: str
    ):
        self.root = root  # type: str

    def __repr__(self):
        return '%s(root=%r)' % (self.__class__.__name__, self.root)

    def __reduce__(self):
        return self.__class__, (self.root,)

    def __hash__(self):
        return hash(self.__reduce__())

    def __eq__(self, other):
        return self.__reduce__() == other.__reduce__()


class Parent(FSPathVerb):
    """Step to the parent directory."""

    def __repr__(self):
        return '%s()' % (self.__class__.__name__,)

    def __reduce__(self):
        return self.__class__, ()

    def __hash__(self):
        return hash(self.__reduce__())

    def __eq__(self, other):
        return self.__reduce__() == other.__reduce__()


class Current(FSPathVerb):
    """Step to the current directory."""

    def __repr__(self):
        return '%s()' % (self.__class__.__name__,)

    def __reduce__(self):
        return self.__class__, ()

    def __hash__(self):
        return hash(self.__reduce__())

    def __eq__(self, other):
        return self.__reduce__() == other.__reduce__()


class Child(FSPathVerb):
    """Step to the child `child` (file or directory)."""
    __slots__ = ('child',)

    def __init__(
            self,
            child,  # type: str
    ):
        self.child = child  # type: str

    def __repr__(self):
        return '%s(child=%r)' % (self.__class__.__name__, self.child)

    def __reduce__(self):
        return self.__class__, (self.child,)

    def __hash__(self):
        return hash(self.__reduce__())

    def __eq__(self, other):
        return self.__reduce__() == other.__reduce__()


def compile_to_fspathverbs(
        path,  # type: str
        split,  # type: Callable[[str], Tuple[str, str]]
):
    # type: (...) -> List[FSPathVerb]
    head_tail_pairs = deque()  # type: deque[Tuple[str, str]]
    while True:
        head, tail = split(path)
        if head_tail_pairs and (head, tail) == head_tail_pairs[0]:
            break  # Detect infinite loop on e.g. posix '/'
        else:
            head_tail_pairs.appendleft((head, tail))
            path = head

    verbs = []

    head, _ = head_tail_pairs.popleft()
    if not head:
        verbs.append(Current())
    else:
        verbs.append(Root(root=head))

    while head_tail_pairs:
        _, tail = head_tail_pairs.popleft()
        if tail in ('', '.'):
            verbs.append(Current())
        elif tail == '..':
            verbs.append(Parent())
        else:
            verbs.append(Child(child=tail))

    return verbs
