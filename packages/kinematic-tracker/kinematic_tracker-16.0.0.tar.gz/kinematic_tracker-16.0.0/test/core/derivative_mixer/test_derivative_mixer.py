"""."""

import numpy as np
import pytest

from .conftest import DerivativeMixer


def test_derivative_mixer_fixed(der_mix: DerivativeMixer) -> None:
    """."""
    der_mix.is_dynamic = False
    der_mix.save_values(np.ones(3))
    der_mix.compute(1.0, 2.0 * np.ones(3))
    assert der_mix.derivatives == pytest.approx(0.3 * np.ones(3))

    der_mix.save_values(2.5 * np.ones(3))
    der_mix.compute(1.0, 3.0 * np.ones(3))
    assert der_mix.derivatives == pytest.approx(0.36 * np.ones(3))
