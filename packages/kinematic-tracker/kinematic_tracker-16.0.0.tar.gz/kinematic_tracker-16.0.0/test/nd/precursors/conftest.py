"""."""

import pytest

from kinematic_tracker.nd.precursors import NdKkfPrecursors


@pytest.fixture
def pre() -> NdKkfPrecursors:
    return NdKkfPrecursors([3, 2])
