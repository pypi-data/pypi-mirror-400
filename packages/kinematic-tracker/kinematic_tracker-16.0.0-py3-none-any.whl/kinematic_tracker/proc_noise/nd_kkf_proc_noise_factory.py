"""."""

import numpy as np

from kinematic_tracker.nd.gen_x import NdKkfMatGenX

from .meta import ProcNoiseKind, ProcNoiseMeta
from .nd_kkf_dia_noise import NdKkfDiaNoise
from .nd_kkf_white_noise_const import NdKkfWhiteNoiseConst
from .nd_kkf_white_noise_fd import NdKkfWhiteNoiseFd


TT_PN = NdKkfWhiteNoiseFd | NdKkfDiaNoise | NdKkfWhiteNoiseConst


def get_proc_noise(gen_x: NdKkfMatGenX, pn_meta: ProcNoiseMeta, ini_vec_x: np.ndarray) -> TT_PN:
    """."""
    kind = pn_meta.noise_kind
    if kind == ProcNoiseKind.CONST:
        pn = NdKkfWhiteNoiseConst(gen_x, pn_meta.factor)
    elif kind == ProcNoiseKind.FINITE_DIFF:
        pn = NdKkfWhiteNoiseFd(gen_x, pn_meta, ini_vec_x)
    elif kind == ProcNoiseKind.DIAGONAL:
        pn = NdKkfDiaNoise(pn_meta.factor)
    else:
        raise ValueError
    return pn
