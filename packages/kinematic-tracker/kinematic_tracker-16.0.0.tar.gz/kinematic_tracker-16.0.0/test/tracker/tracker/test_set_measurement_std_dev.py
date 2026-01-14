"""."""

import numpy as np
import pytest

from kinematic_tracker.tracker.tracker import NdKkfTracker


@pytest.fixture
def tracker() -> NdKkfTracker:
    return NdKkfTracker([3, 1], [2, 2], [2, 1])


def test_set_measurement_std_dev_at_start_part0_der_order0(tracker: NdKkfTracker) -> None:
    assert tracker.cov_zz is None
    tracker.set_measurement_std_dev(0, 0.5, 0)
    assert isinstance(tracker.cov_zz, np.ndarray)
    assert tracker.cov_zz.shape == (6, 6)
    for i in (1, 3, 4, 5):
        assert np.isnan(tracker.cov_zz[i, i])
        tracker.cov_zz[i, i] = (i + 1) * 10

    ref_zz = [
        [0.25, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 20.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.25, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 40.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 50.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 60.0],
    ]
    assert tracker.cov_zz == pytest.approx(np.array(ref_zz))


def test_set_measurement_std_dev_at_start_part0_der_order1(tracker: NdKkfTracker) -> None:
    tracker.set_measurement_std_dev(0, 0.5, 1)
    assert isinstance(tracker.cov_zz, np.ndarray)
    for i in (0, 2, 4, 5):
        assert np.isnan(tracker.cov_zz[i, i])
        tracker.cov_zz[i, i] = (i + 1) * 10

    ref_zz = [
        [10.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.25, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 30.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.25, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 50.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 60.0],
    ]
    assert tracker.cov_zz == pytest.approx(np.array(ref_zz))


def test_set_measurement_std_dev_at_start_part1_der_order0(tracker: NdKkfTracker) -> None:
    tracker.set_measurement_std_dev(1, 0.5, 0)
    assert isinstance(tracker.cov_zz, np.ndarray)
    for i in (0, 1, 2, 3):
        assert np.isnan(tracker.cov_zz[i, i])
        tracker.cov_zz[i, i] = (i + 1) * 10

    ref_zz = [
        [10.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 20.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 30.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 40.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.25, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.25],
    ]
    assert tracker.cov_zz == pytest.approx(np.array(ref_zz))


def test_set_measurement_std_dev_at_start_part1_der_order1(tracker: NdKkfTracker) -> None:
    with pytest.raises(ValueError):
        tracker.set_measurement_std_dev(1, 0.5, 1)


def test_set_measurement_std_dev_on_the_go(tracker: NdKkfTracker) -> None:
    tracker.cov_zz = -999 * np.ones((6, 6))
    tracker.set_measurement_std_dev(1, 0.5, 0)
    ref_zz = [
        [-999.0, -999.0, -999.0, -999.0, -999.0, -999.0],
        [-999.0, -999.0, -999.0, -999.0, -999.0, -999.0],
        [-999.0, -999.0, -999.0, -999.0, -999.0, -999.0],
        [-999.0, -999.0, -999.0, -999.0, -999.0, -999.0],
        [-999.0, -999.0, -999.0, -999.0, 0.25, -999.0],
        [-999.0, -999.0, -999.0, -999.0, -999.0, 0.25],
    ]
    assert tracker.cov_zz == pytest.approx(np.array(ref_zz))
