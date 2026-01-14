"""."""

import numpy as np
import pytest

from kinematic_tracker.association.metric_giou_aligned import DT, MetricGIoUAligned


def test_comp_report_aux_normal(det_rz: DT, driver: MetricGIoUAligned) -> None:
    driver.comp_report_aux(det_rz)
    ref0 = [[-1.0, -0.5, 0.0], [3.0, 4.5, 6.0]]
    assert driver.aux_r[0].corners == pytest.approx(np.array(ref0))
    ref1 = [[-0.5, 0.0, 0.5], [4.5, 6.0, 7.5]]
    assert driver.aux_r[1].corners == pytest.approx(np.array(ref1))
    assert driver.aux_r[2].corners == pytest.approx(0.0)
