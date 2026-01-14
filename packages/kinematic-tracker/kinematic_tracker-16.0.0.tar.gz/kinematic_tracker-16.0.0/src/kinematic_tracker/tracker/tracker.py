"""NdKkfTracker class implementation.

This module defines the NdKkfTracker class. The tracker is responsible for managing
and updating a set of Kalman filter-based tracks to organize the multiple-object tracking.
It provides methods for associating detections with existing tracks, creating
new tracks, and removing stale tracks.

Classes:
    NdKkfTracker: A tracker that uses kinematic Kalman filters for multiple-object tracking.
"""

from typing import Sequence

import cv2
import numpy as np

from kinematic_tracker.association.association import Association, AssociationMethod
from kinematic_tracker.association.association_metric import AssociationMetric
from kinematic_tracker.association.det_type import MT, VT
from kinematic_tracker.core.creation_id import CreationId
from kinematic_tracker.core.loose_items import get_loose_indices
from kinematic_tracker.core.track_free_id import get_free_id
from kinematic_tracker.nd.gen_kf import NdKkfGenKf
from kinematic_tracker.nd.shape import NdKkfShape
from kinematic_tracker.proc_noise.meta import ProcNoiseMeta
from kinematic_tracker.proc_noise.nd_kkf_proc_noise_factory import get_proc_noise

from .kkf import NdKkf
from .track import NdKkfTrack


UNKNOWN_REPORT_ID = -1000


class NdKkfTracker:
    """NdKkfTracker class to manage the multiple-object tracking using the
       N-dimensional, mixed-order, kinematic Kalman filters.

    Attributes:
        shape: auxiliary object encoding the distribution of variables in N-dimensional,
               mixed-order, block-diagonal state vectors.
        gen_xz: A manager object to cope with the block-diagonal distribution of variables.
        ini_der_vars: Initial variances for diagonal parts of the error covariances not defined
                      by the measurement covariances.
        pre: Precursor 1D matrices for Kalman filter prediction step (transition- and white-noise).
        pn_meta: Metadata (parameters) for the process-noise calculation.
        creation_id: A generator of the globally unique track IDs.
        tracks: List of tracked targets.
        gen_kf: Kalman filter generator. Contains a shared buffer for transition matrices.
        association: Metadata (parameters) for association of detection reports and targets.
        metric_driver: Metric computation driver for association.
        match_driver: Match computation driver for association.
        cov_zz: Measurement covariance matrix. Initially None, must be set before use.
        num_misses_max: Maximum number of consecutive misses before target removal.
        num_det_min: Minimum number of consecutive detections required to confirm targets.
        last_ts_ns: Timestamp of the last prediction in nanoseconds.
    """

    def __init__(
        self,
        orders_x: Sequence[int],
        num_dims: Sequence[int],
        orders_z: Sequence[int] | None = None,
    ) -> None:
        """Initialize the NdKkfTracker.

        Args:
            orders_x: Kinematic orders for each part of the ND, mixed-order states.
            num_dims: Number of dimensions for each part of the ND, mixed-order state.
            orders_z: Kinematic orders of the measurement variables. The argument is optional.
                      If not provided, it defaults to a sequence of ones of suitable length.
        """
        orders_z_seq = [1] * len(num_dims) if orders_z is None else orders_z
        self.shape = NdKkfShape(orders_x, num_dims, orders_z_seq)
        self.gen_xz = self.shape.get_mat_gen_xz()
        self.ini_der_vars = 100.0 * np.ones(self.gen_xz.gen_x.num_d)
        self.pre = self.shape.get_precursors()
        self.pn_meta = ProcNoiseMeta()
        self.creation_id = CreationId()
        self.tracks: list[NdKkfTrack] = []
        num_x = self.gen_xz.gen_x.num_x
        self.gen_kf = NdKkfGenKf(np.zeros((num_x, num_x)))
        self.association = Association(num_x, self.gen_xz.num_z)
        self.metric_driver = self.association.get_metric_driver()
        self.match_driver = self.association.get_match_driver()
        self.cov_zz: np.ndarray | None = None
        self.num_misses_max = 3
        self.num_det_min = 3
        self.last_ts_ns = 0
        num_reports_max = self.association.num_reports_max
        self.unknown_report_ids = UNKNOWN_REPORT_ID * np.ones(num_reports_max, dtype=int)

    def internal_check(self) -> None:
        """Perform internal consistency checks.

        Raises:
            RuntimeError: If the measurement covariance is not set or contains NaN values.
        """
        if self.cov_zz is None:
            raise RuntimeError('Forgot to set the measurement covariance?')
        if np.any(np.isnan(self.cov_zz)):
            raise RuntimeError('All standard deviations defined?')

    def set_association_method(self, method_name: str) -> None:
        """Set the association method for matching detections to tracks.

        Args:
            method_name: Name of the association method.
        """
        self.association.method = AssociationMethod(method_name)
        self.match_driver = self.association.get_match_driver()

    def set_association_metric(
        self,
        metric_name: str,
        mah_factor: float = 1.0,
        ind_pos_size: Sequence[int] = (0, 1, 2, -3, -2, -1),
    ) -> None:
        """Set the association metric for evaluating matches.

        Args:
            metric_name: name of the association metric.
            mah_factor: Mahalanobis distance pre-factor. Defaults to 1.0.
            ind_pos_size: indices for extracting positions and sizes from the measurement vectors.
                          For more details, see docstring of the method `set_ind_pos_size(...)`.
        """
        self.association.metric = AssociationMetric(metric_name)
        self.association.mah_pre_factor = mah_factor
        self.association.ind_pos_size = ind_pos_size
        self.metric_driver = self.association.get_metric_driver()

    def set_association_threshold(self, threshold: float) -> None:
        """Set the matching threshold for the association.

        The threshold is a guard against clutter detections.
        This setter is very simple. It exists to assure the library consumers.

        Args:
            threshold: new threshold value.
        """
        if not (0.0 < threshold < 1.0):
            raise ValueError(f'Threshold {threshold} seems to be out of range.')
        self.association.threshold = threshold

    def set_max_reports_and_targets(self, num_reports_max: int, num_targets_max: int) -> None:
        """Set the maximum number of reports (detected objects) and targets (tracked objects).

        Args:
            num_reports_max: maximum number of reports.
            num_targets_max: maximum number of targets.
        """
        self.association.num_reports_max = num_reports_max
        self.association.num_targets_max = num_targets_max
        self.unknown_report_ids = UNKNOWN_REPORT_ID * np.ones(num_reports_max, dtype=int)
        self.metric_driver = self.association.get_metric_driver()
        self.match_driver = self.association.get_match_driver()

    def set_ind_pos_size(self, ind_pos_size: Sequence[int]) -> None:
        """Set the distribution of variables in the measurement vector.

        This is relevant for GIoU metric because for this metric we treat the
        variables in a non-uniform way. Firstly, the measurement vector
        should contain the positions of the cuboids as well as their sizes (dimensions).
        Secondly, we should not mix up positions (vector with 3 variables)
        and sizes (another vector with 3 variables). Finally, the distribution
        of variables in the measurement vector could be arbitrary, so we
        need a permutation index in general. The argument `ind_pos_size` should be
        a sequence of integers pointing to the positions and sizes of the cuboids
        in the following convention:

           (pos_x, pos_y, pos_z, size_x, size_y, size_z)

        By default, the `ind_pos_size = (0, 1, 2, -3, -2, -1)`. This corresponds
        to the positions gathered at the start of the measurement vector and
        the sizes gathered at the end of the measurement vector. This choice of default
        value should be convenient for ASAM OpenLabel measurement vectors.
        The ASAM OpenLabel measurement vectors feature the following distribution of
        variables

            z^T = (px, py, pz, alpha, beta, gamma, sx, sy, sz)

        or

            z^T = (px, py, pz, a, b, c, d, sx, sy, sz)

        In both cases, the sizes of the cuboids locate at the end of the measurement vector.

        Args:
            ind_pos_size: the permutation pointer array.
        """
        self.tracks.clear()
        self.association.ind_pos_size = ind_pos_size
        self.metric_driver = self.association.get_metric_driver()

    def set_measurement_cov(self, cov_zz: np.ndarray) -> None:
        """Set (the whole) measurement covariance matrix.

        Args:
            cov_zz: Measurement covariance matrix.

        Raises:
            ValueError: If the shape of the covariance matrix is incorrect.
        """
        shape = (self.gen_xz.num_z, self.gen_xz.num_z)
        if self.cov_zz is None:
            self.cov_zz = np.zeros(shape)
        if cov_zz.shape != shape:
            raise ValueError(f'Wrong shape of the measurement covariance. Expected {shape}')
        self.cov_zz[:, :] = cov_zz

    def set_measurement_std_dev(self, part: int, std_dev: float, der_order: int = 0) -> None:
        """Set the standard deviation for a given part of the measurement vector.

        Args:
            part: Index of the measurement part.
            std_dev: Standard deviation value.
            der_order: Derivative order. Defaults to 0.

        Raises:
            ValueError: If no element is found for the given part and derivative order.
        """
        if self.cov_zz is None:
            self.cov_zz = np.eye(self.gen_xz.num_z)
            for i in range(self.gen_xz.num_z):
                self.cov_zz[i, i] = np.nan  # to prevent incomplete initialization

        ind = 0
        variance = std_dev * std_dev
        is_set = False
        for cur_part, (o, nd) in enumerate(zip(self.gen_xz.orders_z, self.gen_xz.gen_x.num_dof)):
            for _ in range(nd):
                for cur_der_order in range(o):
                    if cur_der_order == der_order and cur_part == part:
                        self.cov_zz[ind, ind] = variance
                        is_set = True
                    ind += 1
        if not is_set:
            raise ValueError(f'No element found for part {part} and der_order {der_order}')

    def __repr__(self) -> str:
        """Return a string representation of the tracker.

        Returns:
            str: String representation of the tracker.
        """
        return (
            f'NdKkfTracker(\n'
            f'    {self.association}\n'
            f'    num_misses_max {self.num_misses_max}\n'
            f'    num_det_min {self.num_det_min})'
        )

    def correct_associated(
        self,
        reports: Sequence[int],
        targets: Sequence[int],
        metric_rt: np.ndarray,
        det_rz: Sequence[np.ndarray],
        ids_r: Sequence[int],
    ) -> None:
        """Correct tracks based on the given association matches.

        Args:
            reports: Indices of associated detection reports.
            targets: Indices of associated tracked targets.
            metric_rt: Metric values for report-target pairs.
            det_rz: Detection vectors to be used eventually for correction step.
            ids_r: Detection IDs to be used eventually for assigning the update IDs.
        """
        for r, t in zip(reports, targets):
            track = self.tracks[t]
            track.kkf.correct(det_rz[r])
            track.bump_num_detections(float(metric_rt[r, t]), ids_r[r])

    def update_for_loose_tracks(self, targets: Sequence[int], num_tracks_before: int) -> None:
        """Update the list of tracks for loose tracks (i.e., tracks without association).

        Args:
            targets: Indices of associated tracks.
            num_tracks_before: Number of tracks before association.
        """
        tracks_wo_correspondence = get_loose_indices(targets, num_tracks_before)
        for t in tracks_wo_correspondence:
            self.tracks[t].bump_num_misses()

        to_remove = [t for t in self.tracks if t.num_miss > self.num_misses_max]
        for t in to_remove:
            self.tracks.remove(t)

    def get_track(self, vec_z: np.ndarray, ann_id: int) -> NdKkfTrack:
        """Create a new track for a given measurement vector, with corresponding annotation ID.

        Args:
            vec_z: Measurement (detection) vector.
            ann_id: Annotation ID of the detection report.

        Returns:
            NdKkfTrack: Newly created track.
        """
        self.internal_check()
        kf = self.gen_kf.get_kf(self.gen_xz, vec_z, self.cov_zz, self.ini_der_vars)
        proc_noise = get_proc_noise(self.gen_xz.gen_x, self.pn_meta, kf.statePre[:, 0])
        nd_kkf = NdKkf(kf, proc_noise)
        track = NdKkfTrack(nd_kkf, ann_id)
        track.creation_id = self.creation_id.get_next_id()
        return track

    def update_for_loose_reports(
        self, reports: Sequence[int], det_rz: Sequence[np.ndarray], ids_r: Sequence[int]
    ) -> None:
        """Update the list of tracks for loose detections (detections without association).

        Args:
            reports: Indices of associated reports.
            det_rz: Detection vectors to eventually construct the states of new targets.
            ids_r: Annotation IDs to eventually assign in the new targets.
        """
        reports_wo_correspondence = get_loose_indices(reports, len(det_rz))
        for r in reports_wo_correspondence:
            self.tracks.append(self.get_track(det_rz[r], ids_r[r]))

    def promote_clutter_eventually(self) -> None:
        """Promote clutter tracks to regular tracks if they meet the
        condition on the minimal number of consecutive associations.
        """
        for track in self.tracks:
            if track.id < 0 and track.num_det > self.num_det_min:
                track.id = get_free_id(self.tracks)

    def get_filters(self) -> list[cv2.KalmanFilter]:
        """Get the list of Kalman filters for all tracks.

        Returns:
            list[cv2.KalmanFilter]: List of Kalman filters.
        """
        return [track.kkf.kalman_filter for track in self.tracks]

    def predict_all(self, time_stamp_ns: int) -> None:
        """Predict the state of all tracks to the given timestamp.

        Args:
            time_stamp_ns: Timestamp in nanoseconds.
        """
        dt = (time_stamp_ns - self.last_ts_ns) / 1e9
        assert dt >= 0.0
        self.last_ts_ns = time_stamp_ns
        self.pre.compute(dt)
        self.gen_xz.gen_x.fill_f_mat(self.pre, self.gen_kf.f_mat)
        for track in self.tracks:
            track.kkf.predict(self.pre)

    def advance(
        self, stamp_ns: int, det_rz: Sequence[VT] | MT, ids_r: Sequence[int] | None = None
    ) -> list[NdKkfTrack]:
        """Advance tracks to the given timestamp with new detections.

        Args:
            stamp_ns: timestamp of the detections in nanoseconds.
            det_rz: detection vectors.
            ids_r: annotation IDs.

        Returns:
            list[NdKkfTrack]: Updated list of tracks.
        """
        if isinstance(det_rz, np.ndarray):
            assert det_rz.ndim == 2
            assert det_rz.shape[1] == self.gen_xz.num_z

        assert isinstance(stamp_ns, int) or isinstance(stamp_ns, np.int64), (
            f'Time stamp (nanoseconds) should be an integer or np.int64, but got {type(stamp_ns)}'
        )
        self.predict_all(stamp_ns)
        score_rt = self.metric_driver.compute_metric(det_rz, self.get_filters())
        self.match_driver.compute_matches(score_rt, self.association.threshold)
        reports, targets = self.match_driver.get_reports_targets()
        report_ids = self.unknown_report_ids[: len(det_rz)] if ids_r is None else ids_r
        self.correct_associated(reports, targets, score_rt, det_rz, report_ids)
        num_tracks_before = len(self.tracks)
        self.update_for_loose_reports(reports, det_rz, report_ids)
        self.promote_clutter_eventually()
        self.update_for_loose_tracks(targets, num_tracks_before)
        return self.tracks
