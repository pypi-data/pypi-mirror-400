"""."""

import pytest

from kinematic_tracker.association.g_iou_scores_aligned import GIoUAux


def test_get_giou(
    giou_aux: GIoUAux,
    disjoint_xyz: GIoUAux,
    disjoint_x: GIoUAux,
    disjoint_xy: GIoUAux,
    joint_xy: GIoUAux,
) -> None:
    """."""
    assert giou_aux.get_g_iou(giou_aux) == pytest.approx(1.0)
    assert giou_aux.get_g_iou(joint_xy) == pytest.approx(0.680952380952381)
    assert joint_xy.get_g_iou(giou_aux) == pytest.approx(0.680952380952381)
    assert giou_aux.get_g_iou(disjoint_x) == pytest.approx(0.2857142857142857)
    assert disjoint_x.get_g_iou(giou_aux) == pytest.approx(0.2857142857142857)
    assert giou_aux.get_g_iou(disjoint_xy) == pytest.approx(0.09523809523809523)
    assert giou_aux.get_g_iou(disjoint_xyz) == pytest.approx(0.0357142857142857)
