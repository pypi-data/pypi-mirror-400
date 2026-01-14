class Note:
    """
    Note

    Used to store text in Quote Breakdowns.
    """

    def __init__(self, note: str):
        self.text: str = note

    def __repr__(self):
        return f"{'': <7} :: {self.text:<60}."
