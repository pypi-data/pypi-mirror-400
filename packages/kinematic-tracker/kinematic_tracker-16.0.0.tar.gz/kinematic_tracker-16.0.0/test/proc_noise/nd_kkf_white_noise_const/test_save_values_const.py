"""."""

import numpy as np

from kinematic_tracker.proc_noise.nd_kkf_white_noise_const import NdKkfWhiteNoiseConst


def test_nd_kkf_white_noise_const_save_values(wn_const: NdKkfWhiteNoiseConst) -> None:
    """."""
    wn_const.save_values(np.empty(0))
