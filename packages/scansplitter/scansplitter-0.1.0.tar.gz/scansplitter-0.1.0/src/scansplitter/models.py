"""Model download and management for face detection."""

import urllib.request
from pathlib import Path

# Model URLs from OpenCV's GitHub
PROTOTXT_URL = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
CAFFEMODEL_URL = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"

# Cache directory for models
MODELS_DIR = Path(__file__).parent / "model_cache"


def get_model_paths() -> tuple[Path, Path]:
    """Get paths to the face detection model files, downloading if needed.

    Returns:
        Tuple of (prototxt_path, caffemodel_path)
    """
    MODELS_DIR.mkdir(exist_ok=True)

    prototxt_path = MODELS_DIR / "deploy.prototxt"
    caffemodel_path = MODELS_DIR / "res10_300x300_ssd_iter_140000.caffemodel"

    if not prototxt_path.exists():
        print("Downloading face detection prototxt...")
        urllib.request.urlretrieve(PROTOTXT_URL, prototxt_path)

    if not caffemodel_path.exists():
        print("Downloading face detection model (10MB)...")
        urllib.request.urlretrieve(CAFFEMODEL_URL, caffemodel_path)

    return prototxt_path, caffemodel_path
