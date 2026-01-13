from typing import Dict
import numpy as np

try:
    import cv2
except Exception as e:
    print("An error occurred while importing cv2:", e)
    print(
        "Please install opencv-python(-headless) to use opencv_estimate_tag_pose_solvepnp."
    )


def opencv_estimate_tag_pose_solvepnp(
    
    detection: Dict[str, float | np.ndarray],
    tagsize: float,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    dist_coeffs: np.ndarray | list[float]| None = None,
) -> Dict[str, np.ndarray] | None:
    object_points = np.array(
        [
            [-tagsize / 2, tagsize / 2, 0],
            [tagsize / 2, tagsize / 2, 0],
            [tagsize / 2, -tagsize / 2, 0],
            [-tagsize / 2, -tagsize / 2, 0],
        ],
        dtype=np.float64,
    )
    image_points = np.array(detection["lb-rb-rt-lt"], dtype=np.float64)
    camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)
    ret, rvec, tvec = cv2.solvePnP(
        object_points, image_points, camera_matrix, distCoeffs=dist_coeffs, flags=cv2.SOLVEPNP_IPPE_SQUARE
    )
    if not ret:
        return None
    projected_points, _ = cv2.projectPoints(
        object_points, rvec, tvec, camera_matrix, distCoeffs=dist_coeffs)
    reprojection_error = np.mean(
            np.linalg.norm(projected_points.reshape(-1, 2) - image_points, axis=1)
        )
    return {"R": cv2.Rodrigues(rvec)[0], "t": tvec, "reprojection_error": float(reprojection_error)}
