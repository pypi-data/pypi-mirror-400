"""."""

import numpy as np
import pytest

from kinematic_tracker.association.metric_giou_aligned import DT, FT, MetricGIoUAligned


def test_normal(det_rz: DT, filters: FT, driver: MetricGIoUAligned) -> None:
    """."""
    metric = driver.compute_metric(det_rz, filters)
    ref = [
        [1.0, 0.6318122555410691],
        [0.6318122555410691, 1.0],
        [0.4686147186147186, 0.6735666418466121],
    ]
    assert metric == pytest.approx(np.array(ref).T)
    assert np.shares_memory(metric, driver.metric_rt)
