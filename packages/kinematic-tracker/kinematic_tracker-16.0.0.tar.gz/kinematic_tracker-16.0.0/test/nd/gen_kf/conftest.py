"""."""

import numpy as np
import pytest

from cv2 import KalmanFilter

from kinematic_tracker.nd.gen_kf import NdKkfGenKf
from kinematic_tracker.nd.gen_xz import NdKkfMatGenXz
from kinematic_tracker.nd.shape import NdKkfShape


@pytest.fixture
def shape() -> NdKkfShape:
    """."""
    return NdKkfShape([2, 1], [2, 1], [1, 1])


@pytest.fixture
def gen_xz(shape: NdKkfShape) -> NdKkfMatGenXz:
    """."""
    return shape.get_mat_gen_xz()


@pytest.fixture
def gen_kf(gen_xz: NdKkfMatGenXz) -> NdKkfGenKf:
    """."""
    nx = gen_xz.gen_x.num_x
    return NdKkfGenKf(np.zeros((nx, nx)))


@pytest.fixture
def kf(gen_kf: NdKkfGenKf, gen_xz: NdKkfMatGenXz) -> KalmanFilter:
    """."""
    vec_z = np.linspace(1.0, 3.0, num=3)
    cov_zz = 3.0 * np.eye(3)
    ini_der_vars = 100 * np.linspace(1.0, 3.0, num=3)
    return gen_kf.get_kf(gen_xz, vec_z, cov_zz, ini_der_vars)


@pytest.fixture
def kf_predicted(
    kf: KalmanFilter, gen_xz: NdKkfMatGenXz, shape: NdKkfShape, gen_kf: NdKkfGenKf
) -> KalmanFilter:
    """."""
    pre = shape.get_precursors()
    pre.compute(3.0)
    gen_x = gen_xz.gen_x
    gen_x.fill_f_mat(pre, gen_kf.f_mat)
    kf.statePost[:, 0] = np.linspace(1.0, 5.0, num=5)
    factors = 6 * np.linspace(1.0, 3.0, num=3)
    gen_x.fill_q_mat(pre, factors, kf.processNoiseCov)
    kf.predict(None)
    return kf
