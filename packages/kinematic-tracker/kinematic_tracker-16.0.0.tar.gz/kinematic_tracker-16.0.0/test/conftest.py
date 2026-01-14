"""."""

import pytest

from kinematic_tracker.proc_noise.meta import ProcNoiseKind, ProcNoiseMeta, get_proc_noise_meta


@pytest.fixture
def pn_meta_fd() -> ProcNoiseMeta:
    return get_proc_noise_meta(ProcNoiseKind.FINITE_DIFF, 1.0, 0.75, True, True)
