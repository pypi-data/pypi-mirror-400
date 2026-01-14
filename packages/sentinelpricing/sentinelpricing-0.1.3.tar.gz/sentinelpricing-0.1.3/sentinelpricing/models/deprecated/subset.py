class Subset(tuple):
    """Subset

    Often, we have to select groups/subsets from our data, we could need
    to segment by age, or other factor.

    The Subset class provides a simple way to implement these
    filters/groups/subsets in a way that doesn't require lot's
    of code (on your part...).

    """

    def __init__(self, data_dict=None, *args, **kwargs):

        raise RuntimeError("Subset is deprecated, do not use.")

        self._fields = []

        for k, v in kwargs.items():
            self._fields.append(k)
            setattr(self, k, v)

    def __iter__(self):
        return iter(self._fields)

    def __repr__(self):
        return (
            "("
            + ",".join([f"{k}={getattr(self, k)}" for k in self._fields])
            + ")"
        )

    def __getitem__(self, key):
        return getattr(self, key)

    def __lt__(self, other):
        if all(
            getattr(self, field) < getattr(other, field)
            for field in self._fields
        ):
            return True
        return False

    def __le__(self, other):
        if all(
            getattr(self, field) <= getattr(other, field)
            for field in self._fields
        ):
            return True
        return False

    def __gt__(self, other):
        if all(
            getattr(self, field) > getattr(other, field)
            for field in self._fields
        ):
            return True
        return False

    def __ge__(self, other):
        if all(
            getattr(self, field) >= getattr(other, field)
            for field in self._fields
        ):
            return True
        return False

    def __eq__(self, other):
        if not isinstance(other, Subset):
            raise NotImplementedError(
                f"Only implemented subset on subset so far: {type(other)}"
            )

        if set(self._fields) != set(other._fields):
            return False
        if all(
            getattr(self, field) == getattr(other, field)
            for field in self._fields
        ):
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        keys = ""
        values = ""
        for k in self._fields:
            keys += k
            values += str(getattr(self, k))
        return hash(keys + values)

    def __contains__(self, other):
        if len(other._fields) >= len(self._fields):
            if any(
                getattr(self, field) == getattr(other, field)
                for field in other._fields
            ):
                return True
        return False

    def keys(self):
        return iter(self._fields)

    def values(self):
        for field in self._fields:
            yield getattr(self, field)

    def items(self):
        for field in self._fields:
            yield field, getattr(self, field)
