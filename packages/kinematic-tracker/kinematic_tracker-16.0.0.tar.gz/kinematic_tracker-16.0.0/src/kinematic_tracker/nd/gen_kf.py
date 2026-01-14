"""Generator of the Kalman filters.

The object facilitates generation of Kalman filters with common (shared)
transition. Sharing of the fundamental matrix across a set of Kalman filters
should improve the performance when filling the matrices. Simultaneously,
sharing of fundamental matrices reduces the memory footprint.
"""

import numpy as np

from cv2 import CV_64F, KalmanFilter

from .gen_xz import NdKkfMatGenXz


class NdKkfGenKf:
    """Generator of the Kalman filters."""

    def __init__(self, f_mat: np.ndarray) -> None:
        """Constructor.

        The object will keep the fundamental (transition) matrix and initialize the Kalman filters
        using this fundamental matrix. The fundamental matrices in Kalman filters produced by this
        generator *share the same memory*.

        Similarly, the measurement matrix (H matrix) will be taken from the measurement
        matrices generator and will share the same memory.

        Args:
            f_mat: the fundamental (transition) matrix.
        """
        self.f_mat = f_mat

    def get_kf(
        self, gen_xz: NdKkfMatGenXz, vec_z: np.ndarray, cov_zz: np.ndarray, ini_der_vars: np.ndarray
    ) -> KalmanFilter:
        """Get new Kalman filter object.

        Args:
            gen_xz: generator of Kalman matrices.
            vec_z: the measurement vector used to (partially) initialize the state vector x.
                   The derivatives of the state vector missing in the measurement will be zeros.
            cov_zz: the measurement covariance matrix used to (partially) initialize
                    the state error covariance (P matrix). The derivative parts of the
                    error covariance will be diagonal initialized with derivative variances
                    (see `ini_der_vars`)
            ini_der_vars:
                    The variances for all-order derivative parts in the initial error
                    covariances.

        For example, given a composed ND state with orders_x = [2, 1], dimensions [2, 2]
        and measurement orders orders_z = [1, 1], the state vector x will be 6-dimensional:

           x^T = (px, vx, py, vy, dx, dy)

        while the measurement vector z will be 4-dimensional

           z^T = (px, py, dx, dy)

        The given the measurement vector z^T = (px, py, dx, dy), the Kalman filter will be
        initialized with (initial) state vector x^T = (px, 0, py, 0, dx, dy).

        Similarly, given a measurement covariance

                 pp_xx  pp_xy  pd_xx  pd_xy
           R =   pp_xy  pp_yy  pd_yx  pd_yy
                 pd_xx  pd_yx  dd_xx  dd_xy
                 pd_xy  pd_yy  dd_xy  dd_yy

        and the initial derivative variances

            v^T  = (100, 200, 300, 400)

        The initial state error covariance will be

                  pp_xx  0      pp_xy  0      pd_xx  pd_xy
                  0      100    0      0      0      0
           P =    pp_xy  0      pp_yy  0      pd_yx  pd_yy
                  0      0      0      200    0      0
                  pd_xx  0      pd_yx  0      dd_xx  dd_xy
                  pd_xy  0      pd_yy  0      dd_xy  dd_yy
        """
        assert ini_der_vars.shape == (gen_xz.gen_x.num_d,)
        nx = gen_xz.gen_x.num_x
        kf = KalmanFilter(nx, gen_xz.num_z, 0, CV_64F)
        kf.measurementNoiseCov = cov_zz.copy()
        kf.measurementMatrix = gen_xz.h_mat
        kf.processNoiseCov = np.zeros((nx, nx))
        vec_x = np.zeros((nx, 1))
        gen_xz.fill_vec_x(vec_z, vec_x[:, 0])
        kf.statePre = vec_x
        kf.statePost = vec_x.copy()
        kf.errorCovPre = np.zeros((nx, nx))
        for (o, s, e), ini_der_var in zip(gen_xz.gen_x.gen_loop(), ini_der_vars):
            kf.errorCovPre[s:e, s:e] = ini_der_var * np.eye(o)
        gen_xz.fill_mat_xx(cov_zz, kf.errorCovPre)
        kf.errorCovPost = kf.errorCovPre.copy()
        kf.transitionMatrix = self.f_mat
        return kf
