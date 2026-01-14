"""."""

import numpy as np
import pytest

from cv2 import KalmanFilter


def test_kalman_filter_correct(kf_predicted: KalmanFilter) -> None:
    """."""
    vec_z = np.linspace(2.0, 4.0, num=3).reshape((3, 1))
    kf_predicted.correct(vec_z)
    x_pre = np.array([[7.0], [2.0], [15.0], [4.0], [5.0]])
    x_post = np.array([[2.015625], [0.296875], [3.0188087774295], [-0.100313479624], [4.05]])
    assert kf_predicted.statePre == pytest.approx(x_pre)
    assert kf_predicted.statePost == pytest.approx(x_post)
    p_pre = np.array(
        [
            [957.0, 327.0, 0.0, 0.0, 0.0],
            [327.0, 118.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1911.0, 654.0, 0.0],
            [0.0, 0.0, 654.0, 236.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 57.0],
        ]
    )
    p_post = np.array(
        [
            [2.9906250000000227, 1.0218750000000227, 0.0, 0.0, 0.0],
            [1.021874999999966, 6.615624999999994, 0.0, 0.0, 0.0],
            [0.0, 0.0, 2.995297805642622, 1.0250783699059411, 0.0],
            [0.0, 0.0, 1.0250783699059411, 12.532915360501562, 0.0],
            [0.0, 0.0, 0.0, 0.0, 2.8500000000000014],
        ]
    )
    assert kf_predicted.errorCovPre == pytest.approx(p_pre)
    assert kf_predicted.errorCovPost == pytest.approx(p_post)
    k_ref = np.array(
        [
            [0.996875, 0.0, 0.0],
            [0.340625, 0.0, 0.0],
            [0.0, 0.9984326018808778, 0.0],
            [0.0, 0.34169278996865204, 0.0],
            [0.0, 0.0, 0.95],
        ]
    )
    assert kf_predicted.gain == pytest.approx(k_ref)
