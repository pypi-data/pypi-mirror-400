"""."""

import pytest

from kinematic_tracker.nd.gen_x import NdKkfMatGenX


def test_nd_kkf_mat_gen_set_orders(gen_x: NdKkfMatGenX) -> None:
    """."""
    gen_x.set_orders([4, 3])
    assert gen_x.orders_set == {3, 4}
    assert gen_x.num_x == 18
    assert gen_x.num_d == 5


def test_nd_kkf_mat_set_wrong_orders(gen_x: NdKkfMatGenX) -> None:
    """."""
    with pytest.raises(AssertionError):
        gen_x.set_orders([4, 3, 1])
    with pytest.raises(AssertionError):
        gen_x.set_orders([4, 0])
    with pytest.raises(AssertionError):
        gen_x.set_orders([])
