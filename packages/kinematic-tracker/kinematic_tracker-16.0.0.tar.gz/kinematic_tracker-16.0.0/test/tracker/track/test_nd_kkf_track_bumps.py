"""."""

import pytest

from kinematic_tracker.tracker.track import NdKkfTrack


def test_nd_kkf_track_bump_num_detections(track: NdKkfTrack) -> None:
    """."""
    track.num_miss = 3
    track.bump_num_detections(0.5, 77)
    assert track.score == pytest.approx(0.5)
    assert track.num_det == 1
    assert track.num_miss == 0
    assert track.upd_id == 77


def test_nd_kkf_track_bump_num_misses(track: NdKkfTrack) -> None:
    """."""
    track.num_det = 3
    track.bump_num_misses()
    assert track.score == pytest.approx(0.0)
    assert track.num_det == 0
    assert track.num_miss == 1
    assert track.upd_id == -9999
