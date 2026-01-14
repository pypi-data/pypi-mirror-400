"""."""

from typing import Any

from .free_id import get_free_id as get_free_id_list_int


def get_free_id(tracks: list[Any]) -> int:
    """."""
    return get_free_id_list_int([track.id for track in tracks])
