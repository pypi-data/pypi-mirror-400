"""Test Case

So some quick testing revealed that the quote object needs to be separated.

It needs to be split into two classes, one dedicated to holding the data needed
to create the quote, the other to hold the calculations/history.

"""

from typing import Dict, Union, List
import uuid


class TestCase:
    """Test Case

    This is a test case, or as many would think an
    individual quote.
    """

    def __init__(self, data: Dict, name: Union[str, None] = None):
        self.data: Dict = data
        self.quotes: List = []
        self.identifier: Union[str, uuid.UUID] = name or uuid.uuid4()

    def __getitem__(self, key):
        if self.data is None:
            raise ValueError(
                "Quote has not been run against a framework/testcase yet."
            )

        return self.data[key]

    def __contains__(self, other) -> bool:
        return other in self.data

    def quote(self, framework, *args, **kwargs):
        if not isinstance(framework, type):
            raise ValueError(
                "Framework Instance received, expected definition."
            )
        quote = framework.quote(self, *args, **kwargs)
        self.quotes.append(quote)
        return quote
