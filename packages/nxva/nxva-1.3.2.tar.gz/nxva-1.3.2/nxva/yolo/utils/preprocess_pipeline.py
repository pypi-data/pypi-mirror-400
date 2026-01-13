import cv2
import numpy as np
from PIL import Image

from .np_ops import letterbox, classify_transforms

# ===== Operators =====

def resize_letterbox_batch(imgs, input_shape):
    """Apply letterbox resize on batch."""
    return np.stack([letterbox(img, input_shape) for img in imgs])

def bgr_to_rgb(arr):
    """Convert BGR to RGB (batch)."""
    return arr[..., ::-1] if arr.shape[-1] == 3 else arr

def hwc_to_chw(arr):
    """HWC -> CHW for batch."""
    return arr.transpose(0, 3, 1, 2)

def normalize(arr):
    """Normalize [0,255] -> [0,1]."""
    return arr.astype(np.float32) / 255.0

def to_uint8(arr):
    """Cast to uint8."""
    return arr.astype(np.uint8)

def to_contiguous(arr):
    """Ensure memory is contiguous."""
    return np.ascontiguousarray(arr)

def classify_stack(imgs, transforms):
    img_stack = np.stack(
        [transforms(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))) for im in imgs]
    )
    return img_stack


# ===== Pipeline Builder =====

def build_preprocess_pipeline(
    *,
    version: str,
    task: str,
    weights: str,
    input_shape=None,
    do_letterbox=True,
    do_bgr_to_rgb=True,
):       
    # Auto rules
    do_transpose = not weights.endswith(('.hef', '.axmodel'))
    do_normalize = not weights.endswith(('.hef', '.axmodel'))

    # normalize input_shape format
    if isinstance(input_shape, int):
        input_shape = (input_shape, input_shape)
    elif isinstance(input_shape, (list, tuple)):
        input_shape = tuple(input_shape)

    steps = []
    if task == 'classify':
        transforms = classify_transforms(size=input_shape)
        steps.append(lambda imgs: classify_stack(imgs, transforms))
    else:
        # 1. Letterbox
        if do_letterbox:
            steps.append(lambda imgs: resize_letterbox_batch(imgs, input_shape))

        # 2. Color
        if do_bgr_to_rgb:
            steps.append(bgr_to_rgb)

        # 3. HWC -> CHW
        if do_transpose:
            steps.append(hwc_to_chw)

        # 4. Normalize or uint8
        if do_normalize:
            steps.append(normalize)
        else:
            steps.append(to_uint8)

        # 5. Contiguous
        steps.append(to_contiguous)

    # ==== Pipeline Callable ====
    def pipeline(imgs):
        """Process one image or batch."""
        # Allow single image input
        single = False
        if isinstance(imgs, np.ndarray) and imgs.ndim == 3:
            imgs = imgs[None, ...]  # add batch dim
            single = True

        # Apply steps
        for fn in steps:
            imgs = fn(imgs)

        return imgs[0] if single else imgs

    return pipeline
