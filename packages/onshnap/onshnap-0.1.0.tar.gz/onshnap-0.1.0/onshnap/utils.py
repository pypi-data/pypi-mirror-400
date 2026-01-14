"""Utility functions for the onshnap package."""

import re

import numpy as np
from scipy.spatial.transform import Rotation as R


def matrix_to_rpy(mat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Convert a 4x4 transformation matrix to XYZ translation and RPY rotation.

    Onshape returns row-major 4x4 matrices. The rotation is extracted and
    converted to roll-pitch-yaw (XYZ Euler angles) in radians.

    Args:
        mat: 4x4 transformation matrix (row-major)

    Returns:
        Tuple of (xyz, rpy) where:
            xyz: 3-element translation vector [x, y, z]
            rpy: 3-element rotation vector [roll, pitch, yaw] in radians
    """
    if mat.shape != (4, 4):
        raise ValueError(f"Expected 4x4 matrix, got shape {mat.shape}")

    # Extract translation (last column, first 3 rows)
    xyz = mat[:3, 3].flatten()

    # Extract rotation (top-left 3x3)
    rot_mat = mat[:3, :3]

    # Convert to RPY using scipy
    # Use 'xyz' (extrinsic) = 'XYZ' Euler angles = roll-pitch-yaw
    rotation = R.from_matrix(rot_mat)
    rpy = rotation.as_euler("xyz", degrees=False)

    return xyz, rpy


def sanitize_name(name: str) -> str:
    """Sanitize a string for use in URDF names and filenames.

    Replaces special characters with underscores and removes
    characters that are problematic for XML or filesystems.

    Args:
        name: Input string to sanitize

    Returns:
        Sanitized string safe for URDF/filenames
    """
    # Replace angle brackets
    name = name.replace("<", "_").replace(">", "_")

    # Replace whitespace with underscores
    name = re.sub(r"\s+", "_", name)

    # Replace slashes and backslashes
    name = name.replace("/", "_").replace("\\", "_")

    # Keep only alphanumeric, underscore, hyphen, and period
    name = re.sub(r"[^a-zA-Z0-9_\-.]", "_", name)

    # Collapse multiple underscores
    name = re.sub(r"_+", "_", name)

    # Remove leading/trailing underscores
    name = name.strip("_")

    # Ensure non-empty
    if not name:
        name = "unnamed"

    return name


def transform_to_matrix(transform_list: list[float]) -> np.ndarray:
    """Convert Onshape's 16-float transform array to a 4x4 matrix.

    Onshape returns transforms as a flat 16-element list in row-major order.

    Args:
        transform_list: 16-element list from Onshape API

    Returns:
        4x4 numpy array transformation matrix
    """
    if len(transform_list) != 16:
        raise ValueError(f"Expected 16 elements, got {len(transform_list)}")

    return np.array(transform_list).reshape(4, 4)


def matrix_to_transform(mat: np.ndarray) -> list[float]:
    """Convert a 4x4 matrix back to Onshape's 16-float format.

    Args:
        mat: 4x4 numpy array

    Returns:
        16-element list in row-major order
    """
    if mat.shape != (4, 4):
        raise ValueError(f"Expected 4x4 matrix, got shape {mat.shape}")

    return mat.flatten().tolist()
