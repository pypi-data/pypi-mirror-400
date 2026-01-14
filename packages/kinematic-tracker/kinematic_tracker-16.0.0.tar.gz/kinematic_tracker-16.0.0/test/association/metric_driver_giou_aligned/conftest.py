"""."""

import pytest

from kinematic_tracker.association.metric_giou_aligned import MetricGIoUAligned


@pytest.fixture
def driver() -> MetricGIoUAligned:
    return MetricGIoUAligned(100, 500, 6, (0, 1, 2, 3, 4, 5))
