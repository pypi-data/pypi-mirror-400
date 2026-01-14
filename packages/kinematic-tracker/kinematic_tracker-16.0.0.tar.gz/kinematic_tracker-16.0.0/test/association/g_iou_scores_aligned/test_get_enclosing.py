"""."""

import pytest

from kinematic_tracker.association.g_iou_scores_aligned import GIoUAux


def test_get_enclosing(
    giou_aux: GIoUAux,
    disjoint_xyz: GIoUAux,
    disjoint_x: GIoUAux,
    disjoint_xy: GIoUAux,
    joint_xy: GIoUAux,
) -> None:
    """."""
    assert giou_aux.get_enclosing(giou_aux) == pytest.approx(120.0)
    assert giou_aux.get_enclosing(joint_xy) == pytest.approx(180.0)
    assert joint_xy.get_enclosing(giou_aux) == pytest.approx(180.0)
    assert giou_aux.get_enclosing(disjoint_x) == pytest.approx(420.0)
    assert disjoint_x.get_enclosing(giou_aux) == pytest.approx(420.0)
    assert giou_aux.get_enclosing(disjoint_xy) == pytest.approx(1260.0)
    assert giou_aux.get_enclosing(disjoint_xyz) == pytest.approx(3360.0)
