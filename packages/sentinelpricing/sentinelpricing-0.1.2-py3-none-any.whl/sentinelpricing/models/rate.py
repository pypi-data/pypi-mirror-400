"""Rate"""


# TODO: What if step was initialized here?
class Rate:
    """Rate

    This is the lowest Sentinel object, in that its role is to record where the
    value used in a calculation came from.

    The name will be set by the rating factor/lookup table, and the value saved
    accordingly.

    """

    name: str
    value: int | float

    def __init__(self, name: str, value: int | float):
        self.name = name
        self.value = value

    def __add__(self, other):
        if isinstance(other, Rate):
            return self.value + other.value
        return self.value + other

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, Rate):
            return self.value - other.value
        return self.value - other

    def __mul__(self, other):
        if isinstance(other, Rate):
            return self.value * other.value
        return self.value * other

    def __truediv__(self, other):
        if isinstance(other, Rate):
            return self.value / other.value
        return self.value / other

    def __floordiv__(self, other):
        if isinstance(other, Rate):
            return self.value // other.value
        return self.value // other

    def __eq__(self, other):
        if isinstance(other, Rate):
            return self.value == other.value
        return self.value == other

    def __lt__(self, other):
        if isinstance(other, Rate):
            return self.value < other.value
        else:
            return self.value < other

    def __gt__(self, other):
        return not self < other

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other
