"""."""

import pytest

from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.proc_noise.nd_kkf_white_noise_const import NdKkfWhiteNoiseConst


@pytest.fixture
def pre() -> NdKkfPrecursors:
    return NdKkfPrecursors([2, 1])


@pytest.fixture
def gen_x() -> NdKkfMatGenX:
    return NdKkfMatGenX([2, 1], [3, 2])


@pytest.fixture
def wn_const(gen_x: NdKkfMatGenX) -> NdKkfWhiteNoiseConst:
    """."""
    return NdKkfWhiteNoiseConst(gen_x, 5.678)
