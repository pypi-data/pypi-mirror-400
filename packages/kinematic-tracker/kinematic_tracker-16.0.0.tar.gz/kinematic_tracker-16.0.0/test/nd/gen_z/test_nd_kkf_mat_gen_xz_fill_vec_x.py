"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.gen_xz import NdKkfMatGenXz


REF = [1, 404, 2, 404, 3, 404, 4, 404, 5, 6, 404, 7, 8, 404, 9, 10, 404, 11, 12, 404, 13, 14, 404]


def test_nd_kkf_mat_gen_xz_fill_vec_x(gen_xz: NdKkfMatGenXz) -> None:
    """."""
    vec_z = np.linspace(1, 14, num=14)
    vec_x = 404 * np.ones(gen_xz.gen_x.num_x)
    gen_xz.fill_vec_x(vec_z, vec_x)
    assert vec_x == pytest.approx(REF)


def test_easy_fill_vec_x(gen_xz: NdKkfMatGenXz) -> None:
    """."""
    vec_z = np.linspace(1, 14, num=14)
    vec_x = np.dot(gen_xz.h_mat.T, vec_z)
    ref_x = np.array(REF)
    ref_x[ref_x > 403] = 0.0
    assert vec_x == pytest.approx(ref_x)
