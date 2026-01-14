"""."""

from kinematic_tracker.nd.gen_xz import NdKkfMatGenXz
from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.nd.shape import NdKkfShape


def test_nd_kkf_get_precursors(shape: NdKkfShape) -> None:
    """."""
    pre = shape.get_precursors()
    assert isinstance(pre, NdKkfPrecursors)


def test_nd_kkf_get_gen_xz(shape: NdKkfShape) -> None:
    """."""
    gen_xz = shape.get_mat_gen_xz()
    assert isinstance(gen_xz, NdKkfMatGenXz)
