import cv2
import numpy as np

def identity_transform(x: np.ndarray) -> np.ndarray:
    """Identity transform - returns input as is."""
    return x


def yolo_transform(x: np.ndarray) -> np.ndarray:
    """YOLO transform - normalize to [0, 1] range."""
    return x / 255.0


def v5_pose_transform(x: np.ndarray) -> np.ndarray:
    """
    YOLOv5 pose transform - reshape and normalize.
    Input: (1, 320, 320, 3)
    Output: (1, 160, 160, 12)
    """
    # Reshape: 1x320x320x3 -> (-1, 160, 2, 160, 2, 3)
    x = x.reshape(-1, 160, 2, 160, 2, 3)
    
    # Transpose: mix block (2x2) with channel
    x = np.transpose(x, (0, 2, 4, 5, 1, 3))  # (1, 2, 2, 3, 160, 160)
    
    # Reshape: (1, 12, 160, 160) but keep BHWC format
    x = x.reshape(x.shape[0], 160, 160, 12)
    x /= 255.0
    
    return x


def ir_transform(imgs: np.ndarray) -> np.ndarray:
    """
    IR (face recognition) transform.
    Resize to 112x112, convert BGR to RGB, normalize to [-1, 1].
    """
    imgs_out = np.empty((imgs.shape[0], 112, 112, 3), dtype=np.float32)
    
    for idx in range(imgs.shape[0]):
        img = imgs[idx]
        
        # Ensure correct dtype
        if img.dtype != np.float32:
            img = img.astype(np.float32)
        
        # Resize
        img = cv2.resize(img, (112, 112), interpolation=cv2.INTER_AREA)
        
        # BGR -> RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        imgs_out[idx] = img
    
    # Normalize to [-1, 1]
    imgs_out /= 255.0
    imgs_out = (imgs_out - 0.5) / 0.5
    
    return imgs_out


def reid_transform(imgs: np.ndarray) -> np.ndarray:
    """
    ReID transform - ImageNet normalization.
    Input: (N, H, W, 3), value range [0, 255]
    Output: Normalized with ImageNet mean/std
    """
    imgs = imgs.astype(np.float32) / 255.0
    
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    
    imgs = (imgs - mean) / std  # Broadcasting
    return imgs


def par_transform(img: np.ndarray) -> np.ndarray:
    """
    PAR (person attribute recognition) transform.
    Convert BGR to RGB, normalize with CLIP mean/std, convert to CHW format.
    """
    clip_mean = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
    clip_std = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)
    
    # BGR -> RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    
    # Normalize
    img = (img - clip_mean) / clip_std
    
    # CHW format
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, 0)  # [1, 3, H, W]
    
    return img.astype(np.float32)