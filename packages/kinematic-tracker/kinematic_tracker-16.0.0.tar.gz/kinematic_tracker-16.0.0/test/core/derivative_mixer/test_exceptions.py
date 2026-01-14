"""."""

import pytest

from .conftest import DerivativeMixer


def test_derivative_mixer_exception_in_constructor() -> None:
    """."""
    with pytest.raises(AssertionError):
        DerivativeMixer(0.7, 0, False)

    with pytest.raises(AssertionError):
        DerivativeMixer(0.7, -1, False)
