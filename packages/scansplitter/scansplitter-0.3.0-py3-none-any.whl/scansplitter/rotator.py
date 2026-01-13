"""Automatic rotation detection and correction for photos."""

import cv2
import numpy as np
from PIL import Image

# Lazy-loaded face detection network
_face_net = None


def _get_face_net():
    """Lazy-load the face detection neural network."""
    global _face_net
    if _face_net is None:
        from .models import get_model_paths

        prototxt_path, caffemodel_path = get_model_paths()
        _face_net = cv2.dnn.readNetFromCaffe(str(prototxt_path), str(caffemodel_path))
    return _face_net


def detect_face(cv_image: np.ndarray, min_confidence: float = 0.7) -> bool:
    """
    Detect if there's a face in the image using DNN.

    Args:
        cv_image: OpenCV image (BGR format)
        min_confidence: Minimum confidence threshold (0-1)

    Returns:
        True if a face is detected with sufficient confidence
    """
    net = _get_face_net()
    h, w = cv_image.shape[:2]

    # Create blob from image (resize to 300x300 as expected by the model)
    blob = cv2.dnn.blobFromImage(
        cv2.resize(cv_image, (300, 300)),
        1.0,
        (300, 300),
        (104.0, 177.0, 123.0),
    )

    net.setInput(blob)
    detections = net.forward()

    # Check if any face detected with sufficient confidence
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence >= min_confidence:
            return True

    return False


def detect_rotation_by_face(image: Image.Image) -> int | None:
    """
    Detect the correct rotation using face detection.

    Tries each 90-degree rotation and returns the one where a face is detected.

    Args:
        image: PIL Image to analyze

    Returns:
        Rotation angle (0, 90, 180, 270) if face found, None otherwise
    """
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Try original orientation first
    if detect_face(cv_image):
        return 0

    h, w = cv_image.shape[:2]
    center = (w / 2, h / 2)

    # Try 90, 180, 270 degree rotations
    for angle in [90, 180, 270]:
        rotation_matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)

        # Calculate new dimensions after rotation
        cos_a = abs(rotation_matrix[0, 0])
        sin_a = abs(rotation_matrix[0, 1])
        new_w = int(h * sin_a + w * cos_a)
        new_h = int(h * cos_a + w * sin_a)

        # Adjust rotation matrix for new dimensions
        rotation_matrix[0, 2] += (new_w - w) / 2
        rotation_matrix[1, 2] += (new_h - h) / 2

        rotated = cv2.warpAffine(cv_image, rotation_matrix, (new_w, new_h))

        if detect_face(rotated):
            return angle

    return None  # No face detected in any orientation


def score_rotation(image: Image.Image) -> float:
    """
    Score an image orientation based on edge alignment.

    Higher scores indicate better alignment (more horizontal/vertical edges).
    Uses Hough line detection to find dominant line angles.

    Args:
        image: PIL Image to analyze

    Returns:
        Score where higher = better orientation
    """
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Detect lines using probabilistic Hough transform
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=50,
        minLineLength=30,
        maxLineGap=10,
    )

    if lines is None:
        return 0.0

    # Score based on how many lines are near horizontal (0) or vertical (90)
    score = 0.0
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        angle = abs(angle) % 90

        # Lines at 0 or 90 get high scores, lines at 45 get low scores
        if angle < 10 or angle > 80:
            line_length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            score += line_length

    return score


def detect_rotation_by_edges(image: Image.Image) -> int:
    """
    Detect the best rotation angle based on edge alignment (Hough lines).

    Tests 0, 90, 180, and 270 rotations and returns the best one.

    Args:
        image: PIL Image to analyze

    Returns:
        Best rotation angle in degrees (0, 90, 180, or 270)
    """
    best_angle = 0
    best_score = -1.0

    for angle in [0, 90, 180, 270]:
        if angle == 0:
            rotated = image
        else:
            rotated = image.rotate(-angle, expand=True)

        score = score_rotation(rotated)

        if score > best_score:
            best_score = score
            best_angle = angle

    return best_angle


def detect_rotation(image: Image.Image) -> int:
    """
    Detect the best rotation angle for an image.

    Uses face detection first (more reliable for photos of people),
    then falls back to edge-based detection.

    Args:
        image: PIL Image to analyze

    Returns:
        Best rotation angle in degrees (0, 90, 180, or 270)
    """
    # Try face detection first - most reliable for photos with people
    face_angle = detect_rotation_by_face(image)
    if face_angle is not None:
        return face_angle

    # Fall back to edge-based detection for landscapes, objects, etc.
    return detect_rotation_by_edges(image)


def auto_rotate(image: Image.Image) -> tuple[Image.Image, int]:
    """
    Automatically rotate an image to the correct orientation.

    Args:
        image: PIL Image to rotate

    Returns:
        Tuple of (rotated image, angle applied)
    """
    angle = detect_rotation(image)

    if angle == 0:
        return image, 0

    rotated = image.rotate(-angle, expand=True)
    return rotated, angle


def rotate_images(images: list[Image.Image]) -> list[tuple[Image.Image, int]]:
    """
    Auto-rotate a list of images.

    Args:
        images: List of PIL Images

    Returns:
        List of tuples (rotated image, angle applied)
    """
    return [auto_rotate(img) for img in images]
