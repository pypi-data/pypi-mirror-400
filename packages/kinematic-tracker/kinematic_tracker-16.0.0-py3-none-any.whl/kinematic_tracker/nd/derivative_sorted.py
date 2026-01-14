"""Produce a derivative-sorted ordering of the variables.

Convert the block-diagonal ordered vectors and matrices to a derivative-sorted ordering.
For example, for an ND state with orders [3, 1] and number of dimensions [2, 2],
the block-diagonal state vector (bd) used internally, is going to have entries

   bd^T = (px, vx, ax, py, vy, ay, dx, dy)

The corresponding derivative-sorted state vector (ds) is

   ds^T = (px, py, dx, dy, vx, vy, ax, ay)

The derivative-sorted ordering might simplify input-output processing.
"""

from typing import Sequence

import numpy as np

from .gen_x import NdKkfMatGenX


class DerivativeSorted:
    """The helper for the derivative-sorted ordering of the variables."""

    def __init__(self, gen_x: NdKkfMatGenX) -> None:
        """Constructor

        Args:
            gen_x: the state-vector generator.
        """
        nx = gen_x.num_x
        self.tmp_mat = np.zeros((nx, nx))
        self.c_mat = np.zeros((nx, nx))
        self.bd_ds = np.zeros(nx, dtype=int)
        ind = 0
        for der_order in range(4):
            for part_order, s, _ in gen_x.gen_loop():
                if der_order < part_order:
                    self.bd_ds[s + der_order] = ind
                    self.c_mat[ind, s + der_order] = 1.0
                    ind += 1

    def convert_vec(self, vec_x: np.ndarray, out_x: np.ndarray) -> None:
        """Convert from block-diagonal to derivative-sorted ordering for a single vector.

        Args:
            vec_x: the block-diagonal vector.
            out_x: the buffer to fill with the corresponding derivative-sorted vector.
        """
        out_x[self.bd_ds] = vec_x

    def convert_vectors(self, vec_sx: Sequence[np.ndarray], out_sx: Sequence[np.ndarray]) -> None:
        """Convert to derivative-sorted ordering for a sequence of state vectors.

        Args:
            vec_sx: the input sequence of vectors with block-diagonal ordering of variables.
            out_sx: the buffers to fill with derivative-sorted ordering.
        """
        for vec_x, out_x in zip(vec_sx, out_sx):
            self.convert_vec(vec_x, out_x)

    def convert_mat(self, in_xx: np.ndarray, out_xx: np.ndarray) -> None:
        """Convert the block-diagonal covariance matrices to the derivative-sorted covariances.

        Args:
            in_xx: the input matrix with block-diagonal ordering of variables.
            out_xx: the output matrix with derivative-sorted ordering of variables.
        """
        np.dot(self.c_mat, in_xx, out=self.tmp_mat)
        np.dot(self.tmp_mat, self.c_mat.T, out=out_xx)

    def get_num_x(self) -> int:
        """Get the number of variables in the state vectors

        Returns:
            The number of variables in the state vectors.
        """
        return self.c_mat.shape[0]
