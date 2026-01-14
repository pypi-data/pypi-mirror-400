"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.shape import NdKkfShape


def test_nd_kkf_init(shape: NdKkfShape) -> None:
    """."""
    assert isinstance(shape.orders_z, np.ndarray)
    assert isinstance(shape.orders_x, np.ndarray)
    assert isinstance(shape.num_dims, np.ndarray)
    assert shape.orders_z == pytest.approx([1, 2])
    assert shape.orders_x == pytest.approx([2, 3])
    assert shape.num_dims == pytest.approx([3, 2])


def test_nd_kkf_repr(shape: NdKkfShape) -> None:
    """."""
    assert repr(shape) == 'NdKkfShape( orders_x [2 3] num_dims [3 2] orders_z [1 2])'
