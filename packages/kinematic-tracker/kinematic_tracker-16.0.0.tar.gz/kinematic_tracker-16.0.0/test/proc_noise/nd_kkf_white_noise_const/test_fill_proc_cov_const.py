"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.precursors import NdKkfPrecursors
from kinematic_tracker.proc_noise.nd_kkf_white_noise_const import NdKkfWhiteNoiseConst


def test_fill_proc_cov_const(wn_const: NdKkfWhiteNoiseConst, pre: NdKkfPrecursors) -> None:
    """."""
    cov_xx = 1.3 * np.ones((8, 8))
    pre.compute(9.0)
    wn_const.fill_proc_cov(pre, np.empty(8), cov_xx)
    # fmt: off
    ref = [
        [1379.754, 229.959,      1.3,     1.3,      1.3,     1.3,    1.3,  1.3],
        [ 229.959,  51.102,      1.3,     1.3,      1.3,     1.3,    1.3,  1.3],
        [     1.3,     1.3, 1379.754, 229.959,      1.3,     1.3,    1.3,  1.3],
        [     1.3,     1.3,  229.959,  51.102,      1.3,     1.3,    1.3,  1.3],
        [     1.3,     1.3,      1.3,     1.3, 1379.754, 229.959,    1.3,  1.3],
        [     1.3,     1.3,      1.3,     1.3,  229.959,  51.102,    1.3,  1.3],
        [     1.3,     1.3,      1.3,     1.3,      1.3,     1.3, 51.102,  1.3],
        [     1.3,     1.3,      1.3,     1.3,      1.3,     1.3,    1.3, 51.102]
    ]
    # fmt: on
    assert cov_xx == pytest.approx(np.array(ref))
