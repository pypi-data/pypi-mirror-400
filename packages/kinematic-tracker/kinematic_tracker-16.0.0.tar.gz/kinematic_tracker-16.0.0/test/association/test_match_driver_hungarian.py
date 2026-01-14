"""."""

import numpy as np
import pytest

from kinematic_tracker.association.match_hungarian import MatchDriverHungarian


@pytest.fixture
def driver() -> MatchDriverHungarian:
    driver = MatchDriverHungarian(4, 5)
    driver.num_matches = 4
    driver.reports[:] = 9
    driver.targets[:] = 9
    return driver


def test_high_threshold(
    metric_23: np.ndarray[tuple[2, 3], np.dtype[float]], driver: MatchDriverHungarian
) -> None:
    """."""
    driver.compute_matches(metric_23, 5.5)
    assert driver.num_matches == 1
    assert driver.reports == pytest.approx([1, 9, 9, 9])
    assert driver.targets == pytest.approx([2, 9, 9, 9])


def test_low_threshold(
    metric_23: np.ndarray[tuple[2, 3], np.dtype[float]], driver: MatchDriverHungarian
) -> None:
    """."""
    driver.compute_matches(metric_23, 0.5)
    assert driver.num_matches == 2
    assert driver.reports == pytest.approx([0, 1, 9, 9])
    assert driver.targets == pytest.approx([2, 1, 9, 9])


def test_all_zeros(driver: MatchDriverHungarian) -> None:
    """."""
    driver.compute_matches(np.zeros((2, 3)), 0.5)
    assert driver.num_matches == 0
    assert driver.reports == pytest.approx([9, 9, 9, 9])
    assert driver.targets == pytest.approx([9, 9, 9, 9])
