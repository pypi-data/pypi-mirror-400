"""."""

import pytest

from .conftest import KinematicMatrices


def test_const_pos() -> None:
    """."""
    gen = KinematicMatrices(1)
    assert gen.f_mat_dt.shape == (1, 1)
    assert gen.q_mat_dt.shape == (1, 1)


def test_const_vel() -> None:
    """."""
    gen = KinematicMatrices(2)
    assert gen.f_mat_dt.shape == (2, 2)
    assert gen.q_mat_dt.shape == (2, 2)


def test_const_acc() -> None:
    """."""
    gen = KinematicMatrices(3)
    assert gen.f_mat_dt.shape == (3, 3)
    assert gen.q_mat_dt.shape == (3, 3)


def test_const_jrk() -> None:
    """."""
    gen = KinematicMatrices(4)
    assert gen.f_mat_dt.shape == (4, 4)
    assert gen.q_mat_dt.shape == (4, 4)


def test_exceptions() -> None:
    """."""
    with pytest.raises(AssertionError):
        KinematicMatrices(-1)

    with pytest.raises(AssertionError):
        KinematicMatrices(0)

    with pytest.raises(AssertionError):
        KinematicMatrices(5)
