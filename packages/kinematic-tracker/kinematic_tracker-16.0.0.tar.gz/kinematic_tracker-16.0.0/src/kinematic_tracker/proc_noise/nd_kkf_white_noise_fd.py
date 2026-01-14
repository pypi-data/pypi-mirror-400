"""Module for NdKkfWhiteNoiseFd.

This module defines the NdKkfWhiteNoiseFd class. The class serves as a driver
handling process-noise computations according to an original adaptive scheme.
It utilizes the white-noise template and dynamic factors to adjust the pre-factor
variance at each time step.

Classes:
    NdKkfWhiteNoiseFd: Handles process noise computations for kinematic states.
"""

import numpy as np

from kinematic_tracker.core.derivative_mixer import DerivativeMixer
from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.nd.precursors import NdKkfPrecursors

from .meta import ProcNoiseMeta


class NdKkfWhiteNoiseFd:
    """
    Class for handling an adaptive process-noise calculation in a kinematic tracking system.

    Attributes:
        gen_x: Driver for the block-diagonal matrix machinery.
        pn_meta: Parameters for process noise computation.
        variance_factor: Static scaling factor for variance.
        der_mixer: Handles running averages of the derivatives absent in the state.
        dynamic_factors: Stores computed dynamic factors.
        tmp_last_vars: Temporary storage for last variables.
    """

    def __init__(self, gen_x: NdKkfMatGenX, pn_meta: ProcNoiseMeta, vec_x: np.ndarray) -> None:
        """
        Constructor for NdKkfWhiteNoiseFd.

        Args:
            gen_x: The driver used for block-diagonal distribution of variables.
            pn_meta: Parameters for computation of the process noise.
            vec_x: Initial state vector.
        """
        self.gen_x = gen_x
        self.pn_meta = pn_meta
        is_dyn = pn_meta.is_dynamic_mixing
        self.variance_factor = pn_meta.factor
        self.der_mixer = DerivativeMixer(pn_meta.mix_weight, gen_x.num_d, is_dyn)
        self.gather_last_vars(vec_x, self.der_mixer.values)
        self.dynamic_factors = np.zeros(gen_x.num_d)
        self.tmp_last_vars = np.zeros_like(self.der_mixer.values)

    def gather_last_vars(self, vec_x: np.ndarray, last_vars: np.ndarray) -> None:
        """
        Gathers the last variables from the state vector.

        Args:
            vec_x: State vector.
            last_vars: Storage for the last variables (highest-order derivatives).
        """
        self.assert_shape_x(vec_x)
        for i, (o, s, e) in enumerate(self.gen_x.gen_loop()):
            last_vars[i] = vec_x[e - 1]

    def assert_shape_x(self, vec_x: np.ndarray):
        """
        Asserts that the shape of the state vector is valid.

        Args:
            vec_x: State vector.

        Raises:
            AssertionError: If the shape of vec_x is not (gen_x.num_x,).
        """
        assert vec_x.shape == (self.gen_x.num_x,), (
            f'Need 1-D initial state vector, but got {vec_x.shape}'
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the object.

        Returns:
            str: String representation of the object.
        """
        return f'NdKkfWhiteNoiseFd({self.pn_meta})'

    def compute_dyn_factors(self, vec_x: np.ndarray, derivatives: np.ndarray) -> None:
        """
        Computes dynamic factors based on the state vector and derivatives.

        For each part of the state vector, it computes the dynamic factors by
        multiplying the last derivative with the next derivative. For example,
        if we deal with the constant velocity (CV) model, the dynamic factor will be

           $$
              \text{dynamic factor} = |a v|,
           $$
        where $a$ is the acceleration (running-average of the finite-differences
        of velocity), and $v$ is the velocity, i.e. the highest-order derivative
        available in the CV model.

        Args:
            vec_x: State vector.
            derivatives: Array of derivatives.
        """
        is_mult = self.pn_meta.mult_by_last_derivative
        for i, ((o, s, e), der) in enumerate(zip(self.gen_x.gen_loop(), derivatives)):
            last_var = vec_x[e - 1]
            self.dynamic_factors[i] = der * last_var if (o > 1 and is_mult) else der
        self.dynamic_factors *= self.variance_factor
        np.fabs(self.dynamic_factors, out=self.dynamic_factors)

    def fill_proc_cov(self, pre: NdKkfPrecursors, vec_x: np.ndarray, cov_xx: np.ndarray) -> None:
        """
        Fills the process noise covariance matrix.

        Args:
            pre: Precursor data with 1D white-noise matrices computed for a given time step.
            vec_x: State vector, posterior state vector in practice.
            cov_xx: The process-noise covariance matrix to be filled.
        """
        self.gather_last_vars(vec_x, self.tmp_last_vars)
        self.der_mixer.compute(pre.last_dt, self.tmp_last_vars)
        self.compute_dyn_factors(vec_x, self.der_mixer.derivatives)
        self.gen_x.fill_q_mat(pre, self.dynamic_factors, cov_xx)

    def save_values(self, vec_x: np.ndarray) -> None:
        """
        Saves the current state vector values for future computations.

        Args:
            vec_x: Input state vector, predicted or prior state in practice.
        """
        self.gather_last_vars(vec_x, self.der_mixer.values)
