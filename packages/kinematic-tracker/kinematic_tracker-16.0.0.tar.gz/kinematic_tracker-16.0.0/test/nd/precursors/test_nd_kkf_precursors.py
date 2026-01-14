"""."""

import pytest

from kinematic_tracker.nd.precursors import NdKkfPrecursors


def test_nd_kkf_pre_init_simple(pre: NdKkfPrecursors) -> None:
    """."""
    assert pre.kin_mat_gen[0] is None
    for order in (1, 2, 3, 4):
        assert pre.kin_mat_gen[order].num_x == order
    assert pre.orders_set == {2, 3}


def test_nd_kkf_pre_init_asserts() -> None:
    """."""
    with pytest.raises(AssertionError):
        NdKkfPrecursors([])
    with pytest.raises(AssertionError):
        NdKkfPrecursors([0, 1])
    with pytest.raises(AssertionError):
        NdKkfPrecursors([5, 1])
