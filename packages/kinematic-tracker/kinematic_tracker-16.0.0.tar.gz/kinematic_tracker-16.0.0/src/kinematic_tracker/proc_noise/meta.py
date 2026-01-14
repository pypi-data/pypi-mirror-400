"""."""

from .kind import ProcNoiseKind


class ProcNoiseMeta:
    """."""

    def __init__(self) -> None:
        """."""
        self.noise_kind: ProcNoiseKind = ProcNoiseKind.FINITE_DIFF
        self.factor: float = 1.0
        self.mix_weight: float = 0.9
        self.mult_by_last_derivative: bool = True
        self.is_dynamic_mixing: bool = True

    def __repr__(self) -> str:
        """."""
        return (
            f'ProcNoiseMeta({self.noise_kind}\n'
            f'    factor {self.factor}\n'
            f'    mix_weight {self.mix_weight}\n'
            f'    mult_by_last_derivative {self.mult_by_last_derivative}\n'
            f'    is_dynamic_mixing {self.is_dynamic_mixing})'
        )


def get_proc_noise_meta(
    pn_kind: ProcNoiseKind,
    factor: float | None = None,
    mix_weight: float = 0.9,
    mult_by_last_der=True,
    is_dyn_mixing=True,
) -> ProcNoiseMeta:
    """A smarter than nothing factory for initialization of the process-noise-meta objects.

    Note: the expression sometimes below means "for some kinds of the process noise".

    Args:
        pn_kind: the process-noise kind. Only the user can decide this parameter.
        factor: the variance pre-factor in all cases.
                Sometimes I can use default value, sometimes not.
        mix_weight: the mixing weight used sometimes. I can always reasonably decide its value.
        mult_by_last_der: the flag used in the FINITE_DIFF process-noise kind, True by default.
        is_dyn_mixing: the flag used in the FINITE_DIFF process-noise kind, True by default.

    Returns:
        The object.

    Raises:
        ValueError: if the factor is None for the CONST or DIAGONAL process-noise kinds.
    """
    if pn_kind in (ProcNoiseKind.CONST, ProcNoiseKind.DIAGONAL) and factor is None:
        raise ValueError('I cannot reasonably decide the factor value')

    factor = 1.0 if factor is None else factor
    meta = ProcNoiseMeta()
    meta.noise_kind = pn_kind
    meta.factor = factor
    meta.mix_weight = mix_weight
    meta.mult_by_last_derivative = mult_by_last_der
    meta.is_dynamic_mixing = is_dyn_mixing
    return meta
