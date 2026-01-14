"""This is the transition matrix for the constant-position motion model for Cartesian point."""

import numpy as np


class FundMatCp:
    """."""

    def __init__(self) -> None:
        """."""
        self.f_mat = np.ones((1, 1))

    def compute(self, _dt: float) -> None:
        """."""
