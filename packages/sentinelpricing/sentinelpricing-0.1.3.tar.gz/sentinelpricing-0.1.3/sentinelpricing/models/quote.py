"""Quote"""

import uuid
from collections import Counter
from statistics import mean
from operator import add, sub, mul, truediv
from typing import (
    Any,
    Callable,
    Dict,
    Hashable,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Union,
    Tuple,
)

from sentinelpricing.models.breakdown import Breakdown
from sentinelpricing.models.testcase import TestCase
from sentinelpricing.models.transformation import Transformation
from sentinelpricing.models.note import Note
from sentinelpricing.models.override import Override
from sentinelpricing.utils.calculations import percentage, dict_difference


class Quote:
    """
    Represents a quote containing test case data and a detailed calculation
    breakdown.

    This object encapsulates the input data used for calculating a quote,
    along with a breakdown of the calculation steps taken to achieve the
    final price for the quote. It supports arithmetic operations that update
    the breakdown and allows retrieval of test case or pricing data via
    subscript notation.

    Attributes:
        id (uuid.UUID): Unique id for the quote.
        framework: Optional framework instance associated with the quote.
        quotedata (Mapping[str, Any]): Test case data used for quote
            calculation.
        breakdown (Breakdown): A breakdown of calculation steps leading to the
            final price.
    """

    def __init__(
        self,
        testcase: Mapping,
    ) -> None:
        """
        Initialize a new Quote instance.

        Args:
            testcase (Mapping or TestCase): The test case data or a TestCase
                instance. If a TestCase is provided, its `quotedata` attribute
                will be used.
        """

        if isinstance(testcase, TestCase):
            self.quotedata = testcase.data
        elif isinstance(testcase, dict):
            self.quotedata = testcase
        else:
            raise TypeError(
                "testcase must be a Mapping or a TestCase instance."
            )

        self.id = uuid.uuid4()

        self.breakdown = Breakdown(self.id)

    def __repr__(self) -> str:
        """
        Return a string representation of the Quote, including its id
        and breakdown.

        Returns:
            str: A string representation of the quote.
        """
        return "{}({})".format(self.__class__.__name__, self.id)

    def __getitem__(self, key: Hashable) -> Any:
        """
        Retrieve a value from the quote's data.

        Args:
            key (hashable): The key to look up.

        Returns:
            Any: The value associated with the key.
        """
        if key in self.quotedata:
            return self.quotedata[key]
        raise KeyError(f"Key '{key}' not found in quote data.")

    def __add__(self, other: Any) -> "Quote":
        """
        Add a value or merge with another Quote.

        If the other operand is a Quote, this operation is interpreted as a
        merge (currently a no-op, returning self). Otherwise, it applies an
        addition operation to the current final price in the breakdown.

        Args:
            other (Any): The value or Quote to add.

        Returns:
            Quote: The modified Quote instance.
        """
        if isinstance(other, Quote):
            # Optionally implement merging logic.
            return self
        return self._operation(other, add)

    def __radd__(self, other: Any) -> "Quote":
        """
        Reflective addition for Quote.

        Args:
            other (Any): The value to add.

        Returns:
            Quote: The modified Quote instance.
        """
        if isinstance(other, Quote):
            return self
        return self._operation(other, add)

    def __sub__(self, other: Any) -> "Quote":
        """
        Subtract a value from the quote's final price.

        Args:
            other (Any): The value to subtract.

        Returns:
            Quote: The modified Quote instance.
        """
        return self._operation(other, sub)

    def __rsub__(self, other: Any) -> "Quote":
        """
        Reflective subtraction for Quote.

        Args:
            other (Any): The value from which the quote's final price is
                subtracted.

        Returns:
            Quote: The modified Quote instance.
        """
        return self._operation(other, sub)

    def __mul__(self, other: Any) -> "Quote":
        """
        Multiply the quote's final price by a value.

        Args:
            other (Any): The value to multiply by.

        Returns:
            Quote: The modified Quote instance.
        """
        return self._operation(other, mul)

    def __rmul__(self, other: Any) -> "Quote":
        """
        Reflective multiplication for Quote.

        Args:
            other (Any): The value to multiply by.

        Returns:
            Quote: The modified Quote instance.
        """
        return self._operation(other, mul)

    def __truediv__(self, other: Any) -> "Quote":
        """
        Divide the quote's final price by a value.

        Args:
            other (Any): The divisor.

        Returns:
            Quote: The modified Quote instance.
        """
        return self._operation(other, truediv)

    def __rtruediv__(self, other: Any) -> "Quote":
        """
        Reflective division for Quote.

        Args:
            other (Any): The dividend.

        Returns:
            Quote: The modified Quote instance.
        """
        return self._operation(other, truediv)

    def __eq__(self, other: Any) -> bool:
        """
        Compare the Quote with another Quote or a numeric value.

        If comparing with another Quote, the quotedata is compared.
        If comparing with an int or float, the final price is compared.

        Args:
            other (Any): The object to compare against.

        Returns:
            bool: True if the quotes are considered equal; otherwise, False.

        Raises:
            NotImplementedError: If comparison with the given type is not
                supported.
        """
        if isinstance(other, Quote):
            return self.breakdown.final_price == other.breakdown.final_price
        if isinstance(other, (int, float)):
            return self.breakdown.final_price == other
        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        """
        Compare the Quote with another Quote or a numeric value.

        If comparing with another Quote, the final price of each is compared.
        If comparing with an int or float, the final price and int or float are
            compared.

        Args:
            other (Any): The object to compare against.

        Returns:
            bool: True if the quote is less than other; otherwise, False.

        Raises:
            NotImplementedError: If comparison with the given type is not
                supported.
        """
        if isinstance(other, Quote):
            return self.breakdown.final_price < other.breakdown.final_price
        if isinstance(other, (int, float)):
            return self.breakdown.final_price < other
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        """
        Compare the Quote with another Quote or a numeric value.

        If comparing with another Quote, the final price of each is compared.
        If comparing with an int or float, the final price and int or float are
            compared.

        Args:
            other (Any): The object to compare against.

        Returns:
            bool: True if the quote is greater than other; otherwise, False.

        Raises:
            NotImplementedError: If comparison with the given type is not
                supported.
        """
        return not self < other and not self == other

    def __le__(self, other) -> bool:
        """
        Compare the Quote with another Quote or a numeric value.

        If comparing with another Quote, the final price of each is compared.
        If comparing with an int or float, the final price and int or float are
            compared.

        Args:
            other (Any): The object to compare against.

        Returns:
            bool: True if the quote is less than or equal to other; otherwise,
                False.

        Raises:
            NotImplementedError: If comparison with the given type is not
                supported.
        """
        return self < other or self == other

    def __ge__(self, other):
        """
        Compare the Quote with another Quote or a numeric value.

        If comparing with another Quote, the final price of each is compared.
        If comparing with an int or float, the final price and int or float are
            compared.

        Args:
            other (Any): The object to compare against.

        Returns:
            bool: True if the quote is greater than or equal to other;
                otherwise, False.

        Raises:
            NotImplementedError: If comparison with the given type is not
                supported.
        """
        return not self <= other

    def __contains__(self, key):
        return key in self.quotedata

    def _operation(
        self, other: Any, oper: Callable[[Any, Any], Any]
    ) -> "Quote":
        """
        Apply an arithmetic operation to the quote's final price.

        This internal helper performs an operation (such as addition,
        subtraction, multiplication, or division) using the current final price
        and the provided value. It then records the operation as a Step in the
        breakdown.

        Args:
            other (Any): The value or Rate instance to operate with.
            oper (Callable[[Any, Any], Any]): The operator function
                (e.g., add, sub).

        Returns:
            Quote: The modified Quote instance.
        """
        t = Transformation(oper, self.final_price, other)
        self.breakdown.append(t)
        return self

    def override(self, value):
        overriding_step = Override(value)
        self.breakdown.append(overriding_step)

    def note(self, text: str) -> None:
        """
        Append a note to the quote's breakdown.

        Args:
            text (str): The note text to be recorded.
        """
        self.breakdown.append(Note(text))

    def get(self, *args, **kwargs):
        return self.quotedata.get(*args, **kwargs)

    @property
    def calculated(self) -> bool:
        """
        Check if the quote has been calculated.

        Returns:
            bool: True if a final price is available; otherwise, False.
        """
        return bool(self.breakdown.final_price)

    @property
    def final_price(self) -> float:
        """
        Retrieve the final calculated price from the quote.

        Returns:
            float: The final price as determined by the breakdown.
        """
        return self.breakdown.final_price

    def summary(self):
        """Outputs Quote Breakdown.

        Returns the quote breakdown as a string.

        Returns:
            str: Quote Breakdown.
        """
        return repr(self) + "\n" + repr(self.breakdown)


class PreCalculatedQuote(Quote):
    def __init__(self, breakdown, testcase, quoteid=None):
        self.breakdown = Breakdown.from_iterable(breakdown)

        if quoteid is not None:
            self.id = quoteid

        super().__init__(testcase)


class QuoteSet:
    """
    A collection of Quote objects.

    A QuoteSet is generated after running either a TestSuite or TestCase
    through a Framework. It supports aggregation, statistical operations, and
    grouping of quotes.
    """

    def __init__(
        self, quotes: Iterable["Quote"], framework: Optional[Any] = None
    ) -> None:
        """
        Initialize a QuoteSet instance.

        Args:
            quotes (Iterable[Quote]): An iterable of Quote objects.
            framework: Optional framework associated with these quotes.
        """
        self.quotes: List["Quote"] = list(quotes)
        self.uniqueid_check()

    def __iter__(self) -> Iterator["Quote"]:
        """
        Return an iterator over the Quote objects in the list.

        Returns:
            Iterator[Quote]: An iterator over the quotes.
        """
        return iter(self.quotes)

    def __getitem__(self, index) -> Quote:
        """
        Get item from the Quote objects in the quotes list.

        Returns:
            Quote: An instance of a Quote.
        """
        return self.quotes[index]

    def __len__(self) -> int:
        """
        Return the number of Quote objects in the set.

        Returns:
            int: The count of quotes.
        """
        return len(self.quotes)

    def __add__(self, other: "QuoteSet") -> "QuoteSet":
        """
        Combine two QuoteSets.

        Args:
            other (QuoteSet): Another QuoteSet to add.

        Returns:
            QuoteSet: A new QuoteSet containing quotes from both sets.
        """
        return QuoteSet(self.quotes + other.quotes)

    def __sub__(self, other: "QuoteSet") -> "QuoteSet":
        """
        Subtract One QuoteSet From the Other QuoteSet.

        Args:
            other (QuoteSet): Another QuoteSet to subtract.

        Returns:
            QuoteSet: A new QuoteSet containing quotes from both sets.
        """

        other_ids = {q.id for q in other.quotes}

        return QuoteSet(list(filter(lambda q: q.id in other_ids, self.quotes)))

    def __contains__(self, other):
        if isinstance(other, Quote):
            # Should this be comparing quotedata or id?
            return any(other.quotedata == q.quotedata for q in self)
        if isinstance(other, dict):
            return any(other == q.quotedata for q in self)
        return NotImplemented

    def _groupby(
        self,
        quotes: Union[None, List[Quote]] = None,
        by: Optional[Union[Any, Callable[[Quote], Any]]] = None,
    ) -> Dict[Any, List["Quote"]]:
        """
        Group quotes by a specified key or set of keys.

        Args:
            by (Any or Iterable[Any], optional): The key(s) used for grouping.
                If an iterable is provided (and not a string/bytes), the keys
                are combined into a tuple.

        Returns:
            Dict[Any, List[Quote]]: A mapping from group key to list of Quote
                objects.
        """

        groups: Dict[Any, List["Quote"]] = {}
        iterable = quotes or self.quotes

        _by: Union[Tuple[Any, ...], Callable, str]
        if callable(by):
            _by = by
        else:
            if isinstance(by, Iterable) and not isinstance(by, str):

                def _by(x):
                    return x[tuple(by)]

            else:

                def _by(x):
                    return x[by]

        for q in iterable:
            key: Any = _by(q)
            groups.setdefault(key, []).append(q)
        return groups

    def _statistic_function(
        self,
        func: Callable[[Iterable[Any]], Any],
        by: Optional[Union[Any, Iterable[Any]]] = None,
        on: Optional[str] = None,
        where: Optional[Callable[["Quote"], bool]] = None,
        sort_keys: bool = True,
    ) -> Union[Dict[Any, Any], Any]:
        """
        Apply an aggregation function to the quotes or to groups of quotes.

        Args:
            func (Callable): A function that aggregates a list of numeric
                values (e.g., mean, max).
            by (Any or Iterable[Any], optional): Key(s) to group quotes before
                applying the function.
            bin (Callable): A function that groups the by field.
            on (str, optional): The attribute name to extract from each Quote
                (defaults to "final_price").
            where (Callable, optional): A function to filter quotes
                before aggregation.
            sort_keys (bool): Whether to sort the grouping keys in the result.

        Returns:
            Union[Dict[Any, Any], Any]:
                If no grouping is specified, returns the aggregated value for
                    all quotes.
                If grouping is specified, returns a dictionary mapping group
                    keys to aggregated values.
        """
        attribute: str = on or "final_price"

        filtered_quotes = (
            list(filter(where, self.quotes)) if where else self.quotes
        )

        if by is None:
            values = [getattr(q, attribute) for q in filtered_quotes]
            return func(values)

        grouped_data = self._groupby(quotes=filtered_quotes, by=by)
        prelim: Dict[Any, List[Any]] = {
            key: [getattr(q, attribute) for q in quotes]
            for key, quotes in grouped_data.items()
        }

        if sort_keys:
            prelim = {key: prelim[key] for key in sorted(prelim.keys())}

        return {key: func(values) for key, values in prelim.items()}

    def avg(self, *args, **kwargs) -> Union[Dict[Any, float], float]:
        """
        Compute the average of a specified attribute across quotes.

        Args:
            by (Any or Iterable[Any], optional): Key(s) or Callable to group
                quotes by.
            on (str, optional): The attribute name to extract from each Quote
                (defaults to "final_price").
            where (Callable, optional): A function to filter quotes
                before aggregation.
            sort_keys (bool): Whether to sort the grouping keys in the result.

        Returns:
            Union[Dict[Any, float], float]:
                - A single average value if no grouping is specified.
                - A dictionary mapping group keys to their average values if
                    grouping is used.
        """
        return self._statistic_function(mean, *args, **kwargs)

    def max(self, *args, **kwargs) -> Union[Dict[Any, float], float]:
        """
        Compute the maximum of a specified attribute across quotes.

        Args:
            by (Any or Iterable[Any],Key(s) or Callable to group
                quotes by.
            on (str, optional): The attribute name to extract from each Quote
                (defaults to "final_price").
            where (Callable, optional): A function to filter quotes
                before aggregation.
            sort_keys (bool): Whether to sort the grouping keys in the result.

        Returns:
            Union[Dict[Any, float], float]:
                - A single maximum value if no grouping is specified.
                - A dictionary mapping group keys to their maximum values if
                    grouping is used.
        """
        return self._statistic_function(max, *args, **kwargs)

    def min(self, *args, **kwargs) -> Union[Dict[Any, float], float]:
        """
        Compute the minimum of a specified attribute across quotes.

        Args:
            by (Any or Iterable[Any], optional): Key(s) or Callable to group
                quotes by.
            on (str, optional): The attribute name to extract from each Quote
                (defaults to "final_price").
            where (Callable, optional): A function to filter quotes
                before aggregation.
            sort_keys (bool): Whether to sort the grouping keys in the result.

        Returns:
            Union[Dict[Any, float], float]:
                - A single minimum value if no grouping is specified.
                - A dictionary mapping group keys to their minimum values if
                    grouping is used.
        """
        return self._statistic_function(min, *args, **kwargs)

    def sum(self, *args, **kwargs) -> Union[Dict[Any, float], float]:
        """
        Compute the sum of a specified attribute across quotes.

        Args:
            by (Any or Iterable[Any], optional): Key(s) or Callable to group
                quotes by.
            on (str, optional): The attribute name to extract from each Quote
                (defaults to "final_price").
            where (Callable, optional): A function to filter quotes
                before aggregation.
            sort_keys (bool): Whether to sort the grouping keys in the result.

        Returns:
            Union[Dict[Any, float], float]:
                - A single sum if no grouping is specified.
                - A dictionary mapping group keys to their sums if grouping is
                    used.
        """
        return self._statistic_function(sum, *args, **kwargs)

    def apply(
        self,
        func: Callable[[Iterable[Any]], Any],
        *args: Any,
        **kwargs: Any,
    ) -> Union[Dict[Any, Any], Any]:
        """
        Apply a custom aggregation function to the quotes.

        Args:
            func (Callable): A function that aggregates a list of values.
            *args: Additional positional arguments for the function.
            by (Any or Iterable[Any], optional): Key(s) or Callable to group
                quotes by.
            on (str, optional): The attribute name to extract from each Quote
                (defaults to "final_price").
            where (Callable, optional): A function to filter quotes
                before aggregation.
            sort_keys (bool): Whether to sort the grouping keys in the result.

        Returns:
            Union[Dict[Any, Any], Any]:
                - The aggregated value if no grouping is specified.
                - A dictionary mapping group keys to their aggregated values if
                    grouping is used.
        """
        return self._statistic_function(func, *args, **kwargs)

    def mix(
        self,
        by: Optional[Union[Any, Iterable[Any]]] = None,
        percent: bool = False,
        **kwargs: Any,
    ) -> Dict[Any, Union[int, float]]:
        """
        Get a mapping of factors present in the quotes along with their
        frequency.

        Args:
            by (Any or Iterable[Any], optional): Key(s) to group quotes.
            percent (bool): If True, returns the percentage representation of
                 each group.
            **kwargs: Additional keyword arguments to pass to the percentage
                function.

        Returns:
            Dict[Any, Union[int, float]]: A dictionary mapping each group key
                to its count or percentage.
        """
        grouped = self._groupby(by=by)
        if percent:
            return {
                k: percentage(len(v), len(self), **kwargs)
                for k, v in grouped.items()
            }
        return {k: len(v) for k, v in grouped.items()}

    def difference_in_mix(
        self,
        other: "QuoteSet",
        by: Optional[Union[Any, Iterable[Any]]] = None,
        percent: bool = False,
    ) -> Dict[Any, float]:
        """
        Calculate the difference in mix between this QuoteSet and another.

        Args:
            other (QuoteSet): Another QuoteSet to compare.
            by (Any or Iterable[Any], optional): Key(s) to group quotes before
                comparing.
            percent (bool): If True, computes differences in percentage terms.

        Returns:
            Dict[Any, float]: A dictionary mapping group keys to the difference
                in mix.

        Raises:
            NotImplementedError: If `other` is not a QuoteSet.
        """
        if not isinstance(other, QuoteSet):
            raise NotImplementedError(
                "Difference only implemented for QuoteSet"
            )
        return dict_difference(
            self.mix(by=by, percent=percent), other.mix(by=by, percent=percent)
        )

    def difference(
        self,
        other: "QuoteSet",
        func: Callable[[Iterable[Any]], Any],
        by: Optional[Union[Any, Iterable[Any]]] = None,
    ) -> Dict[Any, Any]:
        """
        Calculate the difference between aggregated values of this QuoteSet and
            another.

        Args:
            other (QuoteSet): Another QuoteSet to compare.
            func (Callable): An aggregation function to apply.
            by (Any or Iterable[Any], optional): Key(s) to group quotes before
                applying the function.

        Returns:
            Dict[Any, Any]: A dictionary mapping group keys to the difference
                in aggregated values.

        Raises:
            NotImplementedError: If `other` is not a QuoteSet.
        """
        if not isinstance(other, QuoteSet):
            raise NotImplementedError(
                "Difference only implemented for QuoteSet"
            )
        return dict_difference(
            self.apply(func, by=by), other.apply(func, by=by)
        )

    def factors(self, keys: Optional[Iterable[str]] = None) -> Dict[str, set]:
        """
        Retrieve unique sets of factors present in the quote data.

        Args:
            keys (Iterable[str], optional): Specific factor keys to include.
                If not provided, all keys from each quote's data are
                considered.

        Returns:
            Dict[str, set]: A dictionary mapping each factor to a set of its
                unique values.
        """
        factor_dict: Dict[str, set] = {}
        for quote in self:
            for key, value in quote.quotedata.items():
                if keys is not None and key not in keys:
                    continue
                factor_dict.setdefault(key, set()).add(value)
        return factor_dict

    def subset(
        self, by: Union[Callable[["Quote"], bool], Dict[Any, Any]]
    ) -> "QuoteSet":
        """
        Retrieve a subset of quotes based on filtering criteria.

        Args:
            by (Callable or Dict): If callable, it is used to filter quotes via
                filter(). If a dict is provided (deprecated), its keys refer to
                factors in the quote and its values specify the desired
                selection.

        Returns:
            QuoteSet: A new QuoteSet containing quotes that match the filtering
                criteria.

        Raises:
            NotImplementedError: If dict-based filtering is attempted.
        """
        if callable(by):
            return QuoteSet(filter(by, self))
        raise NotImplementedError(
            "Dict-based filtering is deprecated. Use a function instead."
        )

    def uniqueid_check(self) -> None:
        """
        Check for duplicate quote ids and warn if duplicates exist.

        Prints a warning message if any Quote in the set has a non-unique
            id.
        """
        ids = [q.id for q in self]
        id_counts = Counter(ids)
        if any(count > 1 for count in id_counts.values()):
            print("Warning, non-unique IDs")
