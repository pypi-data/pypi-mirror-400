"""."""

import pytest

from kinematic_tracker.proc_noise.nd_kkf_white_noise_fd import NdKkfWhiteNoiseFd


def test_nd_kkf_proc_noise_repr(wn_fd: NdKkfWhiteNoiseFd) -> None:
    """."""
    ref = """NdKkfWhiteNoiseFd(ProcNoiseMeta(ProcNoiseKind.FINITE_DIFF
    factor 1.0
    mix_weight 0.75
    mult_by_last_derivative True
    is_dynamic_mixing True))"""
    assert repr(wn_fd) == ref
    assert wn_fd.der_mixer.values == pytest.approx([2, 4, 6, 7, 8])
