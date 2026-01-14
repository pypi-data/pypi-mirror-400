"""."""

import numpy as np
import pytest

from kinematic_tracker.association.metric_driver_base import FT, MetricDriverBase


def test_compute(driver: MetricDriverBase, filters: FT) -> None:
    driver = MetricDriverBase(4, 5, 6)
    vxx_z = [vec_z.copy() for vec_z in driver.gen_vec_z(filters)]
    assert len(vxx_z) == 3
    assert vxx_z[0] == pytest.approx([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    assert vxx_z[1] == pytest.approx([2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
    assert vxx_z[2] == pytest.approx([3.0, 4.0, 5.0, 6.0, 7.0, 8.0])


def test_share_buffer(driver: MetricDriverBase, filters: FT) -> None:
    ls = list(driver.gen_vec_z(filters))
    assert len(ls) == 3
    assert np.shares_memory(ls[0], driver.vec_z)
    assert np.shares_memory(ls[1], driver.vec_z)
    assert np.shares_memory(ls[2], driver.vec_z)
