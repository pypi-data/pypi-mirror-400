"""."""

from kinematic_tracker.proc_noise.nd_kkf_white_noise_const import NdKkfWhiteNoiseConst


def test_nd_kkf_white_noise_const_repr(wn_const: NdKkfWhiteNoiseConst) -> None:
    """."""
    assert repr(wn_const) == 'NdKkfWhiteNoiseConst(5.678)'
