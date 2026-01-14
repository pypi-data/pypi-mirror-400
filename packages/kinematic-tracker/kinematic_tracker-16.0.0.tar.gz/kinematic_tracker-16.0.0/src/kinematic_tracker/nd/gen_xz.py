"""Support of the block-diagonal measurement model.

The measurement model is given by a sequence of kinematic orders.
For example, if the ND state vector has one 3D part with the constant-velocity
(CV) point-motion model, then the sequence of state orders contains just one
order [2]. In this case, the sequence of measurement orders could be either [1]
or [2]. If the sequence of measurement orders is [1], then the measurements
vectors will include coordinates. If the sequence of measurement orders is [2],
then the measurements vectors will include coordinates and velocities.
"""

from typing import Generator, Sequence

import numpy as np

from .gen_x import NdKkfMatGenX


def assert_orders_z_compatible(gen_x: NdKkfMatGenX, orders_z: Sequence[int]) -> None:
    """Assert compatibility of the state-matrix generator and the measurement orders.

    Args:
        gen_x: the generator of state matrices.
        orders_z: the sequence of the measurement orders.

    Raises:
        AssertError: if number of parts are different or any of the measurement
                     orders exceeds the corresponding state order.
    """
    assert len(gen_x.orders) == len(orders_z), (
        f'Length should be equal, but {len(gen_x.orders)} /= {len(orders_z)}.'
    )
    for order_x, order_z in zip(gen_x.orders, orders_z):
        assert order_z <= order_x, f'Measurement should have <= order, but {order_z} > {order_x}'
        assert order_z > 0, f'Measurement should contain some variables, but {order_z} < 1'


class NdKkfMatGenXz:
    """Generator of the block-diagonal, n-dimensional, kinematic, Kalman-filter matrices."""

    def __init__(self, gen_x: NdKkfMatGenX, orders_z: Sequence[int]) -> None:
        """Constructor.

        This object keeps the resulting ND measurement model (H matrix).

        In Python, in many case the conversion from the measurement vector z to
        state vector x is possible and faster by matrix multiplication x = H^T z.
        However, we decide for the loops as a close programming-solution model
        for lower-level languages.

        Args:
            gen_x: the generator of state matrices.
            orders_z: the measurement orders for every part of the state vector.
        """
        assert_orders_z_compatible(gen_x, orders_z)
        self.gen_x = gen_x
        self.orders_z = np.array(orders_z, dtype=int)
        self.num_p = len(orders_z)
        self.num_z = int(np.sum(self.orders_z * gen_x.num_dof))
        self.h_mat = np.zeros((self.num_z, gen_x.num_x))
        for o_x, s_x, e_x, o_z, s_z, e_z in self.gen_loop_xz():
            self.h_mat[s_z:e_z, s_x : s_x + o_z] = np.eye(o_z)

    def fill_vec_x(self, vec_z: np.ndarray, vec_x: np.ndarray) -> None:
        """Distribute the variables from the measurement vector to the state vector.

        It is a block-by-block distribution.

        Args:
            vec_z: the measurement vector.
            vec_x: the state vector.
        """
        assert vec_z.shape == (self.num_z,)
        assert vec_x.shape == (self.gen_x.num_x,)
        for o_x1, s_x1, _, o_z1, s_z1, e_z1 in self.gen_loop_xz():
            vec_x[s_x1 : s_x1 + o_z1] = vec_z[s_z1:e_z1]

    def fill_mat_xx(self, mat_zz: np.ndarray, mat_xx: np.ndarray) -> None:
        """Distribute the measurement covariance to the process-noise (state) covariance.

        Args:
            mat_zz: measurement covariance matrix.
            mat_xx: process-noise covariance matrix to be partially filled.
        """
        assert mat_zz.shape == (self.num_z, self.num_z)
        assert mat_xx.shape == (self.gen_x.num_x, self.gen_x.num_x)
        for o_x1, s_x1, _, o_z1, s_z1, e_z1 in self.gen_loop_xz():
            for o_x2, s_x2, _, o_z2, s_z2, e_z2 in self.gen_loop_xz():
                mat_xx[s_x1 : s_x1 + o_z1, s_x2 : s_x2 + o_z2] = mat_zz[s_z1:e_z1, s_z2:e_z2]

    def gen_loop_xz(self) -> Generator[tuple[int, int, int, int, int, int], None, None]:
        """Generator of the loop over 1D blocks of the state and measurement vectors.

        Returns:
            Generator yielding a complete sequence of orders, start and end indices
            for state and measurement vectors.
        """
        s_x = 0
        s_z = 0
        for o_x, o_z, nd in zip(self.gen_x.orders, self.orders_z, self.gen_x.num_dof):
            for _iz in range(nd):
                e_x = s_x + o_x
                e_z = s_z + o_z
                yield o_x, s_x, e_x, o_z, s_z, e_z
                s_x = e_x
                s_z = e_z
