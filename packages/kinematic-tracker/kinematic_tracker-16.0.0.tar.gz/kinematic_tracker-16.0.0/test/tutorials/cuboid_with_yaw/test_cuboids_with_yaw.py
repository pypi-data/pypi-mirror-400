"""."""

from pathlib import Path

import numpy as np

from kinematic_tracker.nd.derivative_sorted import DerivativeSorted
from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_cuboids_with_yaw() -> None:
    """."""

    det_path = Path(__file__).parent / 'annotation_task_1_757.csv'
    tss_l = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=(0,), dtype=int)
    ids_l = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=(1,), dtype=int)
    det_ly = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=range(2, 9))
    stamps = np.unique(tss_l)
    # Detections are prepared above.

    tracker = NdKkfTracker([3, 1, 1], [3, 3, 2])
    tracker.set_ind_pos_size((0, 1, 2, 3, 4, 5))
    tracker.set_measurement_std_dev(0, 0.1)  # define std dev for coordinates and...
    tracker.set_measurement_std_dev(1, 0.02)  # ... for dimensions of cuboids
    tracker.set_measurement_std_dev(2, 0.2)  # ... for yaw of cuboids
    # Tracker is initialized, tracking will be run below.

    der_sorted = DerivativeSorted(tracker.gen_xz.gen_x)
    buf_x = np.zeros((der_sorted.get_num_x(), 1))
    print()
    np.set_printoptions(linewidth=200, precision=4)
    for stamp_num, stamp_ns in enumerate(stamps):
        stamp_ns: int
        mask = tss_l == stamp_ns
        det_ry, ids_r = det_ly[mask], ids_l[mask]
        det_rz = convert_cartesian_yaw(det_ry)
        tracker.advance(stamp_ns, det_rz, ids_r)
        print(stamp_num)
        for track in tracker.tracks:
            der_sorted.convert_vec(track.kkf.kalman_filter.statePost, buf_x)
            print('  ', buf_x.T)  # tracking state in a derivative-sorted order:
            # px,py,py,dx,dy,dz,Psi_x,Psi_y,vx,vy,vz,ax,ay,ax


def convert_cartesian_yaw(det_ry: np.ndarray) -> np.ndarray[tuple[int, 8]]:
    """Linearize vectors with yaw angle.

    Essentially take the measurements
        y^T = (px, py, py, dx, dy, dz, Psi)
    and produce
        z^T = (px, py, py, dx, dy, dz, cos(Psi), sin(Psi))
    """
    assert det_ry.shape[1] == 7
    num_reports = len(det_ry)
    det_rz = np.zeros((num_reports, 8))
    det_rz[:, :6] = det_ry[:, :6]
    yaw_r = det_ry[:, 6]
    det_rz[:, 6] = np.cos(yaw_r)
    det_rz[:, 7] = np.sin(yaw_r)
    return det_rz
