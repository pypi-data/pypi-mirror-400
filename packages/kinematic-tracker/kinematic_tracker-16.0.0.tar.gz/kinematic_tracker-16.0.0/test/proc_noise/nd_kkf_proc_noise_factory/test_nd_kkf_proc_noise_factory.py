"""."""

import numpy as np
import pytest

from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.proc_noise.meta import ProcNoiseKind, ProcNoiseMeta
from kinematic_tracker.proc_noise.nd_kkf_dia_noise import NdKkfDiaNoise
from kinematic_tracker.proc_noise.nd_kkf_proc_noise_factory import get_proc_noise
from kinematic_tracker.proc_noise.nd_kkf_white_noise_fd import NdKkfWhiteNoiseFd


def test_get_proc_noise_white_noise_fd(gen_x: NdKkfMatGenX, pn_meta_fd: ProcNoiseMeta) -> None:
    """."""
    vec_x = np.linspace(1.0, 8.0, num=8)
    pn = get_proc_noise(gen_x, pn_meta_fd, vec_x)
    assert isinstance(pn, NdKkfWhiteNoiseFd)


def test_get_dia_noise(gen_x: NdKkfMatGenX, pn_meta_dia: ProcNoiseMeta) -> None:
    """."""
    vec_x = np.linspace(1.0, 8.0, num=8)
    pn = get_proc_noise(gen_x, pn_meta_dia, vec_x)
    assert isinstance(pn, NdKkfDiaNoise)


def test_exceptions(gen_x: NdKkfMatGenX, pn_meta_dia: ProcNoiseMeta) -> None:
    """."""
    pn_meta_dia.noise_kind = ProcNoiseKind.UNKNOWN
    with pytest.raises(ValueError):
        get_proc_noise(gen_x, pn_meta_dia, np.linspace(1.0, 8.0, num=8))
