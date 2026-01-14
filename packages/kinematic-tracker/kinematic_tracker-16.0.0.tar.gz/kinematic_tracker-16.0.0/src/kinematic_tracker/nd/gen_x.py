"""Generator of the block-diagonal, n-dimensional, kinematic, Kalman-filter matrices.

The fundamental- and process-noise matrices are generated for an n-dimensional state vector
composed of 1D kinematic state vectors.

The n-dimensional state vector is defined by a list of *kinematic orders* and their corresponding
*numbers of degrees of freedom* (DOF).
For example, a simple tracking_cuboid of cuboids with their centers processes with
constant-velocity (CV) point-motion model (PMM) and their dimensions processes with
constant-position (CP) PMM is defined by the orders [2, 1] and numbers of DOF [3, 3].
The distribution of variables in the composed state vector will be:

    state_vector = (pos_x, vel_x, pos_y, vel_y, pos_z, vel_z, dim_x, dim_y, dim_z)

To track the orientation (yaw) of cuboids we will add the 2-dimensional CP PMM to process
for x = cos(yaw) and y = sin(yaw). As a result the orders will be [2, 1, 1] and
numbers of DOF [3, 3, 2]. The distribution of variables in the composed state vector will be:

    state_vector = (pos_x, vel_x, pos_y, vel_y, pos_z, vel_z, dim_x, dim_y, dim_z, yaw_x, yaw_y)

Possible choices for kinematic orders range between 1 and 4. The correspondence between the
kinematic orders and PMMs is CP = 1, CV = 2, constant acceleration (CA) = 3 and
constant jerk (CJ) = 4. Number of DOF could vary from 1 to any big number. In practice,
the number of DOF is 2 or 3.

The number of variables in the state vector is  $N = sum_i Order_i * DOF_i$.
"""

from typing import Generator, Sequence

import numpy as np

from kinematic_tracker.matrices.factory import get_is_order_implemented

from .precursors import NdKkfPrecursors


def assert_compatible(orders: Sequence[int], num_dof: Sequence[int]) -> None:
    """Assert correctness of the kinematic orders and numbers of degrees of freedom (DoF).

    There should be at least one entry in the orders sequence.
    Every entry in orders should 1, 2, 3 or 4.
    Number of entries in orders should be the same as in num_dof.
    Every entry in num_dof should be positive.

    Args:
        orders: the kinematic orders for every part of the state vector.
        num_dof: numbers of degrees of freedom for every part of the state vector.

    Raises:
        Assert exceptions whenever some condition is not met.
    """
    assert len(orders) > 0
    assert all([get_is_order_implemented(o) for o in orders])
    assert len(orders) == len(num_dof)
    assert all([n > 0 for n in num_dof])


class NdKkfMatGenX:
    """Generator of the block-diagonal, n-dimensional, kinematic state matrices."""

    def __init__(self, orders: Sequence[int], num_dof: Sequence[int]) -> None:
        """Constructor

        Args:
            orders: the kinematic orders for every part of the state vector.
            num_dof: numbers of degrees of freedom for every part of the state vector.
        """
        assert_compatible(orders, num_dof)
        self.orders = np.empty(len(orders), dtype=int)
        self.orders_set = set()
        self.num_dof = np.array(num_dof, dtype=int)
        self.num_x = 0
        self.num_d = 0
        self.set_orders(orders)

    def set_orders(self, orders: Sequence[int]) -> None:
        """Setter for the kinematic orders.

        This is a helper method which allows to change the list of orders without
        creation of the new generator object.

        Args:
            orders: new kinematic orders.
        """
        assert_compatible(orders, self.num_dof)
        self.orders[:] = np.array(orders, dtype=int)
        self.orders_set.clear()
        self.orders_set |= set(orders)
        self.num_x = np.sum(self.orders * self.num_dof)
        self.num_d = int(self.num_dof.sum())

    def fill_q_mat(self, pre: NdKkfPrecursors, factors: np.ndarray, cov_xx: np.ndarray) -> None:
        """Fill the process-noise covariance matrix.

        Args:
            pre: a precursor object storing the precomputed 1D white-noise matrices.
            factors: a sequence of prefactors for each 1D part of the state vector.
            cov_xx: the resulting covariance matrix to be assigned (filled).

        Raises:
            AssertError: if precursor object or factor sequence are not compatible.
        """
        assert pre.orders_set == self.orders_set, (
            f' pre.orders_set {pre.orders_set} != gen.orders_set {self.orders_set}'
        )
        assert factors.shape == (self.num_d,)

        for (o, s, e), factor in zip(self.gen_loop(), factors):
            q_mat_dt = pre.kin_mat_gen[o].q_mat_dt
            cov_xx[s:e, s:e] = factor * q_mat_dt

    def fill_f_mat(self, pre: NdKkfPrecursors, f_mat_xx: np.ndarray) -> None:
        """Fill the transition (fundamental) matrix.

        Args:
            pre: a precursor object storing the precomputed 1D white-noise matrices.
            f_mat_xx: the resulting fundamental matrix to be assigned (filled).

        Raises:
            AssertError: if precursor object is not compatible with the generator.
        """
        assert pre.orders_set == self.orders_set
        for o, s, e in self.gen_loop():
            f_mat_dt = pre.kin_mat_gen[o].f_mat_dt
            f_mat_xx[s:e, s:e] = f_mat_dt

    def gen_loop(self) -> Generator[tuple[int, int, int], None, None]:
        """Generator of the loops over the 1D parts of the state vector.

        Returns:
            Generator yielding a complete sequence of orders, start and end indices.
        """
        s = 0
        for o, nd in zip(self.orders, self.num_dof):
            for _ix in range(nd):
                e = s + o
                yield o, s, e
                s = e
