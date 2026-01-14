from typing import List, Union, Iterator, Any


class InitialStep:
    """The initial step of a breakdown."""

    def __init__(self):
        self.a = 0
        self.b = 0
        self.result = 0
        self.oper = lambda: None
        self.name = "ORIG"


class Breakdown:
    """Quote Breakdown.

    Records a detailed breakdown of the calculation steps leading to the final
    price.

    This object maintains a sequence of steps (and optional notes) that
    document the process used to compute a final quoted price. It provides
    methods for appending new steps, iterating over all steps, and
    summarizing the calculation process.

    Attributes:
        steps (List[Union[Step, Note]]): A list of steps and notes representing
            the calculation process.
    """

    def __init__(self, parent_quote_id) -> None:
        """Initialize a Breakdown instance.

        If a final price is provided, a pre-calculated quote step is added;
        otherwise, an initial "Start" step is added with a result of 0.

        Args:
            parent_quote_id (int): The parent quote id of the breakdown.
        """
        self.steps: List = []
        self.steps.append(InitialStep())
        self.parent_quote_id = parent_quote_id

    def __getitem__(self, index: Union[int, slice]) -> Any:
        """Retrieve one or more steps from the breakdown by index.

        Args: index (int or slice): The index (or slice of indices) of the
            step(s) to retrieve.

        Returns: Union[Step, Note, List[Union[Step, Note]]]: The step(s)
            corresponding to the given index.
        """
        return self.steps[index]

    def __len__(self) -> int:
        """Return the number of steps in the breakdown.

        Returns:
            int: The total number of recorded steps.
        """
        return len(self.steps)

    def __iter__(self) -> Iterator:
        """Return an iterator over the steps in the breakdown.

        Returns:
            Iterator[Union[Step, Note]]: An iterator over all recorded steps.
        """
        return iter(self.steps)

    def __reversed__(self) -> Iterator:
        """
        Return a reverse iterator over the steps in the breakdown.

        Returns: Iterator[Union[Step, Note]]: A reverse iterator over the
            recorded steps.
        """
        return reversed(self.steps)

    def __repr__(self) -> str:
        """Return a string representation of the breakdown.

        Returns:
            str: A summary of all steps in the breakdown.
        """
        return "Breakdown({})".format(self.parent_quote_id)

    def __bool__(self) -> bool:
        """Determine the truth value of the Breakdown.

        Returns:
            bool: True if at least one step is recorded; False otherwise.
        """
        return bool(self.steps)

    def summary(self) -> str:
        """Generate a summary of the breakdown steps.

        Returns: str: A newline-separated string representation of each
            recorded step.
        """
        steps = list(self)
        return "\n".join(repr(step) for step in steps)

    def append(self, step) -> None:
        """Append a new step to the breakdown.

        Args:
            step: The new step to add to the breakdown.
        """
        self.steps.append(step)

    @property
    def final_price(self) -> float:
        """Retrieve the final calculated price from the breakdown.

        The final price is determined by iterating over the recorded steps in
        reverse order and returning the result of the first step that is not a
        note.

        Returns:
            float: The final calculated price.

        Raises:
            ValueError: If no calculation step is present in the breakdown.
        """
        for step in reversed(self):
            # Skip any steps that are purely notes.
            if hasattr(step, "result"):
                return step.result
        raise ValueError("No calculations present in quote.")
