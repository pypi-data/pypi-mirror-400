"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.derivative_sorted import DerivativeSorted


DS_1_BASED_RANGE = 1.0, 4.0, 7.0, 8.0, 2.0, 5.0, 3.0, 6.0


def test_convert_vector(der_sorted: DerivativeSorted) -> None:
    """."""
    vec_nd = np.linspace(1.0, 8.0, num=8)
    vec_ds = np.zeros(8)
    der_sorted.convert_vec(vec_nd, vec_ds)
    assert vec_ds == pytest.approx(DS_1_BASED_RANGE)


def test_convert_vectors(der_sorted: DerivativeSorted) -> None:
    """."""
    vec_sx = [np.linspace(1.0, 8.0, num=8), np.linspace(9.0, 16.0, num=8)]
    out_sx = np.zeros((2, 8))
    der_sorted.convert_vectors(vec_sx, out_sx)
    ref_0x = np.array(DS_1_BASED_RANGE)
    assert out_sx[0] == pytest.approx(ref_0x)
    assert out_sx[1] == pytest.approx(ref_0x + 8.0)


def test_convert_matrix(der_sorted: DerivativeSorted) -> None:
    """."""
    mat_nd = np.array(
        [
            [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8],
            [2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8],
            [3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8],
            [4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8],
            [5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8],
            [6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8],
            [7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8],
            [8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8],
        ]
    )
    mat_cu = np.zeros((8, 8))
    ref_cu = np.array(
        [
            [1.1, 1.4, 1.7, 1.8, 1.2, 1.5, 1.3, 1.6],
            [4.1, 4.4, 4.7, 4.8, 4.2, 4.5, 4.3, 4.6],
            [7.1, 7.4, 7.7, 7.8, 7.2, 7.5, 7.3, 7.6],
            [8.1, 8.4, 8.7, 8.8, 8.2, 8.5, 8.3, 8.6],
            [2.1, 2.4, 2.7, 2.8, 2.2, 2.5, 2.3, 2.6],
            [5.1, 5.4, 5.7, 5.8, 5.2, 5.5, 5.3, 5.6],
            [3.1, 3.4, 3.7, 3.8, 3.2, 3.5, 3.3, 3.6],
            [6.1, 6.4, 6.7, 6.8, 6.2, 6.5, 6.3, 6.6],
        ]
    )
    der_sorted.convert_mat(mat_nd, mat_cu)
    assert mat_cu == pytest.approx(ref_cu)
