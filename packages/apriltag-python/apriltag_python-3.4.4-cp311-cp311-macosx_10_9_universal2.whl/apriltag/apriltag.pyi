"""
Type stubs for apriltag module.

AprilTag visual fiducial system detector.
Auto-generated from C extension module.

Note on type annotations:
    Detection and Pose are defined as TypedDict to provide type hints for the
    dictionaries returned by the C extension. While these are not enforced at
    runtime (the C extension returns plain dict objects), they enable:
    - IDE autocomplete and type checking
    - Static type analysis with mypy/pyright
    - Better documentation through type hints

    This approach follows PEP 589 and is the standard practice for typing
    C extension modules (e.g., numpy, opencv-python, etc.).
"""

from typing import Literal, TypedDict
import numpy as np
import numpy.typing as npt

__version__: str

class Detection(TypedDict):
    """
    AprilTag detection result (returned as dict from C extension).

    Note:
        This is a TypedDict definition for type checking purposes only.
        The actual return value from detect() is a plain dict object.
        See PEP 589 for details on TypedDict semantics.

    Attributes:
        id: The decoded tag ID
        hamming: Number of error bits corrected
        margin: Decision margin (higher is better, measure of detection quality)
        center: Tag center coordinates [x, y]
        lb-rb-rt-lt: 4x2 array of corner coordinates (left-bottom, right-bottom, right-top, left-top)
        homography: 3x3 homography matrix from tag coordinates to image pixels
    """
    id: int
    hamming: int
    margin: float
    center: npt.NDArray[np.float64]  # Shape: (2,)
    homography: npt.NDArray[np.float64]  # Shape: (3, 3)

class Pose(TypedDict):
    """
    Estimated 6-DOF pose of an AprilTag (returned as dict from C extension).

    Note:
        This is a TypedDict definition for type checking purposes only.
        The actual return value from estimate_tag_pose() is a plain dict object.
        See PEP 589 for details on TypedDict semantics.

    Attributes:
        R: 3x3 rotation matrix from tag frame to camera frame
        t: 3x1 translation vector from camera to tag in meters
        error: Reprojection error (lower is better)
    """
    R: npt.NDArray[np.float64]  # Shape: (3, 3)
    t: npt.NDArray[np.float64]  # Shape: (3, 1)
    error: float

TagFamily = Literal[
    'tag36h11',
    'tag36h10',
    'tag25h9',
    'tag16h5',
    'tagCircle21h7',
    'tagCircle49h12',
    'tagStandard41h12',
    'tagStandard52h13',
    'tagCustom48h12'
]

class apriltag:
    """
    AprilTag detector.

    Creates a detector for a specific tag family with configurable parameters.

    Args:
        family: Tag family name. Options:
            - 'tag36h11': Recommended, 36-bit tags with min. Hamming distance of 11
            - 'tag36h10': 36-bit tags with min. Hamming distance of 10
            - 'tag25h9': 25-bit tags with min. Hamming distance of 9
            - 'tag16h5': 16-bit tags with min. Hamming distance of 5
            - 'tagCircle21h7': Circular tags
            - 'tagCircle49h12': Circular tags
            - 'tagStandard41h12': Standard tags
            - 'tagStandard52h13': Standard tags
            - 'tagCustom48h12': Custom tags

        threads: Number of threads to use for detection (default: 1)
            Set to number of CPU cores for best performance.

        maxhamming: Maximum number of bit errors that can be corrected (default: 1)
            Higher values allow detection of more damaged tags but increase
            false positive rate. Range: 0-3.

        decimate: Detection resolution downsampling factor (default: 2.0)
            Detection is performed on a reduced-resolution image. Higher values
            increase speed but reduce accuracy. Set to 1.0 for full resolution.

        blur: Gaussian blur standard deviation in pixels (default: 0.0)
            Can help with noisy images. 0 means no blur.

        refine_edges: Refine quad edge positions for better accuracy (default: True)
            Recommended to keep enabled.

        debug: Enable debug output and save intermediate images (default: False)

    Example:
        >>> import apriltag
        >>> import numpy as np
        >>>
        >>> # Create detector
        >>> detector = apriltag.apriltag('tag36h11', threads=4)
        >>>
        >>> # Detect tags in grayscale image
        >>> image = np.zeros((480, 640), dtype=np.uint8)
        >>> detections = detector.detect(image)
        >>>
        >>> # Process results
        >>> for detection in detections:
        ...     print(f"Tag ID: {detection['id']}")
        ...     print(f"Center: {detection['center']}")
    """

    def __init__(
        self,
        family: TagFamily,
        threads: int = 1,
        maxhamming: int = 1,
        decimate: float = 2.0,
        blur: float = 0.0,
        refine_edges: bool = True,
        debug: bool = False
    ) -> None:
        """
        Initialize AprilTag detector.

        Args:
            family: Tag family name (required)
            threads: Number of threads for detection (default: 1)
            maxhamming: Maximum bit errors to correct (default: 1, range: 0-3)
            decimate: Downsampling factor (default: 2.0)
            blur: Gaussian blur sigma in pixels (default: 0.0)
            refine_edges: Refine quad edges (default: True)
            debug: Enable debug mode (default: False)

        Raises:
            RuntimeError: If family is not recognized or detector creation fails
            ValueError: If maxhamming > 3 or other parameter validation fails
        """
        ...

    def detect(
        self,
        image: npt.NDArray[np.uint8]
    ) -> tuple[Detection, ...]:
        """
        Detect AprilTags in a grayscale image.

        Args:
            image: Grayscale image as a 2D NumPy array of uint8 values.
                Shape should be (height, width).

        Returns:
            Tuple of detection dictionaries. Each detection contains:
                - id (int): The decoded tag ID
                - hamming (int): Number of error bits corrected
                - margin (float): Decision margin (higher is better)
                - center (ndarray): Tag center [x, y], shape (2,)
                - 'lb-rb-rt-lt' (ndarray): Corner coordinates, shape (4, 2)
                  Order: left-bottom, right-bottom, right-top, left-top
                - homography (ndarray): 3x3 homography matrix, shape (3, 3)

        Raises:
            RuntimeError: If image format is invalid or detection fails

        Example:
            >>> import cv2
            >>> image = cv2.imread('tag.jpg', cv2.IMREAD_GRAYSCALE)
            >>> detections = detector.detect(image)
            >>> for det in detections:
            ...     print(f"Found tag {det['id']} at {det['center']}")
        """
        ...

    def estimate_tag_pose(
        self,
        detection: Detection,
        tagsize: float,
        fx: float,
        fy: float,
        cx: float,
        cy: float
    ) -> Pose:
        """
        Estimate the 6-DOF pose of a detected AprilTag.

        This method computes the 3D position and orientation of the tag relative
        to the camera using the homography matrix from detection and camera parameters.

        Args:
            detection: Detection dictionary from detect() method (must include 'homography')
            tagsize: Physical size of the tag in meters (side length of the black square)
            fx: Camera focal length in pixels (x-axis)
            fy: Camera focal length in pixels (y-axis)
            cx: Camera principal point x-coordinate in pixels
            cy: Camera principal point y-coordinate in pixels

        Returns:
            Dictionary containing:
                - R (ndarray): 3x3 rotation matrix from tag frame to camera frame
                - t (ndarray): 3x1 translation vector in meters (camera to tag)
                - error (float): Reprojection error (lower is better)

        Raises:
            TypeError: If detection is not a dictionary
            ValueError: If detection is missing required fields
            RuntimeError: If pose estimation fails

        Example:
            >>> # Camera calibration parameters
            >>> fx, fy = 500.0, 500.0  # focal lengths
            >>> cx, cy = 320.0, 240.0  # principal point
            >>> tagsize = 0.16  # 16cm tag
            >>>
            >>> # Detect and estimate pose
            >>> detections = detector.detect(image)
            >>> for det in detections:
            ...     pose = detector.estimate_tag_pose(det, tagsize, fx, fy, cx, cy)
            ...     print(f"Tag {det['id']} position: {pose['t'].T}")
            ...     print(f"Rotation matrix:\n{pose['R']}")
            ...     print(f"Reprojection error: {pose['error']}")

        Note:
            The rotation matrix R and translation vector t describe the transformation
            from the tag coordinate frame to the camera coordinate frame.
            Tag frame: origin at tag center, z-axis points out of tag, x-axis to the right,
            y-axis pointing up when viewed from the front.
        """
        ...

__all__ = ['apriltag', 'Detection', 'Pose', 'TagFamily']