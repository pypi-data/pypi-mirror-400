"""."""

from kinematic_tracker.core.loose_items import get_loose_indices


def test_get_loose_values() -> None:
    """."""
    assert {0, 2, 3} == get_loose_indices([1, 4], 5)


def test_empty_correspondence() -> None:
    """."""
    assert get_loose_indices([], 8) == {0, 1, 2, 3, 4, 5, 6, 7}


def test_nothing_lost() -> None:
    """."""
    assert get_loose_indices([0, 1], 2) == set()
