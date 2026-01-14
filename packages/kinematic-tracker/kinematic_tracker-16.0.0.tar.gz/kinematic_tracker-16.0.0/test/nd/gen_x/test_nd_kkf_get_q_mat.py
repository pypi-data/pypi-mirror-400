"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.nd.precursors import NdKkfPrecursors


def test_get_q_mat_compatible_factors(pre: NdKkfPrecursors, gen_x: NdKkfMatGenX) -> None:
    """."""
    pre.compute(3.0)
    cov = 1.3 * np.ones((8, 8))
    factors = np.linspace(1.0, 5.0, num=5)
    gen_x.fill_q_mat(pre, factors, cov)
    ref = [
        [9.0, 4.5, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3],
        [4.5, 3.0, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3],
        [1.3, 1.3, 18.0, 9.0, 1.3, 1.3, 1.3, 1.3],
        [1.3, 1.3, 9.0, 6.0, 1.3, 1.3, 1.3, 1.3],
        [1.3, 1.3, 1.3, 1.3, 27.0, 13.5, 1.3, 1.3],
        [1.3, 1.3, 1.3, 1.3, 13.5, 9.0, 1.3, 1.3],
        [1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 12.0, 1.3],
        [1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 1.3, 15.0],
    ]
    assert cov == pytest.approx(np.array(ref))


def test_get_q_mat_incompatible_precursors(gen_x: NdKkfMatGenX) -> None:
    """."""
    cov = np.empty((8, 8))
    factors = np.linspace(1.0, 5.0, num=5)
    with pytest.raises(AssertionError):
        gen_x.fill_q_mat(NdKkfPrecursors([3, 1]), factors, cov)


def test_get_q_mat_incompatible_factors(pre: NdKkfPrecursors, gen_x: NdKkfMatGenX) -> None:
    """."""
    cov = np.empty((8, 8))
    factors = np.linspace(1.0, 5.0, num=4)
    with pytest.raises(AssertionError):
        gen_x.fill_q_mat(pre, factors, cov)
