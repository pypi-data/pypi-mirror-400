"""."""

from kinematic_tracker.nd.derivative_sorted import DerivativeSorted
from kinematic_tracker.nd.gen_x import NdKkfMatGenX


def test_init_and_get_num_x() -> None:
    """."""
    gen_x = NdKkfMatGenX([3, 1], [3, 2])
    der_sorted = DerivativeSorted(gen_x)
    assert der_sorted.get_num_x() == 11
