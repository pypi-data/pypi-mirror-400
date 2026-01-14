"""."""

from kinematic_tracker.core.track_free_id import get_free_id


class MockTrack:
    def __init__(self, self_id: int) -> None:
        """."""
        self.id = self_id


def test_get_free_id() -> None:
    """."""
    tracks = [MockTrack(0), MockTrack(1)]
    tracks[0].id = 0
    tracks[1].id = 1
    assert get_free_id(tracks) == 2
