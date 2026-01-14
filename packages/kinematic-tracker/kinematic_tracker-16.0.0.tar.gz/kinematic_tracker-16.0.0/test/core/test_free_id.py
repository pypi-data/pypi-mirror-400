"""."""

from kinematic_tracker.core.free_id import get_free_id


def test_get_free_id() -> None:
    """."""
    assert get_free_id([-1, -1]) == 0
    assert get_free_id([-1, 1]) == 0
    assert get_free_id([-1, 0]) == 1
    assert get_free_id([1, 2]) == 0
    assert get_free_id([0, 1]) == 2
