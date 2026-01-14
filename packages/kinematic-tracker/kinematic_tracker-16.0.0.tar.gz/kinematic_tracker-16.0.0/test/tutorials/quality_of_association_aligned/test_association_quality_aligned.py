"""."""

from pathlib import Path

import numpy as np

from association_quality_clavia import AssociationQuality
from binary_classification_ratios import BinaryClassificationRatios

from kinematic_tracker.association.association_metric import AssociationMetric
from kinematic_tracker.tracker.tracker import NdKkfTracker


def test_association_quality() -> None:
    """."""

    det_path = Path(__file__).parent / 'detections.csv'
    tss_l = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=(0,), dtype=int)
    ids_l = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=(1,), dtype=int)
    det_lz = np.genfromtxt(det_path, skip_header=1, delimiter=',', usecols=range(2, 8))
    stamps = np.unique(tss_l)
    # Detections are prepared above.

    tracker = NdKkfTracker([3, 1], [3, 3])
    tracker.set_association_metric(AssociationMetric.GIOU.value)
    tracker.set_measurement_std_dev(0, 0.05)  # define std dev for coordinates and...
    tracker.set_measurement_std_dev(1, 0.02)  # ... for dimensions of cuboids
    # Tracker is initialized, tracking will be run below.

    classifier = AssociationQuality()  # Classifier into TP, FP, FN, TN
    for stamp_ns in stamps:
        mask = tss_l == stamp_ns
        det_rz, ids_r = det_lz[mask], ids_l[mask]
        tracker.advance(stamp_ns, det_rz, ids_r)
        for track in tracker.tracks:
            is_det_supplied = track.ann_id in ids_r
            classifier.classify(track.ann_id, track.upd_id, is_det_supplied)

    conf_mat_dct = classifier.get_confusion_matrix()
    ratios = BinaryClassificationRatios(**conf_mat_dct)
    print(ratios.get_summary())
    ratios.assert_min(0.8918, 0.9939, 0.8878)
