"""Test Case

So some quick testing revealed that the quote object needs to be separated.

It needs to be split into two classes, one dedicated to holding the data needed
to create the quote, the other to hold the calculations/history.

"""

from typing import (
    Any,
    List,
    Dict,
    Union,
    Iterable,
)

from .testcase import TestCase
from sentinelpricing.utils.calculations import dict_difference, percentage


class TestSuite:
    """Test Suite

    This class represents a group of testcases that you need to test.

    Typical usage would be to load quotes from a file, whether it be
    JSON, CSV, or XML (Or even a pandas dataframe).

        >>> TestSuite.from_csv("path/to/file.csv")
        TestSuite()

    The initialized test suite can then be used to generate quotes
    against frameworks you have predefined:

        >>> from .frameworks import motor_r22
        >>> quotes: QuoteSet = tests.quote(motor_r22)
        QuoteSet()

    Note: the uninstantiated framework is passed. Sentinel handles
    instantiating the framework automatically.

    When using the 'quote' method in the TestSuite, the response is a
    QuoteSet. The QuoteSet contains all details relating to price, and
    a copy of the quote data used to generate the quote.
    """

    def __init__(self, tests: Iterable[Union[TestCase, Dict]]):
        # TODO: Covert this to only accept dict/mapping, having both lists and
        # dicts is confusing. Especially so, given we can easily convert a list
        # to a dict using the index as a key.

        if all(not isinstance(t, (dict, TestCase)) for t in tests):
            raise TypeError("Expected dict or TestCase")

        self.testcases: List[TestCase] = list(
            map(lambda x: TestCase(x) if isinstance(x, dict) else x, tests)
        )

    def __iter__(self) -> Iterable[TestCase]:
        return iter(self.testcases)

    def __len__(self) -> int:
        return len(self.testcases)

    def __getitem__(self, k):
        return self.testcases[k]

    def __add__(self, other: "TestSuite") -> "TestSuite":
        """
        Combine two TestSuites.

        Args:
            other (TestSuite): Another TestSuite to add.

        Returns:
            TestSuite: A new TestSuite containing testcases from both sets.
        """
        if not isinstance(other, TestSuite):
            raise ValueError(f"Expected TestSuite, got {other.__name__}")

        return TestSuite(self.testcases + other.testcases)

    def __sub__(self, other: "TestSuite") -> "TestSuite":
        """
        Subtract two TestSuites.

        Args:
            other (TestSuite): TestSuite to remove.

        Returns:
            TestSuite: A new TestSuite containing testcases from A minus B.
        """

        if not isinstance(other, TestSuite):
            raise ValueError(f"Expected TestSuite, got {other.__name__}")

        other_ids = {t.identifier for t in other.testcases}

        return TestSuite(
            list(
                filter(
                    lambda t: getattr(t, "identifier", True) in other_ids,
                    self.testcases,
                )
            )
        )

    def __contains__(self, other) -> bool:
        if isinstance(other, TestCase):
            # Should this be comparing quotedata or identifier?
            return any(other.data == t.data for t in self.testcases)
        if isinstance(other, dict):
            return any(other == t.data for t in self.testcases)
        return NotImplemented

    def _groupby(self, by=None) -> Dict[Any, List]:
        if isinstance(by, Iterable):
            _by = tuple(by)
        else:
            _by = by

        # TODO: Find out if this is worth replacing with
        # itertools.groupby
        _prelim: Dict[Any, List[Any]] = {}
        for t in self.testcases:
            key = t[_by]
            if key not in _prelim:
                _prelim[key] = []
            _prelim[key].append(t)

        return _prelim

    def mix(self, by=None, percent=False, sorted=True, **kwargs):
        """Mix

        Returns the mix for a given factor in a set of test cases.
        """
        grouped = self._groupby(by=by)
        print(grouped)
        if percent:
            mix = {
                k: percentage(len(v), len(self), **kwargs)
                for k, v in grouped.items()
            }
        else:
            mix = {k: len(v) for k, v in grouped.items()}

        if sorted:
            keys = list(mix.keys())
            keys.sort()
            return {key: mix[key] for key in keys}

        return mix

    def difference_in_mix(self, other, by=None, percent=False):
        """Difference In Mix

        Returns a dict that is the difference between two supplied
        dicts.
        """
        if not isinstance(other, TestSuite):
            raise NotImplementedError(
                "Difference only implemented for QuoteSet"
            )
        return dict_difference(
            self.mix(by=by, percent=percent),
            other.mix(by=by, percent=percent),
        )

    def factors(self, keys=None, sort_keys=True):
        factor_dict = {}
        for testcase in self:
            for key, value in testcase.quotedata.items():
                if key not in factor_dict:
                    factor_dict[key] = set()
                factor_dict[key].add(value)
        return factor_dict

    def subset(self, by):

        if callable(by):
            return TestSuite(filter(by, self))
