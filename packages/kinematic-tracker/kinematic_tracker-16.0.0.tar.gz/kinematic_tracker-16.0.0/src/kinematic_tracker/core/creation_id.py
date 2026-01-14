"""."""


class CreationId:
    """."""

    def __init__(self) -> None:
        """."""
        self.next_id: int = -1

    def get_next_id(self) -> int:
        """."""
        self.next_id += 1
        return self.next_id
