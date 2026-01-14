"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.proc_noise.nd_kkf_white_noise_fd import NdKkfWhiteNoiseFd


def test_fill_proc_cov(wn_fd: NdKkfWhiteNoiseFd, pre: NdKkfPrecursors) -> None:
    """."""
    vec_x = np.linspace(1.0, 8.0, num=8)
    wn_fd.save_values(vec_x)
    pre.compute(9.0)
    cov_xx = 1.3 * np.ones((8, 8))
    wn_fd.fill_proc_cov(pre, 10.0 * vec_x, cov_xx)
    assert wn_fd.der_mixer.last_mix_weight == pytest.approx(0.0)
    assert wn_fd.der_mixer.counter == 1
    assert wn_fd.der_mixer.derivatives == pytest.approx([2.0, 4.0, 6.0, 7.0, 8.0])
    # fmt: off
    ref = [
        [9720.0, 1620.0,     1.3,    1.3,     1.3,     1.3,  1.3,  1.3],
        [1620.0,  360.0,     1.3,    1.3,     1.3,     1.3,  1.3,  1.3],
        [   1.3,    1.3, 38880.0, 6480.0,     1.3,     1.3,  1.3,  1.3],
        [   1.3,    1.3,  6480.0, 1440.0,     1.3,     1.3,  1.3,  1.3],
        [   1.3,    1.3,     1.3,    1.3, 87480.0, 14580.0,  1.3,  1.3],
        [   1.3,    1.3,     1.3,    1.3, 14580.0,  3240.0,  1.3,  1.3],
        [   1.3,    1.3,     1.3,    1.3,     1.3,     1.3, 63.0,  1.3],
        [   1.3,    1.3,     1.3,    1.3,     1.3,     1.3,  1.3, 72.0]
    ]
    # fmt: on
    assert cov_xx == pytest.approx(np.array(ref))
