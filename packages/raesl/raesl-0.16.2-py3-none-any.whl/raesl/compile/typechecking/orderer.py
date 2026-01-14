"""Generic class for resolving an order of checking 'things' assuming each thing
has a name, and knows the names of its direct dependencies.
"""
from typing import Dict, Iterable, List, Optional, Tuple

TypeOfData = Optional[None]


class OrdererEntry:
    """Entry in the orderer.

    Arguments:
        name: Name of the entry.
        data: Data associated with the entry.

    Attributes:
        needed_by: List of entries that depend on this entry. May only be accessed by
            the Orderer.
        depend_on: List of entries that need this entry. May only be accessed by
            the Orderer.
    """

    def __init__(self, name: str, data: TypeOfData) -> None:
        self.name = name
        self.data = data

        # Internal data.
        self.needed_by: List[OrdererEntry] = []
        self.depend_on: List[OrdererEntry] = []

    def __repr__(self):
        return "OrdererEntry[{}]".format(self.name)


class Orderer:
    """Class that orders entries so their 'needed_by' entries are processed first.

    Attributes:
        _independent_entries: Entries that do not depend on other entries.
        _dependent_entries: Entries that depend on other entries.
    """

    def __init__(self) -> None:
        self._independent_entries: Dict[str, OrdererEntry] = {}
        self._dependent_entries: Dict[str, OrdererEntry] = {}

    def add_dependency(self, provide: str, needs: Iterable[str], data: TypeOfData = None):
        """Add a dependency where the 'provide' name depends on the 'needs' names.

        Arguments:
            provide: Name of the 'thing' that this dependency provides.
            needs: Names of 'things' that are required by the provide 'thing'.
            data: Optional data associated with 'provide'. At most one such data item
                should exist, class cannot handle multiple data items.
        """
        provide_entry = self._find_create_entry(provide, data)
        provide_independent = len(provide_entry.depend_on) == 0

        # Add needs as 'things' it depends on.
        for need in needs:
            need_entry = self._find_create_entry(need)
            need_entry.needed_by.append(provide_entry)
            provide_entry.depend_on.append(need_entry)

        # If 'provide_entry' became dependent, move it.
        if provide_independent and len(provide_entry.depend_on) > 0:
            del self._independent_entries[provide]
            self._dependent_entries[provide] = provide_entry

    def resolve(self) -> Tuple[List[OrdererEntry], Optional[List[OrdererEntry]]]:
        """Resolve the dependency chain by peeling away independent entries. This should
        cause some dependent entries to become independent, allowing them to be peeled
        as well.

        Returns:
            Ordered sequence of entries containing name and associated data, and
                optionally a cycle of entries if at least one cycle exists. Note that
                the Orderer returns one arbitrary cycle in such a case.
        """
        ordered = []
        while len(self._independent_entries) > 0:
            entry = self._independent_entries.popitem()[1]
            assert len(entry.depend_on) == 0
            ordered.append(entry)

            # Peeling done, update dependent entries.
            while len(entry.needed_by) > 0:
                dependent = entry.needed_by.pop()
                dependent.depend_on.remove(entry)
                if len(dependent.depend_on) == 0:
                    # Dependent entry became independent!
                    del self._dependent_entries[dependent.name]
                    self._independent_entries[dependent.name] = dependent

        if len(self._dependent_entries) == 0:
            return ordered, None

        # We have at least one cycle, find one.
        def find_cycle(
            stack: List[OrdererEntry], entry_indices: Dict[OrdererEntry, int]
        ) -> Optional[List[OrdererEntry]]:
            entry = stack[-1]
            for dep in entry.needed_by:
                if dep in entry_indices:
                    # Bingo!
                    return stack[entry_indices[dep] :]
                entry_indices[dep] = len(stack)
                stack.append(dep)
                cycle = find_cycle(stack, entry_indices)
                if cycle is not None:
                    return cycle
                stack.pop()
                del entry_indices[dep]
            return None

        entry = next(iter(self._dependent_entries.values()))
        stack = [entry]
        entry_indices = {entry: 0}
        cycle = find_cycle(stack, entry_indices)
        assert cycle is not None
        return ordered, cycle

    def find_entry(self, name: str) -> Optional[OrdererEntry]:
        """Try to find an entry with the provided name. Useful for duplicate name
        detection.

        Returns:
            The found entry (treat as read-only), or None.
        """
        entry = self._independent_entries.get(name)
        if entry is not None:
            entry = self._dependent_entries.get(name)
        return entry

    def _find_create_entry(self, name: str, data: TypeOfData = None) -> OrdererEntry:
        """Find or create an entry with the provide name.

        Arguments:
            name: name of the entry to find or create.
            data: Optional data associated with the name. It is copied into the entry
                whenever possible without overwriting existing data.

        Returns:
            The entry.
        """
        entry = self._independent_entries.get(name)
        if entry is not None:
            if entry.data is None and data is not None:
                entry.data = data
            return entry

        entry = self._dependent_entries.get(name)
        if entry is not None:
            if entry.data is None and data is not None:
                entry.data = data
            return entry

        entry = OrdererEntry(name, data)
        self._independent_entries[name] = entry
        return entry
