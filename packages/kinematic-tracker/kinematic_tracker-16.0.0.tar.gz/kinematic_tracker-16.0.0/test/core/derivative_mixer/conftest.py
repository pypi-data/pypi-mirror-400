"""."""

import pytest

from kinematic_tracker.core.derivative_mixer import DerivativeMixer


@pytest.fixture
def der_mix() -> DerivativeMixer:
    """."""
    return DerivativeMixer(0.7, 3, True)
