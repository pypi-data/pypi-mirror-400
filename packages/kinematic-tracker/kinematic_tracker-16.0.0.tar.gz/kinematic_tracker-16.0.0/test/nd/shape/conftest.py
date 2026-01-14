"""."""

import pytest

from kinematic_tracker.nd.shape import NdKkfShape


@pytest.fixture
def shape() -> NdKkfShape:
    """."""
    return NdKkfShape([2, 3], [3, 2], [1, 2])
