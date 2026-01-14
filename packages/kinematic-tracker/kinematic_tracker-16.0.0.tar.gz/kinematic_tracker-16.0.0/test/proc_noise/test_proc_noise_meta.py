"""."""

from kinematic_tracker.proc_noise.meta import ProcNoiseMeta


def test_proc_noise_meta_repr(pn_meta_fd: ProcNoiseMeta) -> None:
    """."""
    ref = """ProcNoiseMeta(ProcNoiseKind.FINITE_DIFF
    factor 1.0
    mix_weight 0.75
    mult_by_last_derivative True
    is_dynamic_mixing True)"""
    assert repr(pn_meta_fd) == ref
