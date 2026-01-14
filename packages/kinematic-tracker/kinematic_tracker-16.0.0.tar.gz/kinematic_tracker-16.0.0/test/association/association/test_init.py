"""."""

from kinematic_tracker.association.association import Association
from kinematic_tracker.association.association_metric import AssociationMetric


def test_init() -> None:
    """."""
    association = Association(12, 6)
    assert association.metric == AssociationMetric.MAHALANOBIS
