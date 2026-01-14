"""."""

from kinematic_tracker.proc_noise.nd_kkf_dia_noise import NdKkfDiaNoise


def test_nd_kkf_dia_noise_repr(dia_n: NdKkfDiaNoise) -> None:
    """."""
    assert repr(dia_n) == 'NdKkfDiaNoise(5.678)'
