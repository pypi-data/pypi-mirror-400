from scipy import signal
import cv2
import numpy as np
from skimage import measure
from skimage.measure import regionprops
from copy import deepcopy
from scipy.signal import argrelextrema
from skimage.filters.rank import entropy
from skimage.morphology import disk


def image2mask(image: np.ndarray):
    mask = image.std(axis=2)
    mask = mask > 10
    mask = mask.astype(np.uint8)
    # 消除噪点
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    # k = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.dilate(mask, k, dst=mask, iterations=1)
    mask = cv2.erode(mask, k, dst=mask, iterations=2)
    mask = cv2.dilate(mask, k, dst=mask, iterations=1)
    return mask * 255
