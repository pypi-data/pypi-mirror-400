"""."""

import copy

import numpy as np
import pytest

from kinematic_tracker.association.g_iou_scores_aligned import GIoUAux


@pytest.fixture
def giou_aux() -> GIoUAux:
    """."""
    aux = GIoUAux()
    aux.set_vec_z(np.linspace(1.0, 6.0, num=6).reshape(6, 1))
    return aux


@pytest.fixture
def disjoint_xyz(giou_aux: GIoUAux) -> GIoUAux:
    """."""
    aux = copy.deepcopy(giou_aux)
    aux.corners += 10.0
    return aux


@pytest.fixture
def disjoint_x(giou_aux: GIoUAux) -> GIoUAux:
    """."""
    aux = copy.deepcopy(giou_aux)
    aux.corners[:, 0] += 10.0
    return aux


@pytest.fixture
def disjoint_xy(giou_aux: GIoUAux) -> GIoUAux:
    """."""
    aux = copy.deepcopy(giou_aux)
    aux.corners[:, 0:2] += 10.0
    return aux


@pytest.fixture
def joint_xy(giou_aux: GIoUAux) -> GIoUAux:
    """."""
    aux = copy.deepcopy(giou_aux)
    aux.corners[:, 0:2] += 1.0
    return aux
