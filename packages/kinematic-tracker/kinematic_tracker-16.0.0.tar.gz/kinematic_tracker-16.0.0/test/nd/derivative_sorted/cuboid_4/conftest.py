"""."""

import pytest

from kinematic_tracker.nd.derivative_sorted import DerivativeSorted
from kinematic_tracker.nd.gen_x import NdKkfMatGenX


@pytest.fixture
def gen_x() -> NdKkfMatGenX:
    return NdKkfMatGenX([4], [2])


@pytest.fixture
def der_sorted(gen_x: NdKkfMatGenX) -> DerivativeSorted:
    """."""
    return DerivativeSorted(gen_x)
