from sentinelpricing.models.rate import Rate


class Step:
    """Step

    Form part of a quote Breakdown. Represents an operation carried out on a
    quote.
    """

    def __init__(self, original, oper, other, name=None):

        if isinstance(other, Rate):
            self.name = other.name
        else:
            self.name = name or "CONST"

        self.original = original
        self.oper = oper
        self.other = other

        self.result = oper(original, other)

    @classmethod
    def headers(cls):
        return (
            f"{'Total':<8} - {"Name":<72}"
            + f" - {"Operation": <30} - {"Other"}"
        )

    def __repr__(self):
        return (
            f"{round(self.result, 5): <9} - {self.name:<72}"
            + f" - {repr(self.oper): <30} - {self.other}"
        )


class Override:
    """Override"""

    def __init__(self, original, other):
        self.name = "Override"
        self.other = other
        self.result = other
        self.original = original

    @classmethod
    def headers(cls):
        return (
            f"{'Total': <8} :: {"Name":<72}"
            + f" - {"Operation": <30} - {"Other"}"
        )

    def __repr__(self):
        return (
            f"{round(self.result, 5): <9} :: {self.name:<72}"
            + f" - {"OVERRIDE": <30} - {self.other}"
        )
