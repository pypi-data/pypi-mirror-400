"""."""

import numpy as np

from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.proc_noise.kind import ProcNoiseKind
from kinematic_tracker.proc_noise.meta import get_proc_noise_meta
from kinematic_tracker.proc_noise.nd_kkf_proc_noise_factory import get_proc_noise
from kinematic_tracker.proc_noise.nd_kkf_white_noise_const import NdKkfWhiteNoiseConst


def test_get_proc_noise_white_noise_const(gen_x: NdKkfMatGenX) -> None:
    """."""
    vec_x = np.linspace(1.0, 8.0, num=8)
    pn_meta_const = get_proc_noise_meta(ProcNoiseKind.CONST, 0.5, 0.5, True, True)
    pn = get_proc_noise(gen_x, pn_meta_const, vec_x)
    assert isinstance(pn, NdKkfWhiteNoiseConst)
