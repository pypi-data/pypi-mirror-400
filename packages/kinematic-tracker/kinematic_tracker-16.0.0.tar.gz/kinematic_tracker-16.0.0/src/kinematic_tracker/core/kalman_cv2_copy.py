"""."""

from cv2 import CV_64F, KalmanFilter


def get_copy(kf_in: KalmanFilter) -> KalmanFilter:
    """."""
    nz, nx = kf_in.measurementMatrix.shape
    kf = KalmanFilter(nx, nz, 0, CV_64F)
    kf.measurementMatrix = kf_in.measurementMatrix.copy()
    kf.measurementNoiseCov = kf_in.measurementNoiseCov.copy()
    kf.transitionMatrix = kf_in.transitionMatrix.copy()
    kf.processNoiseCov = kf_in.processNoiseCov.copy()
    kf.errorCovPost = kf_in.errorCovPost.copy()
    kf.errorCovPre = kf_in.errorCovPre.copy()
    kf.statePost = kf_in.statePost.copy()
    kf.statePre = kf_in.statePre.copy()
    kf.gain = kf_in.gain.copy()
    return kf
