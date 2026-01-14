"""."""

import pytest

from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.proc_noise.nd_kkf_dia_noise import NdKkfDiaNoise


@pytest.fixture
def pre() -> NdKkfPrecursors:
    return NdKkfPrecursors([2, 1])


@pytest.fixture
def dia_n() -> NdKkfDiaNoise:
    """."""
    return NdKkfDiaNoise(5.678)
