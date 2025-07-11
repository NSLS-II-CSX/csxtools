import numpy as np
from ..ext import axis1
import time as ttime

import logging

logger = logging.getLogger(__name__)


def correct_images_axis(images, dark=None, flat=None):
    """Subtract background and correct images

    This routine subtracts the background and corrects the images
    for AXIS1 detector.

    Parameters
    ----------
    images : array_like
        Input array of images to correct of shape (N, y, x)  where N is the
        number of images and x and y are the image size.
    dark : array_like, optional
        Input array of dark images. This should be of shape (y, x)
    flat : array_like, optional
        Input array for the flatfield correction. This should be of shape
        (y, x)

    Returns
    -------
    array_like
        Array of corrected images of shape (N, y, x)

    """

    t = ttime.time()

    logger.info("Correcting image stack of shape %s", images.shape)

    if dark is None:
        dark = np.zeros(images.shape[-2:], dtype=np.float32)
        logger.info("Not correcting for darkfield. No input.")
    if flat is None:
        flat = np.ones(images.shape[-2:], dtype=np.float32)
        logger.info("Not correcting for flatfield. No input.")
    else:
        flat = np.asarray(flat, dtype=np.float32)

    data = axis1.correct_images_axis(images.astype(np.uint16), dark, flat)
    t = ttime.time() - t

    logger.info("Corrected image stack in %.3f seconds", t)

    return data
