"""."""

from kinematic_tracker.association.association import Association


def test_repr(association: Association) -> None:
    """."""
    ref = 'Association(greedy mahalanobis threshold 0.56 mah_pre_factor 3.996)'
    assert str(association) == ref
