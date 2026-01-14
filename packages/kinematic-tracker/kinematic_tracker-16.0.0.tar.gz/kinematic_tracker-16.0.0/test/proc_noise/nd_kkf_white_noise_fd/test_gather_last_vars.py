"""."""

import numpy as np
import pytest

from kinematic_tracker.proc_noise.nd_kkf_white_noise_fd import NdKkfWhiteNoiseFd


def test_nd_kkf_proc_noise_gather_last_vars(wn_fd: NdKkfWhiteNoiseFd) -> None:
    """."""
    vec_x = np.linspace(1.0, 8.0, num=8)
    last_vars = -999 * np.ones(5)
    wn_fd.gather_last_vars(vec_x, last_vars)
    assert last_vars == pytest.approx([2, 4, 6, 7, 8])
