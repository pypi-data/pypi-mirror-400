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
    assert giou_aux.get_g_iou_diff(giou_aux) == pytest.approx(1.0)
    assert giou_aux.get_g_iou_diff(joint_xy) == pytest.approx(0.3619047619047619)
    assert joint_xy.get_g_iou_diff(giou_aux) == pytest.approx(0.3619047619047619)
    assert giou_aux.get_g_iou_diff(disjoint_x) == pytest.approx(-0.42857142857142855)
    assert disjoint_x.get_g_iou_diff(giou_aux) == pytest.approx(-0.42857142857142855)
    assert giou_aux.get_g_iou_diff(disjoint_xy) == pytest.approx(-0.8095238095238095)
    assert giou_aux.get_g_iou_diff(disjoint_xyz) == pytest.approx(-0.9285714285714286)
