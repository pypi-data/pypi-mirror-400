"""."""

import numpy as np
import pytest

from cv2 import KalmanFilter

from kinematic_tracker.nd.gen_kf import NdKkfGenKf
from kinematic_tracker.nd.gen_xz import NdKkfMatGenXz
from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.nd.shape import NdKkfShape
from kinematic_tracker.proc_noise.meta import ProcNoiseMeta
from kinematic_tracker.proc_noise.nd_kkf_white_noise_fd import NdKkfWhiteNoiseFd
from kinematic_tracker.tracker.kkf import NdKkf


@pytest.fixture
def pre() -> NdKkfPrecursors:
    return NdKkfPrecursors([2, 1])


@pytest.fixture
def gen_xz(shape: NdKkfShape) -> NdKkfMatGenXz:
    return shape.get_mat_gen_xz()


@pytest.fixture
def shape() -> NdKkfShape:
    """."""
    return NdKkfShape([2, 1], [3, 2], [1, 1])


@pytest.fixture
def kf(gen_xz: NdKkfMatGenXz) -> KalmanFilter:
    """."""
    vec_z = np.linspace(1.0, 5.0, num=5)
    cov_zz = 6.0 * np.eye(5)
    ini_der_vars = np.linspace(31.0, 35.0, num=5)
    gen_kf = NdKkfGenKf(np.eye(8))
    return gen_kf.get_kf(gen_xz, vec_z, cov_zz, ini_der_vars)


@pytest.fixture
def kkf_wn(kf: KalmanFilter, gen_xz: NdKkfMatGenXz, pn_meta_fd: ProcNoiseMeta) -> NdKkf:
    """."""
    wn_fd = NdKkfWhiteNoiseFd(gen_xz.gen_x, pn_meta_fd, kf.statePre[:, 0])
    return NdKkf(kf, wn_fd)
