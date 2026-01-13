from typing import List, Tuple, Optional


import numpy as np
import cv2

from .base_predictor import BasePredictor
from ..utils import np_ops


class ClassificationPredictor(BasePredictor):
    def __init__(self, config: dict) -> None:
        super().__init__(config)

    def postprocess(
        self, 
        preds: np.ndarray, 
        orig_imgs: Optional[List[np.ndarray]] = None
    ) -> Tuple[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        preds = preds[0] if isinstance(preds, (list, tuple)) else preds
        top5_idx = np.argsort(preds, axis=1)[:, -5:][:, ::-1]
        top5 = np.take_along_axis(preds, top5_idx, axis=1)
        return preds, (top5, top5_idx)