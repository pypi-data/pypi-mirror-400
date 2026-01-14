"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.proc_noise.meta import ProcNoiseMeta
from kinematic_tracker.proc_noise.nd_kkf_white_noise_fd import NdKkfWhiteNoiseFd


@pytest.fixture
def pre() -> NdKkfPrecursors:
    return NdKkfPrecursors([2, 1])


@pytest.fixture
def gen_x() -> NdKkfMatGenX:
    return NdKkfMatGenX([2, 1], [3, 2])


@pytest.fixture
def wn_fd(gen_x: NdKkfMatGenX, pn_meta_fd: ProcNoiseMeta) -> NdKkfWhiteNoiseFd:
    """."""
    vec_x = np.linspace(1.0, 8.0, num=8)
    return NdKkfWhiteNoiseFd(gen_x, pn_meta_fd, vec_x)
