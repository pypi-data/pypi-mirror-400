"""."""

import numpy as np

from kinematic_tracker.proc_noise.nd_kkf_dia_noise import NdKkfDiaNoise


def test_nd_kkf_dia_noise_save_values(dia_n: NdKkfDiaNoise) -> None:
    """."""
    dia_n.save_values(np.empty(0))
