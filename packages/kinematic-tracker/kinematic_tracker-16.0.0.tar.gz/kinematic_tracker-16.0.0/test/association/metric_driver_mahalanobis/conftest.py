"""."""

import pytest

from kinematic_tracker.association.metric_mahalanobis import MetricMahalanobis


@pytest.fixture
def driver() -> MetricMahalanobis:
    return MetricMahalanobis(100, 500, 1.0, 12, 6)
