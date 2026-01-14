"""."""

import pytest

from kinematic_tracker.association.association import Association
from kinematic_tracker.association.match_greedy import MatchDriverGreedy
from kinematic_tracker.association.match_hungarian import MatchDriverHungarian


def test_get_match_driver(association: Association) -> None:
    """."""
    assert isinstance(association.get_match_driver(), MatchDriverGreedy)
    association.method = association.method.HUNGARIAN
    assert isinstance(association.get_match_driver(), MatchDriverHungarian)
    association.method = association.method.UNKNOWN_METHOD
    with pytest.raises(ValueError):
        association.get_match_driver()
