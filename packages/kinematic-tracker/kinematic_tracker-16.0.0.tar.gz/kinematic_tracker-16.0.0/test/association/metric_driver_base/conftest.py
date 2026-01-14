"""."""

import pytest

from kinematic_tracker.association.metric_driver_base import MetricDriverBase


@pytest.fixture
def driver() -> MetricDriverBase:
    return MetricDriverBase(4, 5, 6)
