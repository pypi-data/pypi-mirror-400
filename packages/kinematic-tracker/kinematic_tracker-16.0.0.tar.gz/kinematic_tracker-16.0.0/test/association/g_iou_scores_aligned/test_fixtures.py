"""."""

import numpy as np
import pytest

from kinematic_tracker.association.g_iou_scores_aligned import GIoUAux


def test_fixtures(
    giou_aux: GIoUAux,
    disjoint_xyz: GIoUAux,
    disjoint_x: GIoUAux,
    disjoint_xy: GIoUAux,
    joint_xy: GIoUAux,
) -> None:
    """."""
    assert giou_aux.volume == pytest.approx(120.0)
    assert giou_aux.corners == pytest.approx(np.array([[-1.0, -0.5, 0.0], [3.0, 4.5, 6.0]]))
    assert disjoint_xyz.corners == pytest.approx(np.array([[9.0, 9.5, 10.0], [13.0, 14.5, 16.0]]))
    assert disjoint_x.corners == pytest.approx(np.array([[9.0, -0.5, 0.0], [13.0, 4.5, 6.0]]))
    assert disjoint_xy.corners == pytest.approx(np.array([[9.0, 9.5, 0.0], [13.0, 14.5, 6.0]]))
    assert joint_xy.corners == pytest.approx(np.array([[0.0, 0.5, 0.0], [4.0, 5.5, 6.0]]))
