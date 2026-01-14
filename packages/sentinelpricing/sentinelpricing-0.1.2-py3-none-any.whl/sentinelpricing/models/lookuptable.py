import uuid
from bisect import bisect_left
from collections import namedtuple
from typing import List, Dict, Any, Optional, Tuple, Union, Hashable

from .rate import Rate


class Cache:

    def __init__(self, maxsize: int = 128) -> None:
        self._cache: Dict[Tuple, int] = {}
        self._hits: Dict[Tuple, int] = {}
        self.maxsize: int = maxsize

    def __contains__(self, key):
        return key in self._cache

    def __getitem__(self, key):
        self._hits[key] += 1
        return self._cache[key]

    def __setitem__(self, key, value):
        if key in self._cache:
            self._cache[key] = value
            return

        if len(self._cache) == self.maxsize:
            lru_keys = sorted(self._hits.items(), key=lambda x: x[1])[
                : self.maxsize // 2
            ]
            for k, v in lru_keys:
                self._cache.pop(k)
                self._hits.pop(k)

        self._cache[key] = value
        self._hits[key] = 1

    def __in__(self, key: Any) -> bool:
        return key in self._cache


class LookupTable:
    """
    A lookup table for mapping multi-dimensional keys to rating values.

    This class builds a lookup table from a list of dictionaries, where each
    dictionary represents a row with index keys and an associated rating
    value. It supports both one-dimensional and multi-dimensional lookups via
    binary search.

    The input data must be structured in a specific CSV format where the rate
    column(default key: "rate") is separated from the index columns. For
    multi-dimensional lookups, the CSV should be arranged in a "vertical"
    format (see examples below).

    If you have multivariate rating tables, you will benefit from
    restructuring your tables prior to use with this package.

    Original - Will not work, or rather it may work but it will not be
        imported correctly.
        Rating Table: Age vs Licence Years
            Lic
        Age |0|1|2|3
        21  |9|8|7|6
        30  |7|6|5|4
        40  |5|5|4|2

    Rearranged - Will work and be imported correctly.
        Age |Lic|Rate
        21  |0  |9
        21  |1  |8
        21  |2  |7
        21  |3  |6
        30  |0  |7
        30  |1  |6
        30  |2  |5
        30  |3  |4
        40  |0  |5
        40  |1  |5
        40  |2  |4
        40  |3  |2
    """

    def __init__(
        self,
        data: List[Dict[str, Any]],
        rate_column: Optional[str] = None,
        name: Optional[str] = None,
        use_cache: bool = True,
    ) -> None:
        """
        Initialize a new instance of LookupTable.

        Args:
            data (List[Dict[str, Any]]): A list of dictionaries representing
                the lookup table rows. Each dictionary should contain one or
                more index keys along with a rating value.
            rate_column (str, optional): The key in each dictionary
                corresponding to the rate value. Defaults to "rate" if not
                provided.
            name (str, optional): A human-readable name for the lookup table.
            cache (bool, optional): A bool enabling a lru cache over the
                lookup method.
        """
        rate_column = rate_column or "rate"
        rates: List[float] = []
        indexes: List[Dict[str, Any]] = []

        # Process each row in the input data.
        for row in data:
            if rate_column not in row:
                raise KeyError(f"Invalid or missing rate key in row: {row}")
            rates.append(float(row[rate_column]))

            # Process index values: if a value is a numeric string,
            # convert it to float.
            index_entry = {}
            for k, v in row.items():
                if k == rate_column:
                    continue
                if isinstance(v, str) and v.replace(".", "", 1).isdigit():
                    index_entry[k] = float(v)
                else:
                    index_entry[k] = v
            indexes.append(index_entry)

        if not indexes or not rates:
            raise ValueError("Data cannot be empty.")

        # Determine lookup dimensionality based on the number of index keys.
        index_keys = list(indexes[0].keys())
        if len(index_keys) == 1:
            self.dimension = (0, "One-Dimensional")
        elif len(index_keys) > 1:
            self.dimension = (1, "Multi-Dimensional")
        else:
            raise ValueError("No index keys found in the data.")

        # Create a namedtuple type for the index using the order of index_keys.
        # Because of the dynamic way we're creating these namedtuples, mypy
        # throws an error as it expects a literal it can analyse.
        # We're going to ignore it until it matters.
        Index = namedtuple("Index", index_keys)  # type: ignore
        self.index_type = Index

        # Build the list of index entries using the established key order.
        self.index: List[Tuple] = [
            Index(*(row[k] for k in index_keys)) for row in indexes
        ]
        self.rates: List[float] = rates
        self.name: Optional[str] = name or uuid.uuid4().hex

        # Ensure the lookup table is sorted by index.
        combined = sorted(
            zip(self.index, self.rates), key=lambda pair: pair[0]
        )
        self.index, self.rates = map(list, zip(*combined))

        self.cache: Optional[Cache] = None
        if use_cache:
            self.cache = Cache()

    def __len__(self):
        return len(self.index)

    def __getitem__(self, key: Union[Any, Tuple[Any, ...]]) -> "Rate":
        """
        Enable subscript notation for lookups.

        Args:
            key (Any or Tuple[Any, ...]): A single key or a tuple of keys
                corresponding to the index dimensions.

        Returns:
            Rate: The resulting rate wrapped in a Rate object.
        """
        if not isinstance(key, tuple):
            key = (key,)

        return self.lookup(*key)

    def lookup(self, *keys: Hashable) -> "Rate":
        """
        Retrieve a rate value from the lookup table based on the provided keys.

        The keys should match the number of index dimensions of the table.

        Args:
            *keys: The key values for the lookup.

        Returns:
            Rate: An instance of Rate containing the lookup table name and
                another found rate value.

        Raises:
            KeyError: If the number of keys provided does not match the table
                dimensions.
        """
        if not self.index or len(keys) != len(self.index[0]):
            raise KeyError("Incompatible number of keys provided.")

        if self.cache is not None and keys in self.cache:
            return Rate(
                self.name or "Unnamed Rate", self.rates[self.cache[keys]]
            )

        # Create an index key using the namedtuple type.
        search_key = self.index_type(*keys)

        idx = bisect_left(self.index, search_key)

        # Determine the appropriate rate value.
        if idx == 0:
            pass
        if idx < len(self.index) and self.index[idx] == search_key:
            pass
        elif idx < len(self.index) and self.index[idx] > search_key:
            idx = idx - 1
        else:
            idx = idx - 1

        rate_value = self.rates[idx]

        if self.cache:
            self.cache[keys] = idx

        return Rate(self.name or "Unnamed Rate", rate_value)
