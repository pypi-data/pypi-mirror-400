"""."""

import pytest

from kinematic_tracker.nd.gen_x import NdKkfMatGenX


def test_nd_kkf_init_simple() -> None:
    """."""
    gen = NdKkfMatGenX([2, 1], [3, 2])
    assert gen.num_x == 8
    assert gen.orders_set == {1, 2}
    assert gen.num_d == 5


def test_nd_kkf_init_asserts() -> None:
    """."""
    with pytest.raises(AssertionError):
        NdKkfMatGenX([], [])
    with pytest.raises(AssertionError):
        NdKkfMatGenX([2, 1], [3, 2, 1])
    with pytest.raises(AssertionError):
        NdKkfMatGenX([0, 1], [3, 2])
    with pytest.raises(AssertionError):
        NdKkfMatGenX([5, 1], [3, 2])
