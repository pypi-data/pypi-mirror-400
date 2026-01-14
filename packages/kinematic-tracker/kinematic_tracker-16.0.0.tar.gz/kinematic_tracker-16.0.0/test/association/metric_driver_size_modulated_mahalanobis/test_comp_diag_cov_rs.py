"""."""

import numpy as np
import pytest

from kinematic_tracker.association.metric_size_modulated_mahalanobis import (
    DT,
    MetricSizeModulatedMahalanobis,
)


def test_normal(det_rz: DT, driver: MetricSizeModulatedMahalanobis) -> None:
    driver.comp_sizes_dia_cov_rs(det_rz)
    ref = [[4.0, 6.25, 9.0], [6.25, 9.0, 12.25]]
    assert driver.sizes_dia_cov_rs[:2] == pytest.approx(np.array(ref))
    assert driver.sizes_dia_cov_rs[2:] == pytest.approx(0.0)


def test_empty_det(driver: MetricSizeModulatedMahalanobis) -> None:
    driver.comp_sizes_dia_cov_rs([])
    assert driver.sizes_dia_cov_rs == pytest.approx(0.0)
