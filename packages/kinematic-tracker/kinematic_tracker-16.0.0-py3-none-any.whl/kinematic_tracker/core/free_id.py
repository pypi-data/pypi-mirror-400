"""Module providing utility functions for tracking IDs."""


def get_free_id(ids: list[int]) -> int:
    """
    Find the smallest non-negative integer that is not in the given list of IDs.

    This function results in the locally unique IDs. However, will reuse IDs
    if they are not currently in use.

    Args:
        ids (list[int]): A list of integers representing used IDs.

    Returns:
        int: The smallest non-negative integer not present in the list.
    """
    track_id = 0
    for track_id in range(len(ids) + 1):
        if track_id not in ids:
            break
    return track_id
