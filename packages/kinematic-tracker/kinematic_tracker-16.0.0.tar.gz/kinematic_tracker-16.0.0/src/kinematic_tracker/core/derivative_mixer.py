"""
This module defines the `DerivativeMixer` class. The class provides functionality
to compute the derivatives (finite-differences) and compute running average of these
derivatives of a given set of variables.
"""

import numpy as np


DT_TOL = 1.0e-5  # Default tolerance for the time step


class DerivativeMixer:
    """
    A class to compute and mix derivatives of values over time, with support
    for dynamic or static mixing weights.

    Attributes:
        mix_weight: The mixing weight used for running averages.
        num_var: The number of variables being tracked.
        is_dynamic: Indicates whether the mixing weight is dynamic.
        values: The current values of the variables.
        derivatives: The computed derivatives of the variables (result).
        counter: A counter used for dynamic weight computation.
        dt_tol: The tolerance for the time step.
        last_mix_weight: The last computed mixing weight.
    """

    def __init__(
        self, mix_weight: float, num_var: int, is_dynamic: bool, dt_tol: float = DT_TOL
    ) -> None:
        """
        Initializes the `DerivativeMixer` class with the given parameters.

        Args:
            mix_weight: The nominal mixing weight for averaging of derivatives.
            num_var: The number of variables to compute.
            is_dynamic: Whether the mixing weight is dynamic.
            dt_tol: The optional tolerance for the time step. Defaults to `DT_TOL`.
        """
        self.mix_weight = mix_weight
        assert num_var > 0
        self.num_var = num_var
        self.is_dynamic = is_dynamic
        self.values: np.ndarray = np.zeros(num_var)
        self.derivatives: np.ndarray = np.zeros(num_var)
        self.counter: int = 0
        self.dt_tol = dt_tol
        self.last_mix_weight = 0.0

    def get_mixing_weight(self) -> float:
        """
        Computes the mixing weight based on the current state.

        Returns:
            float: The computed mixing weight.
        """
        if self.is_dynamic:
            w = self.counter / (self.counter + 1.0)
            w = w if w < self.mix_weight else self.mix_weight
        else:
            w = self.mix_weight
        self.counter += 1
        self.last_mix_weight = w
        return w

    def save_values(self, values: np.ndarray) -> None:
        """
        Saves the current values for future derivative computation.

        Args:
            values: The values to save.
        """
        self.values[:] = values

    def compute(self, dt: float, values: np.ndarray) -> None:
        """
        Computes the derivatives of the given values based on the time step.

        Args:
            dt: The time step for derivative computation.
            values: The new values to compute derivatives from.

        The computation blends the new derivatives with the previous ones
        using the mixing weight.
        """
        if dt > self.dt_tol:
            w = self.get_mixing_weight()
            self.derivatives[:] = w * self.derivatives[:] + (1.0 - w) * (values - self.values) / dt
