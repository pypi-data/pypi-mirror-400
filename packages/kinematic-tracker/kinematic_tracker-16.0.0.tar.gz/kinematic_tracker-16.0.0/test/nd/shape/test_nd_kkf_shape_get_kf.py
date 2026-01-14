"""."""

import numpy as np
import pytest

from cv2 import KalmanFilter

from kinematic_tracker.nd.gen_kf import NdKkfGenKf
from kinematic_tracker.nd.shape import NdKkfShape


def test_nd_kkf_get_kf(shape: NdKkfShape) -> None:
    """."""
    gen_xz = shape.get_mat_gen_xz()
    nz = gen_xz.num_z
    vec_z = np.linspace(1, nz, num=nz)
    cov_zz = np.linspace(1, nz * nz, num=nz * nz).reshape((nz, nz))
    num_dof_tot = gen_xz.gen_x.num_dof.sum()
    ini_der_vars = np.linspace(50, 50 + num_dof_tot - 1, num=num_dof_tot)
    gen_kf = NdKkfGenKf(np.eye(12))
    kf = gen_kf.get_kf(gen_xz, vec_z, cov_zz, ini_der_vars)
    assert isinstance(kf, KalmanFilter)
    assert kf.transitionMatrix == pytest.approx(np.eye(12))
    assert kf.processNoiseCov == pytest.approx(np.zeros((12, 12)))
    assert kf.measurementNoiseCov == pytest.approx(cov_zz)
    h_ref = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    ]
    assert kf.measurementMatrix == pytest.approx(np.array(h_ref))
    x_ref = [1, 0, 2, 0, 3, 0, 4, 5, 0, 6, 7, 0]
    assert kf.statePre[:, 0] == pytest.approx(x_ref)
    # fmt: off
    p_ref = [
                [1,  0,  2,  0,  3,  0,  4,  5,  0,  6,  7,  0],
                [0, 50,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
                [8,  0,  9,  0, 10,  0, 11, 12,  0, 13, 14,  0],
                [0,  0,  0, 51,  0,  0,  0,  0,  0,  0,  0,  0],
                [15, 0, 16,  0, 17,  0, 18, 19,  0, 20, 21,  0],
                [0,  0,  0,  0,  0, 52,  0,  0,  0,  0,  0,  0],
                [22, 0, 23,  0, 24,  0, 25, 26,  0, 27, 28,  0],
                [29, 0, 30,  0, 31,  0, 32, 33,  0, 34, 35,  0],
                [0,  0,  0,  0,  0,  0,  0,  0, 53,  0,  0,  0],
                [36, 0, 37,  0, 38,  0, 39, 40,  0, 41, 42,  0],
                [43, 0, 44,  0, 45,  0, 46, 47,  0, 48, 49,  0],
                [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 54],
    ]
    # fmt: on
    assert kf.errorCovPre == pytest.approx(np.array(p_ref))
