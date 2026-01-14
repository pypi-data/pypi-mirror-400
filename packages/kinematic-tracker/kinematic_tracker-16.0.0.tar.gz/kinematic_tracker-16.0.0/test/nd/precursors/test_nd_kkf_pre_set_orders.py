"""."""

import pytest

from kinematic_tracker.nd.precursors import NdKkfPrecursors


def test_nd_kkf_pre_set_orders(pre: NdKkfPrecursors) -> None:
    """."""
    pre.set_orders([3, 4, 1])
    assert pre.orders_set == {1, 3, 4}


def test_nd_kkf_pre_set_orders_exceptions(pre: NdKkfPrecursors) -> None:
    """."""
    with pytest.raises(AssertionError):
        pre.set_orders([0, 4, 1])

    with pytest.raises(AssertionError):
        pre.set_orders([5, 1])

    with pytest.raises(AssertionError):
        pre.set_orders([])
