# apriltag-python

[![PyPI version](https://badge.fury.io/py/apriltag-python.svg)](https://badge.fury.io/py/apriltag-python)
[![License](https://img.shields.io/badge/License-BSD%202--Clause-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A Python wrapper for the [AprilTag visual fiducial detector](https://github.com/AprilRobotics/apriltag). This library provides fast and robust detection of AprilTag markers in images, along with pose estimation capabilities.

## Features

- **Fast Detection**: Optimized C implementation with Python bindings
- **Multi-threading Support**: Parallel detection for better performance
- **Multiple Tag Families**: Support for tag36h11, tag25h9, tag16h5, and more
- **Pose Estimation**: 6-DOF pose estimation from detected tags
- **Type Hints**: Full type annotations for better IDE support
- **Cross-platform**: Works on Linux, macOS, and Windows

## Installation

Install from PyPI:

```bash
pip install apriltag-python
```

### Requirements

- Python 3.10 or higher
- NumPy

## Quick Start

```python
import apriltag
import cv2

# Create detector for tag36h11 family
detector = apriltag.apriltag('tag36h11', threads=4)

# Load a grayscale image
image = cv2.imread('image.jpg', cv2.IMREAD_GRAYSCALE)

# Detect tags
detections = detector.detect(image)

# Process results
for detection in detections:
    print(f"Tag ID: {detection['id']}")
    print(f"Center: {detection['center']}")
    print(f"Corners: {detection['lb-rb-rt-lt']}")
```

## Usage

### Basic Detection

```python
import apriltag
import numpy as np

# Create detector with custom parameters
detector = apriltag.apriltag(
    family='tag36h11',      # Tag family
    threads=4,              # Number of threads
    maxhamming=1,           # Maximum hamming distance for error correction
    decimate=2.0,           # Image downsampling factor
    blur=0.0,               # Gaussian blur sigma
    refine_edges=True,      # Refine quad edges
    debug=False             # Debug mode
)

# Detect tags in a grayscale image
image = np.zeros((480, 640), dtype=np.uint8)  # Example: black image
detections = detector.detect(image)
```

### Detection Results

Each detection is a dictionary containing:

- `id` (int): The decoded tag ID
- `hamming` (int): Number of bit errors corrected
- `margin` (float): Decision margin (higher values indicate better detection quality)
- `center` (ndarray): Tag center coordinates [x, y], shape (2,)
- `lb-rb-rt-lt` (ndarray): Four corner coordinates in order: left-bottom, right-bottom, right-top, left-top, shape (4, 2)
- `homography` (ndarray): 3×3 homography matrix mapping tag coordinates to image pixels, shape (3, 3)

### Pose Estimation

Estimate the 6-DOF pose (position and orientation) of detected tags:

```python
# Camera calibration parameters
fx, fy = 500.0, 500.0  # Focal lengths in pixels
cx, cy = 320.0, 240.0  # Principal point (image center)
tagsize = 0.16         # Physical tag size in meters (e.g., 16cm)

# Detect tags
detections = detector.detect(image)

# Estimate pose for each detection
for det in detections:
    pose = detector.estimate_tag_pose(det, tagsize, fx, fy, cx, cy)

    print(f"Tag {det['id']}:")
    print(f"  Position (meters): {pose['t'].T}")
    print(f"  Rotation matrix:\n{pose['R']}")
    print(f"  Reprojection error: {pose['error']}")
```

The pose result contains:

- `R` (ndarray): 3×3 rotation matrix from tag frame to camera frame
- `t` (ndarray): 3×1 translation vector from camera to tag in meters
- `error` (float): Reprojection error (lower is better)

### Coordinate Frames

- **Tag Frame**: Origin at tag center, z-axis pointing out of the tag surface, x-axis to the right, y-axis pointing up (when viewed from the front)
- **Camera Frame**: Standard computer vision convention with z-axis pointing forward

## Supported Tag Families

- `tag36h11` (Recommended): 36-bit tags with minimum Hamming distance of 11
- `tag36h10`: 36-bit tags with minimum Hamming distance of 10
- `tag25h9`: 25-bit tags with minimum Hamming distance of 9
- `tag16h5`: 16-bit tags with minimum Hamming distance of 5
- `tagCircle21h7`: Circular tags
- `tagCircle49h12`: Circular tags
- `tagStandard41h12`: Standard tags
- `tagStandard52h13`: Standard tags
- `tagCustom48h12`: Custom tags

## Performance Tips

1. **Use multiple threads**: Set `threads` to the number of CPU cores for parallel processing
2. **Adjust decimation**: Increase `decimate` (e.g., 2.0-4.0) for faster detection on high-resolution images
3. **Image preprocessing**: Ensure good contrast and lighting for better detection
4. **Choose appropriate family**: `tag36h11` provides the best balance of robustness and variety

## Complete Example with OpenCV

```python
import apriltag
import cv2
import numpy as np

# Initialize detector
detector = apriltag.apriltag('tag36h11', threads=4, decimate=2.0)

# Camera parameters (replace with your calibration values)
fx, fy = 500.0, 500.0
cx, cy = 320.0, 240.0
tagsize = 0.16  # 16cm tags

# Capture from camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect tags
    detections = detector.detect(gray)

    # Draw results
    for det in detections:
        # Draw corners
        corners = det['lb-rb-rt-lt'].astype(int)
        cv2.polylines(frame, [corners], True, (0, 255, 0), 2)

        # Draw center
        center = tuple(det['center'].astype(int))
        cv2.circle(frame, center, 5, (0, 0, 255), -1)

        # Draw ID
        cv2.putText(frame, str(det['id']), center,
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        # Estimate and print pose
        pose = detector.estimate_tag_pose(det, tagsize, fx, fy, cx, cy)
        distance = np.linalg.norm(pose['t'])
        print(f"Tag {det['id']} distance: {distance:.2f}m")

    cv2.imshow('AprilTag Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## Building from Source

```bash
git clone --recursive https://github.com/chibai/apriltag-python.git
cd apriltag-python
pip install .
```

### Build Requirements

- C compiler (GCC, Clang, or MSVC)
- CMake 3.15+
- Python development headers
- NumPy

## License

This project is licensed under the BSD 2-Clause License - see the [LICENSE](LICENSE) file for details.

The underlying AprilTag library is also BSD-licensed.

## Credits

- **AprilTag Library**: [AprilRobotics/apriltag](https://github.com/AprilRobotics/apriltag)
- **Python Wrapper**: chibai (huangyibin1992@gmail.com)

## Citation

If you use this library in your research, please cite the original AprilTag paper:

```bibtex
@inproceedings{wang2016iros,
  author    = {John Wang and Edwin Olson},
  title     = {{AprilTag} 2: Efficient and robust fiducial detection},
  booktitle = {Proceedings of the {IEEE/RSJ} International Conference on Intelligent Robots and Systems {(IROS)}},
  year      = {2016},
  month     = {October}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Links

- **PyPI**: https://pypi.org/project/apriltag-python/
- **Source Code**: https://github.com/chibai/apriltag-python
- **AprilTag Homepage**: https://april.eecs.umich.edu/software/apriltag
- **Issues**: https://github.com/chibai/apriltag-python/issues