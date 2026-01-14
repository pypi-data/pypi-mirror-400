"""."""

import numpy as np
import pytest

from kinematic_tracker.proc_noise.nd_kkf_white_noise_fd import NdKkfWhiteNoiseFd


def test_compute_dyn_factors(wn_fd: NdKkfWhiteNoiseFd) -> None:
    """."""
    vec_x = np.linspace(1.0, 8.0, num=8)
    num_d = wn_fd.gen_x.num_d
    derivatives = np.linspace(9.0, 9.0 + num_d - 1, num=num_d)
    wn_fd.compute_dyn_factors(vec_x, derivatives)
    assert wn_fd.dynamic_factors == pytest.approx([18.0, 40.0, 66.0, 12.0, 13.0])

    wn_fd.pn_meta.mult_by_last_derivative = False
    wn_fd.compute_dyn_factors(vec_x, derivatives)
    assert wn_fd.dynamic_factors == pytest.approx([9.0, 10.0, 11.0, 12.0, 13.0])


def test_compute_dyn_factors_multiplied_by_variance_factor(wn_fd: NdKkfWhiteNoiseFd) -> None:
    """."""
    vec_x = np.linspace(1.0, 8.0, num=8)
    num_d = wn_fd.gen_x.num_d
    derivatives = np.linspace(9.0, 9.0 + num_d - 1, num=num_d)
    wn_fd.variance_factor = 2.0
    wn_fd.compute_dyn_factors(vec_x, derivatives)
    assert wn_fd.dynamic_factors == pytest.approx([36.0, 80.0, 132.0, 24.0, 26.0])
