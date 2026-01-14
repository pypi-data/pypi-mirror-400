"""."""

import numpy as np
import pytest

from cv2 import KalmanFilter

from kinematic_tracker.nd.gen_kf import NdKkfGenKf
from kinematic_tracker.nd.gen_xz import NdKkfMatGenXz


def test_get_kf(gen_kf: NdKkfGenKf, gen_xz: NdKkfMatGenXz, kf: KalmanFilter) -> None:
    """."""
    assert kf.transitionMatrix == pytest.approx(np.zeros((5, 5)))
    assert id(kf.transitionMatrix) == id(gen_kf.f_mat)
    assert id(kf.measurementMatrix) == id(gen_xz.h_mat)

    assert kf.controlMatrix is None
    assert kf.measurementNoiseCov == pytest.approx(3.0 * np.eye(3))
    h_ref = [[1.0, 0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0, 1.0]]
    assert kf.measurementMatrix == pytest.approx(np.array(h_ref))
    assert kf.processNoiseCov == pytest.approx(np.zeros((5, 5)))
    p_ref = np.array(
        [
            [3.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 100.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 3.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 200.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 3.0],
        ]
    )
    assert kf.errorCovPre == pytest.approx(p_ref)
    assert kf.errorCovPost == pytest.approx(p_ref)
    x_ref = np.array([1.0, 0.0, 2.0, 0.0, 3.0]).reshape((5, 1))
    assert kf.statePre == pytest.approx(x_ref)
    assert kf.statePost == pytest.approx(x_ref)
