"""."""

from kinematic_tracker.tracker.track import NdKkfTrack


def test_nd_kkf_track_init(track: NdKkfTrack) -> None:
    """."""
    assert track.creation_id == -1
    assert track.ann_id == 123
    assert track.upd_id == 123
    assert track.id == -1


def test_nd_kkf_track_repr(track: NdKkfTrack) -> None:
    """."""
    assert repr(track) == 'TrackNdKkf(x = [1. 0. 2. 0. 3. 0. 4. 5.])'
