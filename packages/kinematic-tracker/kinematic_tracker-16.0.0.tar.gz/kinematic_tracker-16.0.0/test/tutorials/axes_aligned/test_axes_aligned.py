"""."""

from pathlib import Path

import numpy as np

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_cuboids_aligned_with_cartesian_axes_read_from_csv() -> None:
    """."""

    det_path = Path(__file__).parent / 'detections.csv'
    tss_l = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=(0,), dtype=int)
    ids_l = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=(1,), dtype=int)
    det_lz = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=range(2, 8))
    stamps = np.unique(tss_l)
    # Detections are prepared above.

    tracker = NdKkfTracker([3, 1], [3, 3])
    tracker.set_measurement_std_dev(0, 0.1)  # define std dev for coordinates and...
    tracker.set_measurement_std_dev(1, 0.02)  # ... for dimensions of cuboids
    # Tracker is initialized, tracking will be run below.

    print()
    np.set_printoptions(linewidth=200, precision=4)
    for stamp_ns in stamps:
        mask = tss_l == stamp_ns
        det_rz, ids_r = det_lz[mask], ids_l[mask]
        tracker.advance(stamp_ns, det_rz, ids_r)
        for track in tracker.tracks:
            print(track.kkf.kalman_filter.statePost.T)  # result of tracking
            # Block-diagonal variable order: px,vx,ax,py,vy,ay,pz,vz,az,dx,dy,dz
    # Tracking is done.
