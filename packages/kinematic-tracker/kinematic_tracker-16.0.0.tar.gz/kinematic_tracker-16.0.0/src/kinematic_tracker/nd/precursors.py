"""Calculation of 1D kinematic matrices for a given sets of orders.

The object stores kinematic matrix (transition- and white-noise) generators
and assists in computing, buffering and accessing the 1D parts in the state
matrix ND generators.
"""

from typing import Sequence

from kinematic_tracker.matrices.factory import KinematicMatrices, get_is_order_implemented


class NdKkfPrecursors:
    """1D precursors object to organize the computation and access to 1D kinematic matrices."""

    def __init__(self, orders: Sequence[int]) -> None:
        """Precursor matrices (1D kinematic matrices) assistant.

        Provided with a sequence of orders participating in the ND vectors,
        the assistant stores the corresponding set of kinematic orders. When executing
        the computation of the 1D matrices, only orders from this set will be calculated.

        Args:
            orders: the kinematic orders of interest.
        """
        self.orders_set = set()
        self.set_orders(orders)
        self.last_dt = 0.0
        self.kin_mat_gen = [KinematicMatrices(o) if o > 0 else None for o in range(5)]

    def set_orders(self, orders: Sequence[int]) -> None:
        """Hot-change of the orders sequence.

        Args:
            orders: the kinematic orders of interest.

        Raises:
            AssertError: if the new orders are not complying with the requirements.
        """
        assert len(orders) > 0
        assert all([get_is_order_implemented(o) for o in orders])
        self.orders_set = set(orders)
        self.last_dt = 0.0

    def compute(self, dt: float) -> None:
        """Compute the 1D kinematic matrices for a given time step.

        Args:
            dt: the time step
        """
        self.last_dt = dt
        for o in self.orders_set:
            self.kin_mat_gen[o].compute_q_mat(dt)
            self.kin_mat_gen[o].compute_f_mat(dt)
