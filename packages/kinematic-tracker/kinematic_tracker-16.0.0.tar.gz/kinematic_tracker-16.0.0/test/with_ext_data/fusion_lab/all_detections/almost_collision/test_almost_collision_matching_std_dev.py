"""."""

from pathlib import Path

from binary_classification_ratios import BinaryClassificationRatios

from kinematic_tracker.tracker.tracker import NdKkfTracker
from test.with_ext_data.conftest import AlignedCuboidDetectionsFromCsv, AlignedCuboidMotionFromCsv


def test_almost_collision_matching_std_dev(tracker: NdKkfTracker) -> None:
    """Track two almost colliding objects."""
    det_path = Path(__file__).parent / 'share/fusion-lab-detections-sensor-1.csv'
    det_gen = AlignedCuboidDetectionsFromCsv(str(det_path))
    tracking_history = det_gen.run_tracking(tracker)

    association_quality = det_gen.analyse_association(tracking_history)
    conf_mat_dct = association_quality.get_confusion_matrix()
    ratios = BinaryClassificationRatios(**conf_mat_dct)
    ratios.assert_min(0.93333, 1.0, 0.93333)

    motion_path = Path(__file__).parent / 'share/fusion-lab-motion-sensor-1.csv'
    ref_aux = AlignedCuboidMotionFromCsv(str(motion_path))
    assert ref_aux.compute_ate(tracking_history) < 0.75
