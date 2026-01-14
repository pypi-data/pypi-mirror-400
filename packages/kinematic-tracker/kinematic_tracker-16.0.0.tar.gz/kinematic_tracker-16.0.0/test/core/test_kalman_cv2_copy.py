"""."""

from cv2 import CV_64F, KalmanFilter

from kinematic_tracker.core.kalman_cv2_copy import get_copy


def test_kalman_cv2_copy() -> None:
    """."""
    kf = KalmanFilter(8, 5, 0, CV_64F)
    cp = get_copy(kf)
    assert cp.measurementMatrix.shape == (5, 8)
    assert cp.measurementMatrix.dtype == 'float64'
    assert cp.gain.shape == (8, 5)
    assert id(cp.statePost) != id(kf.statePost)
