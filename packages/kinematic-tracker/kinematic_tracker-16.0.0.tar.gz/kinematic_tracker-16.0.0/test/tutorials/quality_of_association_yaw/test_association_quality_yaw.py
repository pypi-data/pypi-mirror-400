"""."""

from pathlib import Path

import numpy as np

from association_quality_clavia import AssociationQuality
from binary_classification_ratios import BinaryClassificationRatios

from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_quality_of_association_yaw() -> None:
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

    np.set_printoptions(linewidth=200, precision=4)
    classifier = AssociationQuality()  # Classifier into TP, FP, FN, TN
    for stamp_num, stamp_ns in enumerate(stamps):
        stamp_ns: int
        mask = tss_l == stamp_ns
        det_ry, ids_r = det_ly[mask], ids_l[mask]
        det_rz = convert_cartesian_yaw(det_ry)
        tracker.advance(stamp_ns, det_rz, ids_r)
        for track in tracker.tracks:
            is_det_supplied = track.ann_id in ids_r
            classifier.classify(track.ann_id, track.upd_id, is_det_supplied)

    confusion_matrix_dct = classifier.get_confusion_matrix()
    ratios = BinaryClassificationRatios(**confusion_matrix_dct)
    print(ratios.get_summary())
    ratios.assert_min(0.8569, 0.995, 0.8492)


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
