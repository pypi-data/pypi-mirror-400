"""."""

from kinematic_tracker.core.creation_id import CreationId


def test_creation_id() -> None:
    """."""
    driver = CreationId()
    assert driver.get_next_id() == 0
    assert driver.get_next_id() == 1
    assert driver.get_next_id() == 2
