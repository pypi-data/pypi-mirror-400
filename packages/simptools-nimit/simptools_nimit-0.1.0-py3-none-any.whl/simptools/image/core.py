import cv2

def load_image(path: str):
    if not path:
        raise ValueError("Image path must be provided")
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image from {path}")
    return f"Image loaded from {path}", img

def show_image(image, title: str = "Image"):
    if image is None:
        raise ValueError("No image provided to show")
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def save_image(path: str, image):
    if not path:
        raise ValueError("Path must be provided to save image")
    if image is None:
        raise ValueError("No image provided to save")
    success = cv2.imwrite(path, image)
    if not success:
        raise ValueError("Failed to save image. Check path and file extension")
    return f"Image saved to {path}"

def resize_image(image, width: int | None = None, height: int | None = None):
    if image is None:
        raise ValueError("No image provided to resize")
    if width is None and height is None:
        raise ValueError("At least one of width or height must be provided")
    (h, w) = image.shape[:2]
    if width is None:
        ratio = height / float(h)
        dim = (int(w * ratio), height)
    elif height is None:
        ratio = width / float(w)
        dim = (width, int(h * ratio))
    else:
        dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

def crop_image(image, crop_percent: int):
    if image is None:
        raise ValueError("No image provided to crop")
    if not (0 <= crop_percent < 50):
        raise ValueError("crop_percent must be between 0 and 49")
    (h, w) = image.shape[:2]
    crop_h = int(h * (crop_percent / 100))
    crop_w = int(w * (crop_percent / 100))
    return image[crop_h:h - crop_h, crop_w:w - crop_w]

def get_image_shape(image):
    if image is None:
        raise ValueError("No image provided")
    return f"Image Height: {image.shape[0]}, Width: {image.shape[1]}, Channels: {image.shape[2] if len(image.shape) > 2 else 1}"

def convert_color(image, mode: str):
    if image is None:
        raise ValueError("No image provided")
    if mode.lower() in ("gray", "grey"):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif mode.lower() == "rgb":
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif mode.lower() == "bgr":
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        raise ValueError("Unsupported color mode. Supported: 'GRAY', 'RGB', 'BGR'")

def flip_image(image, direction: str):
    if image is None:
        raise ValueError("No image provided")
    dir_map = {"horizontal": 1, "h": 1, "vertical": 0, "v": 0, "both": -1, "b": -1}
    if direction.lower() not in dir_map:
        raise ValueError("Unsupported flip direction. Use 'horizontal', 'vertical', 'both'")
    return cv2.flip(image, dir_map[direction.lower()])

def rotate_image(image, angle: int):
    if image is None:
        raise ValueError("No image provided")
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, M, (w, h))
