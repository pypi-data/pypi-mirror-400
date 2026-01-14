"""."""

from kinematic_tracker.tracker.kkf import NdKkf


def test_nd_kkf_repr(kkf_wn: NdKkf) -> None:
    """."""
    ref = """NdKkf(NdKkfWhiteNoiseFd(ProcNoiseMeta(ProcNoiseKind.FINITE_DIFF
    factor 1.0
    mix_weight 0.75
    mult_by_last_derivative True
    is_dynamic_mixing True)))"""
    assert repr(kkf_wn) == ref
