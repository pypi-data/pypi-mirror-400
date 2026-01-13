from __future__ import annotations

import os
from collections import deque
from collections.abc import Iterable
import pathlib

from atomflow.atom import Atom
from atomflow.components import NameComponent, ResidueComponent, IndexComponent
from atomflow.formats import Format


END = object()


class AtomIterator:

    """
    Base iterator over groups of atoms.

    >>> from atomflow.atom import Atom
    >>> from atomflow.components import NameComponent, ResidueComponent, IndexComponent

    >>> atom_a = Atom(NameComponent("A"), ResidueComponent("X"), IndexComponent(3))
    >>> atom_b = Atom(NameComponent("B"), ResidueComponent("X"), IndexComponent(1))
    >>> atom_c = Atom(NameComponent("C"), ResidueComponent("Y"), IndexComponent(2))
    >>> a_iter = AtomIterator.from_list([atom_a, atom_b, atom_c])
    >>> assert list(a_iter) == [(atom_a,), (atom_b,), (atom_c,)]

    AtomIterator.collect() brings all atoms into a single group.
    >>> a_iter = AtomIterator.from_list([atom_a, atom_b, atom_c]).collect()
    >>> assert list(a_iter) == [(atom_a, atom_b, atom_c)]

    While .to_list() flattens the groups.
    >>> a_iter = AtomIterator.from_list([atom_a, atom_b, atom_c]).to_list()
    >>> assert list(a_iter) == [atom_a, atom_b, atom_c]

    Subclasses are iterators that can be passed between each other via functions inherited from
    this class.
    >>> a_iter = AtomIterator.from_list([atom_a, atom_b, atom_c])
    >>> a_list = a_iter.group_by("resname").filter("name", none_of=["B"]).to_list()
    >>> assert a_list == [atom_c]

    Sort atoms based on a given key aspect.
    >>> a_iter = AtomIterator.from_list([atom_a, atom_b, atom_c])
    >>> a_list = a_iter.sort("index").to_list()
    >>> assert a_list == [atom_b, atom_c, atom_a]
    """

    def __init__(self, atom_groups: Iterable[Iterable[Atom]]):
        self._atom_groups = iter(atom_groups)

    def __next__(self):
        return next(self._atom_groups)

    def __iter__(self):
        return self

    def group_by(self, key: str | None = None):
        return GroupIterator(self, key)

    def filter(self, key: str, any_of: None | Iterable = None, none_of: None | Iterable = None) -> AtomIterator:
        return FilterIterator(self, key, any_of, none_of)

    @classmethod
    def from_list(cls, atoms: Iterable[Atom]) -> AtomIterator:
        return GroupIterator([atoms])

    def collect(self) -> AtomIterator:
        return AtomIterator([tuple(self.to_list())])

    def sort(self, key: str):
        return AtomIterator([sorted(self.to_list(), key=lambda a: a[key])])

    def to_list(self) -> list[Atom]:
        return [atm for grp in self for atm in grp]

    def write(self, path: str | os.PathLike) -> str | list[str]:

        """
        Writes atoms group-wise to the path. Intended format is inferred from the file
        extension. If multiple files are produces, variations on the file name are produced
        automatically.

        :param path: location for output file, e.g. './data/struct.pdb'
        :return: path(s) to outputs
        """

        outpaths = []

        # Retrieve the correct format
        path = pathlib.Path(path)
        ext = path.suffix
        writer = Format.get_format(ext)

        # Write each group as it arrives
        for i, group in enumerate(self):
            stem = path.stem if i == 0 else f"{path.stem}_{i}"
            outpath = path.parent / f"{stem}{ext}"
            writer.to_file(group, outpath)
            outpaths.append(outpath)

        # Return the written filepaths
        match len(outpaths):
            case 0:
                raise ValueError("No atoms written")
            case 1:
                return str(outpaths[0])
            case _:
                return [str(o) for o in outpaths]


class GroupIterator(AtomIterator):

    """
    Dispense sequential atoms grouped by a given aspect.

    >>> from atomflow.atom import Atom
    >>> from atomflow.components import NameComponent, ResidueComponent

    >>> atom_a = Atom(NameComponent("A"), ResidueComponent("X"))
    >>> atom_b = Atom(NameComponent("B"), ResidueComponent("Y"))
    >>> atom_c = Atom(NameComponent("B"), ResidueComponent("X"))
    >>> g_iter = GroupIterator([(atom_a, atom_b, atom_c)], group_by="name")
    >>> assert list(g_iter) == [(atom_a,), (atom_b, atom_c)]

    Only collects sequential similar atoms.
    >>> g_iter = GroupIterator([(atom_a, atom_b, atom_c)], group_by="resname")
    >>> assert list(g_iter) == [(atom_a,), (atom_b,), (atom_c,)]

    If no grouping value is given, each atom is grouped separately
    >>> g_iter = GroupIterator([(atom_a, atom_b, atom_c)])
    >>> assert list(g_iter) == [(atom_a,), (atom_b,), (atom_c,)]
    """

    def __init__(self, atom_groups, group_by=None):

        super().__init__(atom_groups)

        self._group_by = group_by

        self._last_value = None
        self._queue = deque()
        self._source_state = None
        self._buffer = []

    def __next__(self):

        # If no atoms left to dispense, signal end of iteration
        if self._source_state == END:
            raise StopIteration

        while True:

            # If the queue is empty
            if len(self._queue) == 0:

                # Try to withdraw the next group of atoms from the source, and add to the queue
                try:
                    next_group = next(self._atom_groups)
                    self._queue.extend(next_group)

                # If source is empty, return the remaining buffer contents and set up end of iterator
                except StopIteration:
                    self._source_state = END
                    return tuple(self._buffer)

            # Get the next atom and its grouping value. If no grouping key was given, use
            # object id as the value so that each atom gets grouped separately.
            atom = self._queue.popleft()
            value = atom[self._group_by] if self._group_by is not None else id(atom)

            # If the atom is the first, or it has the same grouping value as the previous, add
            # it to the buffer
            if self._last_value in (None, value):
                self._buffer.append(atom)
                self._last_value = value

            # If the atom has a new grouping value, output the buffer and reinitialise with this atom
            else:
                out = self._buffer[:]
                self._buffer = [atom]
                self._last_value = value
                return tuple(out)


class FilterIterator(AtomIterator):

    """
    Filter Atoms based on either allowed or disallowed values of an aspect.

    >>> from atomflow.atom import Atom

    >>> atom_a = Atom(NameComponent("A"))
    >>> atom_b = Atom(NameComponent("B"))
    >>> atom_groups = [(atom_a,), (atom_b,)]
    >>> f_iter = FilterIterator(atom_groups, "name", none_of=["B"])
    >>> assert list(f_iter) == [(atom_a,)]

    If any one atom in a group matches the any_of or none_of conditions, the whole group is included or
    excluded, respectively.

    >>> atom_c = Atom(NameComponent("C"))
    >>> atom_groups = [(atom_a, atom_c), (atom_b,)]
    >>> f_iter = FilterIterator(atom_groups, "name", none_of=["C"])
    >>> assert list(f_iter) == [(atom_b,)]

    >>> f_iter = FilterIterator(atom_groups, "name", any_of=["A"])
    >>> assert list(f_iter) == [(atom_a, atom_c)]
    """

    def __init__(self, atom_groups, key,
                 any_of: None | Iterable = None, none_of: None | Iterable = None):

        super().__init__(atom_groups)

        self.key = key

        if any_of is None:
            self._filter = lambda group: not any(atom[key] in none_of for atom in group)
        elif none_of is None:
            self._filter = lambda group: any(atom[key] in any_of for atom in group)
        else:
            raise ValueError("One of 'any_of' or 'none_of' must be provided")

    def __next__(self):
        while True:
            group = next(self._atom_groups)
            if self._filter(group):
                return group


def read(path: str | os.PathLike) -> AtomIterator:

    """
    Read a file into an iterator of atoms. Format is inferred from file extension.
    """

    path = pathlib.Path(path)
    reader = Format.get_format(path.suffix)
    atoms = reader.read_file(path)
    return AtomIterator.from_list(atoms)


if __name__ == '__main__':
    pass