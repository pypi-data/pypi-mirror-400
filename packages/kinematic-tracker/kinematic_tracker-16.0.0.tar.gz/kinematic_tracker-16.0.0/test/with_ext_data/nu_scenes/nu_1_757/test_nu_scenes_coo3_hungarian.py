"""."""

from pathlib import Path

from binary_classification_ratios import BinaryClassificationRatios

from kinematic_tracker.tracker.tracker import NdKkfTracker
from test.with_ext_data.conftest import AlignedCuboidDetectionsFromCsv


def test_nu_scenes_coo3_hungarian(tracker: NdKkfTracker) -> None:
    """."""
    tracker.set_association_method('hungarian')
    det_path = Path(__file__).parent / 'share/fusion-lab-detections-sensor-1.csv'
    det_gen = AlignedCuboidDetectionsFromCsv(str(det_path))
    tracking_history = det_gen.run_tracking(tracker)

    association_quality = det_gen.analyse_association(tracking_history)
    conf_mat_dct = association_quality.get_confusion_matrix()
    ratios = BinaryClassificationRatios(**conf_mat_dct)
    ratios.assert_min(0.9964, 0.998, 0.998)
