"""Factory module for creating kinematic-matrix generators for a given point-motion model (order).

This module provides a `KinematicMatrices` class to compute and store the
white-noise covariance matrices Q and state transition (fundamental) matrices F
for different point-motion models:

   - constant position, kinematic order 1
   - constant velocity, kinematic order 2
   - constant acceleration, kinematic order 3
   - constant jerk, kinematic order 4.
"""

from .const_acc.fundamental import FundMatCa
from .const_acc.proc_cov import WhiteNoiseMatCa
from .const_jerk.fundamental import FundMatCj
from .const_jerk.proc_cov import WhiteNoiseMatCj
from .const_pos.fundamental import FundMatCp
from .const_pos.proc_cov import WhiteNoiseMatCp
from .const_vel.fundamental import FundMatCv
from .const_vel.proc_cov import WhiteNoiseMatCv


def get_is_order_implemented(order: int) -> bool:
    """
    Check if the given kinematic order is implemented.

    Args:
        order: The kinematic order to check.

    Returns:
        bool: True if the order is implemented (1 to 4), False otherwise.
    """
    return 0 < order < 5


class KinematicMatrices:
    """
    A class to generate and compute 1D kinematic matrices for different orders.

    Attributes:
        num_x: The kinematic order (1 to 4).
        q_mat_gen: The generator for the process noise covariance matrix Q.
        f_mat_gen: The generator for the state transition matrix F.
        q_mat_dt: The white-noise covariance matrix Q (result buffer) for a given time step.
        f_mat_dt: The state transition matrix F (result buffer) for a given time step.
    """

    def __init__(self, num_x: int) -> None:
        """
        Initialize the KinematicMatrices object.

        Args:
            num_x: The kinematic order (1 to 4).

        Raises:
            AssertionError: If the given kinematic order is not implemented.
        """
        assert get_is_order_implemented(num_x), f'Not implemented num_x {num_x}'
        self.num_x = num_x
        if num_x == 1:
            self.q_mat_gen = WhiteNoiseMatCp()
            self.f_mat_gen = FundMatCp()
        elif num_x == 2:
            self.q_mat_gen = WhiteNoiseMatCv()
            self.f_mat_gen = FundMatCv()
        elif num_x == 3:
            self.q_mat_gen = WhiteNoiseMatCa()
            self.f_mat_gen = FundMatCa()
        elif num_x == 4:
            self.q_mat_gen = WhiteNoiseMatCj()
            self.f_mat_gen = FundMatCj()
        self.q_mat_dt = self.q_mat_gen.q_mat
        self.f_mat_dt = self.f_mat_gen.f_mat

    def compute_q_mat(self, dt: float) -> None:
        """
        Compute the process noise covariance matrix (Q) for a given time step.

        Args:
            dt: The time step for which to compute the matrix.
        """
        self.q_mat_gen.compute(dt)

    def compute_f_mat(self, dt: float) -> None:
        """
        Compute the state transition matrix (F) for a given time step.

        Args:
            dt: The time step for which to compute the matrix.
        """
        self.f_mat_gen.compute(dt)
