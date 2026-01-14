"""."""

import pytest

from kinematic_tracker.proc_noise.kind import ProcNoiseKind
from kinematic_tracker.proc_noise.meta import get_proc_noise_meta


def test_corner_cases() -> None:
    """."""
    with pytest.raises(ValueError):
        get_proc_noise_meta(ProcNoiseKind.DIAGONAL)
