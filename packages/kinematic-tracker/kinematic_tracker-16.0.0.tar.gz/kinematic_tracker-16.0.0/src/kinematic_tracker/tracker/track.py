"""
This module defines the `NdKkfTrack` class. The class represents a tracked target
used in a tracker based on kinematic Kalman filter.
It provides methods to manage the number of consecutive detections, misses.
"""

from association_quality_clavia import UPD_ID_LOOSE

from .kkf import NdKkf


class NdKkfTrack:
    """
    Represents a track in a kinematic tracking system using an NdKkf (N-dimensional Kalman filter).

    Attributes:
        kkf: The kinematic Kalman filter instance associated with this track.
        id: The locally unique identifier for the track. Defaults to -1 (unconfirmed object).
        creation_id: The ID associated with the creation of the track. Defaults to -1.
                     Used as a globally unique identifier for the targets.
                     The creation ID will be not repeated during the lifetime of the tracker.
        ann_id: The annotation ID associated with the track.
        upd_id: The ID of the last update. Defaults to the detection ID.
        score: The score of the track, representing its association metric value. Defaults to 0.0.
        num_det: The number of consecutive associations being done to this track. Defaults to 0.
        num_miss: The number of consecutive misses for the track. Defaults to 0.
    """

    def __init__(self, kkf: NdKkf, ann_id: int) -> None:
        """
        Initializes an instance of the `NdKkfTrack` class.

        Args:
            kkf: The kinematic Kalman filter instance to use in this track.
            ann_id: The annotation ID to mark the track with. The annotation ID
                    is not changing during the lifetime of the track.
        """
        self.kkf = kkf
        self.id = -1
        self.creation_id: int = -1
        self.ann_id = ann_id
        self.upd_id = ann_id
        self.score: float = 0.0
        self.num_det = 0
        self.num_miss = 0

    def bump_num_detections(self, score: float, upd_id: int) -> None:
        """
        Updates the consecutive detection/misses counters with a new detection.

        Args:
            score: The new score to assign to the track.
            upd_id: The update ID associated with the detection.
        """
        self.score = score
        self.num_det += 1
        self.num_miss = 0
        self.upd_id = upd_id

    def bump_num_misses(self) -> None:
        """
        Updates the track to reflect a missed detection.
        Reduces the score by half, resets the number of detections, and increments the number of misses.
        """
        self.score /= 2.0
        self.num_det = 0
        self.num_miss += 1
        self.upd_id = UPD_ID_LOOSE

    def __repr__(self) -> str:
        """
        Returns a string representation of the track, including the current posterior state of the Kalman filter.

        Returns:
            str: A string representation of the track.
        """
        return f'TrackNdKkf(x = {self.kkf.kalman_filter.statePost[:, 0]})'
