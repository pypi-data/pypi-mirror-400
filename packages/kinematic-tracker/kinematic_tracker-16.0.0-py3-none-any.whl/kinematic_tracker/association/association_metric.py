"""Types of association metrics (matching scores)."""

from enum import Enum


class AssociationMetric(Enum):
    """."""

    GIOU = 'giou'
    MAHALANOBIS = 'mahalanobis'
    SIZE_MODULATED_MAHALANOBIS = 'size-modulated-mahalanobis'
    MEAN_DIM_GIOU = 'mean-dim-giou'
    UNKNOWN_METRIC = 'unknown-metric'
