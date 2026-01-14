"""
This module provides functionality for calculating the Generalized Intersection over Union (GIoU)
between two 3D bounding boxes. The bounding boxes are aligned with Cartesian axes.
It includes a helper class `GIoUAux` that encapsulates the necessary operations and
intermediate quantities for computing GIoU.
"""

import numpy as np


class GIoUAux:
    """
    A helper class for calculating the Generalized Intersection over Union (GIoU)
    between two 3D bounding boxes aligned with Cartesian axes. The object represents
    one bounding box. The bounding box is defined by the coordinates of its geometrical
    center and its extent along each of the Cartesian axes.
    """

    def __init__(self) -> None:
        """
        Initializes the GIoUAux object with nil values for the bounding box
        corners, volume, and intermediate arrays used in calculations.
        """
        self.corners: np.ndarray = np.zeros((2, 3))  # Min and max corners of the bounding box
        self.volume = 0.0  # Volume of the bounding box
        self.min_max: np.ndarray = np.zeros(3)  # Temporary array for min of max corners
        self.max_min: np.ndarray = np.zeros(3)  # Temporary array for max of min corners
        self.min_min: np.ndarray = np.zeros(3)  # Temporary array for min of min corners
        self.max_max: np.ndarray = np.zeros(3)  # Temporary array for max of max corners
        self.diff: np.ndarray = np.zeros(3)  # Temporary array for differences in dimensions

    def set_vec_z(self, vec_z: np.ndarray[tuple[int, ...], np.dtype[np.float64]]) -> None:
        """Set the bounding box center and dimensions.

        Args:
            vec_z: The center and dimensions of the bounding box packed into one vector.
                   vec_z = (pos_x, pos_y, pos_z, dim_x, dim_y, dim_z)
        """
        flat_z = vec_z.flatten()
        self.corners[:] = flat_z[:3]  # Set the center coordinates
        half_dim = flat_z[3:6] / 2.0  # Compute half of the dimensions
        self.corners[0] -= half_dim  # Compute the minimum corner
        self.corners[1] += half_dim  # Compute the maximum corner
        self.volume = flat_z[3:6].prod()  # Compute the volume of the bounding box

    def get_g_iou_diff(self, other: 'GIoUAux') -> float:
        """
        Computes the Generalized Intersection over Union (GIoU) difference
        between this bounding box and another.

        Args:
            other (GIoUAux): Another GIoUAux object representing a bounding box.

        Returns:
            float: The GIoU difference value.
        """
        intersection_volume = self.get_intersection(other)  # Compute intersection volume
        union_volume = self.volume + other.volume - intersection_volume  # Compute union volume
        iou = intersection_volume / union_volume  # Compute IoU
        enclosing_volume = self.get_enclosing(other)  # Compute enclosing volume
        g_iou = iou - (enclosing_volume - union_volume) / enclosing_volume  # Compute GIoU
        return g_iou

    def get_g_iou(self, other: 'GIoUAux') -> float:
        """
        Computes the Generalized Intersection over Union (GIoU) between this
        bounding box and another.

        Args:
            other (GIoUAux): Another GIoUAux object representing a bounding box.

        Returns:
            float: The GIoU value, normalized to the range [0, 1].
        """
        return (self.get_g_iou_diff(other) + 1.0) / 2.0

    def get_intersection(self, other: 'GIoUAux') -> float:
        """
        Computes the intersection volume between this bounding box and another.

        Args:
            other (GIoUAux): Another GIoUAux object representing a bounding box.

        Returns:
            float: The intersection volume. Returns 0.0 if there is no intersection.
        """
        np.fmin(self.corners[1, :], other.corners[1, :], out=self.min_max)  # Min of max corners
        np.fmax(self.corners[0, :], other.corners[0, :], out=self.max_min)  # Max of min corners
        np.subtract(self.min_max, self.max_min, out=self.diff)  # Compute the difference
        return 0.0 if np.any(self.diff < 0.0) else self.diff.prod()  # Return volume or 0.0

    def get_enclosing(self, other: 'GIoUAux') -> float:
        """
        Computes the volume of the smallest enclosing box that contains both
        this bounding box and another.

        Args:
            other (GIoUAux): Another GIoUAux object representing a bounding box.

        Returns:
            float: The enclosing volume.
        """
        np.fmin(self.corners[0, :], other.corners[0, :], out=self.min_min)  # Min of min corners
        np.fmax(self.corners[1, :], other.corners[1, :], out=self.max_max)  # Max of max corners
        np.subtract(self.max_max, self.min_min, out=self.diff)  # Compute the difference
        return self.diff.prod()  # Return the enclosing volume
