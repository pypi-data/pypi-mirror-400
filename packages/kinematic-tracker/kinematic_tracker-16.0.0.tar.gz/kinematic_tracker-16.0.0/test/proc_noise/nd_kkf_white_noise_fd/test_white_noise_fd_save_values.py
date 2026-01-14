"""."""

import numpy as np
import pytest

from kinematic_tracker.proc_noise.nd_kkf_white_noise_fd import NdKkfWhiteNoiseFd


def test_nd_kkf_proc_noise_save_values(wn_fd: NdKkfWhiteNoiseFd) -> None:
    """."""
    vec_x = np.linspace(1.0, 8.0, num=8)
    wn_fd.save_values(vec_x)
    assert wn_fd.der_mixer.values == pytest.approx([2, 4, 6, 7, 8])
