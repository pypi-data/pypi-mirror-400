"""."""

import numpy as np
import pytest

from kinematic_tracker.association.match_driver_base import MatchDriverBase


def test_match_driver_base_init() -> None:
    """."""
    driver = MatchDriverBase(4, 5)
    assert driver.targets.shape == (4,)
    assert driver.reports.shape == (4,)


def test_match_driver_base_check_shape() -> None:
    """."""
    driver = MatchDriverBase(4, 5)
    driver.check_max_shape((2, 3))
    with pytest.raises(ValueError):
        driver.check_max_shape((5, 3))

    with pytest.raises(ValueError):
        driver.check_max_shape((2, 6))


def test_get_reports_targets_no_matches() -> None:
    """."""
    driver = MatchDriverBase(4, 5)
    reports, targets = driver.get_reports_targets()
    assert isinstance(reports, np.ndarray)
    assert isinstance(targets, np.ndarray)
    assert reports.ndim == 1
    assert targets.ndim == 1
    assert reports.size == 0
    assert targets.size == 0
