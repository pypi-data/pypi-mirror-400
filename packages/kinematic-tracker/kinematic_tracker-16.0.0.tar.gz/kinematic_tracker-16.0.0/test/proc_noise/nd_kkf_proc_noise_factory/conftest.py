"""."""

import pytest

from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.proc_noise.meta import ProcNoiseKind, ProcNoiseMeta, get_proc_noise_meta


@pytest.fixture
def gen_x() -> NdKkfMatGenX:
    """."""
    return NdKkfMatGenX([2, 1], [3, 2])


@pytest.fixture
def pn_meta_dia() -> ProcNoiseMeta:
    """."""
    return get_proc_noise_meta(ProcNoiseKind.DIAGONAL, 1.12, 0.75, True, True)
