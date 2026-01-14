"""."""

import pytest

from kinematic_tracker.association.g_iou_scores_aligned import GIoUAux


def test_get_intersection(
    giou_aux: GIoUAux,
    disjoint_xyz: GIoUAux,
    disjoint_x: GIoUAux,
    disjoint_xy: GIoUAux,
    joint_xy: GIoUAux,
) -> None:
    """."""
    assert giou_aux.get_intersection(giou_aux) == pytest.approx(120.0)
    assert giou_aux.get_intersection(joint_xy) == pytest.approx(72.0)
    assert joint_xy.get_intersection(giou_aux) == pytest.approx(72.0)
    assert giou_aux.get_intersection(disjoint_x) == pytest.approx(0.0)
    assert disjoint_x.get_intersection(giou_aux) == pytest.approx(0.0)
    assert giou_aux.get_intersection(disjoint_xy) == pytest.approx(0.0)
