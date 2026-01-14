import cv2
import numpy as np
from typing import Optional, Tuple


# ---------- Loading / Saving ----------

def load_image(path: str) -> np.ndarray:
    """
    Load an image from disk (BGR format).

    :param path: Path to the image file
    :return: Image as NumPy array
    """
    if not path:
        raise ValueError("Image path must be provided")

    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image from '{path}'")

    return img


def save_image(path: str, image: np.ndarray) -> None:
    """
    Save an image to disk.

    :param path: Output file path
    :param image: Image to save
    """
    if not path:
        raise ValueError("Path must be provided to save image")
    if image is None:
        raise ValueError("No image provided to save")

    if not cv2.imwrite(path, image):
        raise IOError("Failed to save image. Check path and file extension")


# ---------- Display ----------

def show_image(image: np.ndarray, title: str = "Image") -> None:
    """
    Display an image in a window.

    :param image: Image to display
    :param title: Window title
    """
    if image is None:
        raise ValueError("No image provided to show")

    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ---------- Image Info ----------

def get_image_shape(image: np.ndarray) -> Tuple[int, int, int]:
    """
    Get image dimensions.

    :param image: Input image
    :return: (height, width, channels)
    """
    if image is None:
        raise ValueError("No image provided")

    h, w = image.shape[:2]
    c = image.shape[2] if image.ndim == 3 else 1
    return h, w, c


# ---------- Transformations ----------

def resize_image(
    image: np.ndarray,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> np.ndarray:
    """
    Resize image while optionally preserving aspect ratio.

    :param image: Input image
    :param width: Target width
    :param height: Target height
    """
    if image is None:
        raise ValueError("No image provided to resize")
    if width is None and height is None:
        raise ValueError("At least one of width or height must be provided")

    h, w = image.shape[:2]

    if width is None:
        ratio = height / float(h)
        dim = (int(w * ratio), height)
    elif height is None:
        ratio = width / float(w)
        dim = (width, int(h * ratio))
    else:
        dim = (width, height)

    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)


def crop_image(image: np.ndarray, crop_percent: int) -> np.ndarray:
    """
    Crop an image evenly on all sides by a percentage.

    :param image: Input image
    :param crop_percent: Percentage to crop from each side (0–49)
    """
    if image is None:
        raise ValueError("No image provided to crop")
    if not (0 <= crop_percent < 50):
        raise ValueError("crop_percent must be between 0 and 49")

    h, w = image.shape[:2]
    crop_h = int(h * crop_percent / 100)
    crop_w = int(w * crop_percent / 100)

    return image[crop_h:h - crop_h, crop_w:w - crop_w]


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate an image around its center (may clip corners).

    :param image: Input image
    :param angle: Rotation angle in degrees
    """
    if image is None:
        raise ValueError("No image provided")

    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h))


def flip_image(image: np.ndarray, direction: str) -> np.ndarray:
    """
    Flip an image.

    :param direction: 'horizontal', 'vertical', or 'both'
    """
    if image is None:
        raise ValueError("No image provided")

    dir_map = {
        "horizontal": 1, "h": 1,
        "vertical": 0, "v": 0,
        "both": -1, "b": -1
    }

    key = direction.lower()
    if key not in dir_map:
        raise ValueError("Unsupported flip direction. Use 'horizontal', 'vertical', or 'both'")

    return cv2.flip(image, dir_map[key])


# ---------- Color Conversion ----------

def convert_color(image: np.ndarray, mode: str) -> np.ndarray:
    """
    Convert image color space.

    Assumes input image is BGR (OpenCV default).

    :param mode: 'gray', 'rgb', or 'bgr'
    """
    if image is None:
        raise ValueError("No image provided")

    mode = mode.lower()

    if mode in ("gray", "grey"):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif mode == "rgb":
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif mode == "bgr":
        return image.copy()
    else:
        raise ValueError("Unsupported color mode. Supported: 'gray', 'rgb', 'bgr'")
