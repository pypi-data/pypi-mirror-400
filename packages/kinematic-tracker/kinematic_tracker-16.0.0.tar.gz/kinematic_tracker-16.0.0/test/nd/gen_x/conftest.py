"""."""

import pytest

from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.nd.precursors import NdKkfPrecursors


@pytest.fixture
def pre() -> NdKkfPrecursors:
    return NdKkfPrecursors([2, 1])


@pytest.fixture
def gen_x() -> NdKkfMatGenX:
    return NdKkfMatGenX([2, 1], [3, 2])
