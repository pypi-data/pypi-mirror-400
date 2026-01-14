"""."""

import copy

from typing import Any, Iterator

import numpy as np

from association_quality_clavia import AssociationQuality

from kinematic_tracker.nd.derivative_sorted import DerivativeSorted
from kinematic_tracker.nd.gen_x import NdKkfMatGenX
from kinematic_tracker.tracker.track import NdKkfTrack
from kinematic_tracker.tracker.tracker import NdKkfTracker


class AlignedCuboidDetectionsFromCsv:
    """."""

    def __init__(self, file_name: str) -> None:
        """."""
        self.file_name = file_name
        self.tss_s = np.genfromtxt(file_name, skip_header=1, delimiter=',', usecols=(0,), dtype=int)
        self.ids_s = np.genfromtxt(file_name, skip_header=1, delimiter=',', usecols=(1,), dtype=int)
        self.det_sz = np.genfromtxt(file_name, skip_header=1, delimiter=',', usecols=range(2, 8))
        self.stamps = np.unique(self.tss_s)

    def gen_stamps_ids_vec_z(
        self,
    ) -> Iterator[tuple[int, np.ndarray[Any, float], np.ndarray[Any, int]]]:
        """."""
        for stamp in self.stamps:
            mask = self.tss_s == stamp
            det_rz, ids_r = self.det_sz[mask], self.ids_s[mask]
            yield stamp, det_rz, ids_r

    def run_tracking(self, tracker: NdKkfTracker) -> list[tuple[int, list[NdKkfTrack]]]:
        """."""
        history: list[tuple[int, list[NdKkfTrack]]] = []
        for stamp, det_rz, ids_r in self.gen_stamps_ids_vec_z():
            tracker.advance(int(stamp), det_rz, ids_r)
            assert len(tracker.tracks) >= len(ids_r)
            history.append((stamp, copy.deepcopy(tracker.tracks)))
        return history

    def get_det_ids(self, stamp: int) -> np.ndarray[Any, int]:
        """."""
        return self.ids_s[self.tss_s == stamp]

    def analyse_association(
        self, history: list[tuple[int, list[NdKkfTrack]]]
    ) -> AssociationQuality:
        """."""
        association_quality = AssociationQuality()
        for stamp, tracks in history:
            det_ids = self.get_det_ids(stamp)
            for track in tracks:
                is_supplied = track.ann_id in det_ids
                association_quality.classify(track.ann_id, track.upd_id, is_supplied)
        return association_quality


class AlignedCuboidMotionFromCsv:
    """."""

    def __init__(self, file_name: str) -> None:
        """."""
        self.file_name = file_name
        self.tss_s = np.genfromtxt(file_name, skip_header=1, delimiter=',', usecols=(0,), dtype=int)
        self.ids_s = np.genfromtxt(file_name, skip_header=1, delimiter=',', usecols=(1,), dtype=int)
        self.ref_sx = np.genfromtxt(file_name, skip_header=1, delimiter=',', usecols=range(2, 14))
        self.stamps = np.unique(self.tss_s)

    def compute_ate(self, history: list[tuple[int, list[NdKkfTrack]]]) -> float:
        """."""
        gen_x = NdKkfMatGenX([3, 1], [3, 3])
        der_sorted = DerivativeSorted(gen_x)
        post_x = np.zeros(12)
        ref_ix = []
        post_ix = []
        for stamp, tracks in history:
            mask_s = self.tss_s == stamp
            ids_r = self.ids_s[mask_s]
            ref_rx = self.ref_sx[mask_s]
            for track in tracks:
                mask_r = ids_r == track.ann_id
                ref_x = ref_rx[mask_r].reshape(12)
                der_sorted.convert_vec(track.kkf.kalman_filter.statePost.reshape(12), post_x)
                ref_ix.append(ref_x)
                post_ix.append(post_x.copy())
        ref_ix = np.array(ref_ix)
        post_ix = np.array(post_ix)
        ate = np.mean(np.linalg.norm(ref_ix[:, :3] - post_ix[:, :3], axis=1))
        return ate
