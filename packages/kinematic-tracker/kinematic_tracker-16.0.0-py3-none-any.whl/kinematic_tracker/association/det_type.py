from typing import Sequence

import cv2
import numpy as np


MT = np.ndarray[tuple[int, int], np.dtype[np.float64]]
VT = np.ndarray[tuple[int], np.dtype[np.float64]]
DT = Sequence[VT] | MT | Sequence[Sequence[float]]
FT = Sequence[cv2.KalmanFilter]
