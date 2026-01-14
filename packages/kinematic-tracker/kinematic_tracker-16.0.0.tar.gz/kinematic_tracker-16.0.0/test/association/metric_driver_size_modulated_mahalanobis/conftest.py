"""."""

import pytest

from kinematic_tracker.association.metric_size_modulated_mahalanobis import (
    MetricSizeModulatedMahalanobis,
)


@pytest.fixture
def driver() -> MetricSizeModulatedMahalanobis:
    return MetricSizeModulatedMahalanobis(100, 500, 1.23, 12, 6, (0, 1, 2, -3, -2, -1))
