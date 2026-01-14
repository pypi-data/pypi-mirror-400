"""."""

from pathlib import Path

import numpy as np
import pytest

from kinematic_tracker.nd.derivative_sorted import DerivativeSorted
from kinematic_tracker.tracker.tracker import NdKkfTracker


def assert_quality(tracker: NdKkfTracker, ate_max: float) -> None:
    """."""
    det_path = Path(__file__).parent / 'share/fusion-lab-detections-sensor-1.csv'
    tss_s = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=(0,), dtype=int)
    det_ids = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=(1,), dtype=int)
    det_sz = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=range(2, 8))
    tracking_history = []
    for stamp, det_id, det_z in zip(tss_s, det_ids, det_sz):
        tracker.advance(int(stamp), [det_z], [det_id])
        assert len(tracker.tracks) == 1
        tracking_history.append(tracker.tracks[0].kkf.kalman_filter.statePost.reshape(12).copy())

    der_sorted = DerivativeSorted(tracker.gen_xz.gen_x)
    state_sx = np.zeros((30, 12))
    der_sorted.convert_vectors(tracking_history, state_sx)

    motion_path = det_path.parent / 'fusion-lab-motion-sensor-1.csv'
    ref_sx = np.genfromtxt(motion_path, skip_header=1, delimiter=',', usecols=range(2, 14))
    ate = np.mean(np.linalg.norm(state_sx[:, :3] - ref_sx[:, :3], axis=1))
    assert ate < ate_max


@pytest.fixture
def tracker() -> NdKkfTracker:
    """."""
    tracker = NdKkfTracker([3, 1], [3, 3])
    tracker.set_measurement_std_dev(0, 0.5)
    tracker.set_measurement_std_dev(1, 0.02)
    return tracker
