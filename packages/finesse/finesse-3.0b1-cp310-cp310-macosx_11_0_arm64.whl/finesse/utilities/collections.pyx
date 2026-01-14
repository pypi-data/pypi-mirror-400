
cdef class OrderedSet:
    """An ordered set implementation using an Dictionary to maintain the order of
    elements. Dictionaries in recent Python versions are all ordered now.

    Parameters
    ----------
    iterable : iterable, optional
        An optional iterable to initialize the ordered set with elements.

    Attributes
    ----------
    _dict : Dict
        The internal dictionary used to maintain order and uniqueness of elements.

    Methods
    -------
    add(item)
        Add an element to the OrderedSet.
    remove(item)
        Remove an element from the OrderedSet.
    difference_update(iterable)
        Remove all elements from the OrderedSet that are also in the provided iterable.
    update(iterable)
        Add all elements from the provided iterable to the OrderedSet.
    clear()
        Remove all elements from the OrderedSet.
    __contains__(item)
        Check if an element is in the OrderedSet.
    __iter__()
        Return an iterator over the elements of the OrderedSet.
    __len__()
        Return the number of elements in the OrderedSet.
    __repr__()
        Return a string representation of the OrderedSet.
    """

    def __init__(self, iterable=None):
        """Initialize the OrderedSet with an optional iterable of elements.

        Parameters
        ----------
        iterable : iterable, optional
            An optional iterable to initialize the ordered set with elements.
        """
        self._dict = {}
        if iterable:
            for item in iterable:
                self._dict[item] = None

    def add(self, item):
        """Add an element to the OrderedSet.

        Parameters
        ----------
        item : object
            The element to be added to the OrderedSet.
        """
        self._dict[item] = None

    def remove(self, item):
        """Remove an element from the OrderedSet.

        Parameters
        ----------
        item : object
            The element to be removed from the OrderedSet.

        Raises
        ------
        KeyError
            If the element is not present in the OrderedSet.
        """
        self._dict.pop(item)

    def difference_update(self, iterable):
        """Remove all elements from the OrderedSet that are also in the provided
        iterable.

        Parameters
        ----------
        iterable : iterable
            An iterable containing elements to be removed from the OrderedSet.
        """
        for item in iterable:
            self._dict.pop(item, None)

    def update(self, iterable):
        """Add all elements from the provided iterable to the OrderedSet.

        Parameters
        ----------
        iterable : iterable
            An iterable containing elements to be added to the OrderedSet.
        """
        for item in iterable:
            self._dict[item] = None

    def clear(self):
        """Remove all elements from the OrderedSet."""
        self._dict.clear()

    def __contains__(self, item):
        """Check if an element is in the OrderedSet.

        Parameters
        ----------
        item : object
            The element to be checked.

        Returns
        -------
        bool
            True if the element is in the OrderedSet, False otherwise.
        """
        return item in self._dict

    def __iter__(self):
        """Return an iterator over the elements of the OrderedSet.

        Returns
        -------
        iterator
            An iterator over the elements of the OrderedSet.
        """
        return iter(self._dict.keys())

    def __len__(self):
        """Return the number of elements in the OrderedSet.

        Returns
        -------
        int
            The number of elements in the OrderedSet.
        """
        return len(self._dict)

    def __repr__(self):
        """Return a string representation of the OrderedSet.

        Returns
        -------
        str
            A string representation of the OrderedSet.
        """
        return f"OrderedSet{tuple(self._dict.keys())}"

    def difference(self, other):
        """Return a new OrderedSet with elements that are the difference between the
        two.

        Parameters
        ----------
        other : OrderedSet
            Another OrderedSet to subtract from this set.

        Returns
        -------
        OrderedSet
            A new OrderedSet with the difference between the sets.
        """
        result = OrderedSet()
        for item in self._dict:
            if item not in other:
                result.add(item)
        return result

    def __sub__(self, other):
        """Return a new OrderedSet with elements that are the difference between the
        two.

        Parameters
        ----------
        other : OrderedSet
            Another OrderedSet to subtract from this set.

        Returns
        -------
        OrderedSet
            A new OrderedSet with the difference between the sets.
        """
        return self.difference(other)

    def union(self, *others):
        """Return a new OrderedSet with elements from the union of this set and `other`.

        Parameters
        ----------
        others : OrderedSet
            Another OrderedSet to union with this set.

        Returns
        -------
        OrderedSet
            A new OrderedSet with all unique elements from both sets.
        """
        result = OrderedSet(self)
        for other in others:
            result.update(other)
        return result

    def __or__(self, other):
        """Return a new OrderedSet with elements from the union of this set and `other`.

        Parameters
        ----------
        other : OrderedSet
            Another OrderedSet to union with this set.

        Returns
        -------
        OrderedSet
            A new OrderedSet with all unique elements from both sets.
        """
        return self.union(other)

    def __and__(self, other):
        """Return a new OrderedSet with elements that are present in both this set and
        `other`.

        Parameters
        ----------
        other : OrderedSet
            Another OrderedSet to intersect with this set.

        Returns
        -------
        OrderedSet
            A new OrderedSet with elements common to both sets.
        """
        result = OrderedSet()
        for item in self._dict:
            if item in other:
                result.add(item)
        return result

    def issubset(self, other):
        """Check if this set is a subset of another set.

        Parameters
        ----------
        other : OrderedSet
            Another OrderedSet to check against.

        Returns
        -------
        bool
            True if this set is a subset of `other`, False otherwise.
        """
        for item in self._dict:
            if item not in other:
                return False
        return True

    def __eq__(self, other):
        """Check if this set is equal to another set.

        Parameters
        ----------
        other : OrderedSet
            Another OrderedSet to compare against.

        Returns
        -------
        bool
            True if both sets contain the same elements in the same order, False otherwise.
        """
        if isinstance(other, OrderedSet):
            return list(self._dict.keys()) == list(other._dict.keys())
        elif isinstance(other, set):
            return set(self._dict.keys()) == other
        return False

    def copy(self):
        """
        Create a shallow copy of this OrderedSet.

        Returns
        -------
        OrderedSet
            A new OrderedSet with the same elements as the current set.
        """
        return OrderedSet(self._dict.keys())
