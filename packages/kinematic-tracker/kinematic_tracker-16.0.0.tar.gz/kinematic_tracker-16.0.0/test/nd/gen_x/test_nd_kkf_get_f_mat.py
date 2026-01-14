"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.nd.precursors import NdKkfPrecursors


def test_get_f_mat(pre: NdKkfPrecursors, gen_x: NdKkfMatGenX) -> None:
    """."""
    pre.compute(3.0)
    f_mat = 9.0 * np.ones((8, 8))
    gen_x.fill_f_mat(pre, f_mat)
    ref = [
        [1.0, 3.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
        [0.0, 1.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
        [9.0, 9.0, 1.0, 3.0, 9.0, 9.0, 9.0, 9.0],
        [9.0, 9.0, 0.0, 1.0, 9.0, 9.0, 9.0, 9.0],
        [9.0, 9.0, 9.0, 9.0, 1.0, 3.0, 9.0, 9.0],
        [9.0, 9.0, 9.0, 9.0, 0.0, 1.0, 9.0, 9.0],
        [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1.0, 9.0],
        [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 1.0],
    ]
    assert f_mat == pytest.approx(np.array(ref))


def test_get_f_mat_incompatible_precursors(gen_x: NdKkfMatGenX) -> None:
    """."""
    f_mat = -9 * np.ones((8, 8))
    with pytest.raises(AssertionError):
        gen_x.fill_f_mat(NdKkfPrecursors([3, 1]), f_mat)
