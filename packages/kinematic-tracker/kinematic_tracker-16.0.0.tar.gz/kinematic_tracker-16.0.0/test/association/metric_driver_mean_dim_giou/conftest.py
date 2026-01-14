"""."""

import pytest

from kinematic_tracker.association.metric_mean_dim_giou import MetricMeanDimGIoU


@pytest.fixture
def driver() -> MetricMeanDimGIoU:
    return MetricMeanDimGIoU(100, 500, 6, (0, 1, 2, -3, -2, -1))
