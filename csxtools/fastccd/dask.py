from typing import Tuple

import numpy as np
from dask.array import Array as DaskArray
from numpy.typing import ArrayLike

GAIN_8 = 0x0000
GAIN_2 = 0x8000
GAIN_1 = 0xC000
BAD_PIXEL = 0x2000
PIXEL_MASK = 0x1FFF


def correct_images(images: DaskArray, dark: ArrayLike, flat: ArrayLike, gain: Tuple[float, float, float]):
    """Apply intensity corrections to a stack of images.

    Parameters
    ----------
    images : DaskArray
        Input array of images to correct; has shape (N, y, x)  where N is the
        number of images and x and y are the image size.
    dark : ArrayLike
        Input array of dark images. This should be of shape (3, y, x).
        dark[0] is the GAIN_8 (most sensitive setting) dark image with
        dark[2] being the GAIN_1 (least sensitive) dark image.
    flat : ArrayLike
        Input array for the flatfield correction. This should be of shape
        (y, x)
    gain : Tuple[float, float, float]
        These are the gain multiplication factors for the three different
        gain settings

    // Note GAIN_1 is the least sensitive setting which means we need to multiply the
    // measured values by 8. Conversly GAIN_8 is the most sensitive and therefore
    // does not need a multiplier
    """

    # Shape checking:
    if dark.ndim != 3:
        raise ValueError(f"Expected 3D array, got {dark.ndim}D array for darks")
    if dark.shape[0] != 3:
        raise ValueError(f"Expected 3 dark images, got {dark.shape[0]}")
    if dark.shape[-2:] != images.shape[-2]:
        raise ValueError(f"Dark images shape {dark.shape[-2:]} does not match images shape {images.shape[-2]}")
    if flat.shape != images.shape[-2:]:
        raise ValueError(f"Flatfield shape {flat.shape} does not match images shape {images.shape[-2]}")

    corrected = np.where(images & BAD_PIXEL, np.NaN, images)
    corrected = np.where(images & GAIN_1, flat * gain[-1] * (corrected - dark[-1, ...]), corrected)
    corrected = np.where(images & GAIN_2, flat * gain[-2] * (corrected - dark[-2, ...]), corrected)
    corrected = np.where(images & GAIN_8, flat * gain[-3] * (corrected - dark[-3, ...]), corrected)

    return corrected
