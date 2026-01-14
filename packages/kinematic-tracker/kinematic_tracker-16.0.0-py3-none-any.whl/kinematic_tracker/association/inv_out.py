"""."""

import numpy as np

from .det_type import MT


def inv_out(mat: MT, out: MT) -> None:
    try:
        out[:] = np.linalg.inv(mat)
    except np.linalg.LinAlgError:
        print('\n', mat)
        raise
