"""."""

import numpy as np
import pytest

from .conftest import DerivativeMixer


def test_derivative_mixer_dynamic(der_mix: DerivativeMixer) -> None:
    """."""
    der_mix.save_values(np.ones(3))
    der_mix.compute(1.0, 2.0 * np.ones(3))
    assert der_mix.derivatives == pytest.approx(1.0 * np.ones(3))

    der_mix.save_values(2.5 * np.ones(3))
    der_mix.compute(1.0, 3.0 * np.ones(3))
    assert der_mix.derivatives == pytest.approx(0.75 * np.ones(3))


def test_derivative_mixer_zero_dt(der_mix: DerivativeMixer) -> None:
    """."""
    der_mix.save_values(np.ones(3))
    der_mix.compute(0.0, 2.0 * np.ones(3))
    assert der_mix.derivatives == pytest.approx(np.zeros(3))
    der_mix.compute(1.0, 2.0 * np.ones(3))
    assert der_mix.derivatives == pytest.approx(1.0 * np.ones(3))
