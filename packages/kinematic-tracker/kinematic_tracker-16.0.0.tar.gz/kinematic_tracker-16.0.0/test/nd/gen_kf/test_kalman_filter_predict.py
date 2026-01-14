"""."""

import numpy as np
import pytest

from cv2 import KalmanFilter


def test_kf_predict(kf_predicted: KalmanFilter) -> None:
    """."""
    x_ref = np.array([[7.0], [2.0], [15.0], [4.0], [5.0]])
    assert kf_predicted.statePre == pytest.approx(x_ref)
    assert kf_predicted.statePost == pytest.approx(x_ref)
    p_ref = np.array(
        [
            [957.0, 327.0, 0.0, 0.0, 0.0],
            [327.0, 118.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1911.0, 654.0, 0.0],
            [0.0, 0.0, 654.0, 236.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 57.0],
        ]
    )
    assert kf_predicted.errorCovPre == pytest.approx(p_ref)
    assert kf_predicted.errorCovPost == pytest.approx(p_ref)
    assert id(kf_predicted.errorCovPost) != id(kf_predicted.errorCovPre)
