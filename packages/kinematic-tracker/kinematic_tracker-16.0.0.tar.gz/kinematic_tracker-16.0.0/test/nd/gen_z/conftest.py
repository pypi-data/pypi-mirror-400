"""."""

import pytest

from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.nd.gen_xz import NdKkfMatGenXz


@pytest.fixture
def gen_x() -> NdKkfMatGenX:
    return NdKkfMatGenX([2, 3], [4, 5])


@pytest.fixture
def gen_xz(gen_x: NdKkfMatGenX) -> NdKkfMatGenXz:
    return NdKkfMatGenXz(gen_x, [1, 2])
