"""The parameters for initialization of the Kalman filter and ProcNoise objects.

The class provides the corresponding methods as well.
"""

from typing import Sequence

import numpy as np

from .gen_x import NdKkfMatGenX
from .gen_xz import NdKkfMatGenXz
from .precursors import NdKkfPrecursors


class NdKkfShape:
    """."""

    def __init__(
        self, orders_x: Sequence[int], num_dims: Sequence[int], orders_z: Sequence[int]
    ) -> None:
        """The constructor

        Args:
            orders_x: point-motion models of the partial kinematic states (CP - 1, CV - 2, CA - 3, CJ - 4).
            num_dims: numbers of Cartesian degrees of freedom for every partial state.
            orders_z: description of detection content similar to the point-motion models of the states.
        """
        self.orders_x = np.array(orders_x, dtype=int)
        self.num_dims = np.array(num_dims, dtype=int)
        self.orders_z = np.array(orders_z, dtype=int)

    def __repr__(self) -> str:
        """."""
        return (
            f'NdKkfShape( '
            f'orders_x {self.orders_x} '
            f'num_dims {self.num_dims} '
            f'orders_z {self.orders_z})'
        )

    def get_precursors(self) -> NdKkfPrecursors:
        """Compose a ready-to-use precursor object.

        Returns:
            The precursor object.
        """
        return NdKkfPrecursors(self.orders_x)

    def _get_mat_gen_x(self) -> NdKkfMatGenX:
        """Compose a ready-to-use state matrix generator.

        Returns:
            The state matrix generator object.
        """
        return NdKkfMatGenX(self.orders_x, self.num_dims)

    def get_mat_gen_xz(self) -> NdKkfMatGenXz:
        """Compose a ready-to-use measurement matrix generator.

        Returns:
            The Kalman-matrices generator object.
        """
        gen_x = self._get_mat_gen_x()
        return NdKkfMatGenXz(gen_x, self.orders_z)
