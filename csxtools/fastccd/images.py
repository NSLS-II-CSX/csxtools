import logging
import time as ttime

import numpy as np

from ..ext import fastccd
from .dask import correct_images as dask_correct_images

logger = logging.getLogger(__name__)


def correct_images(images, dark=None, flat=None, gain=(1, 4, 8), *, dask=False):
    """Subtract backgrond and gain correct images

    This routine subtrtacts the backgrond and corrects the images
    for the multigain FastCCD ADC.

    Parameters
    ----------
    in : array_like
        Input array of images to correct of shape (N, y, x)  where N is the
        number of images and x and y are the image size.
    dark : array_like, optional
        Input array of dark images. This should be of shape (3, y, x).
        dark[0] is the gain 8 (most sensitive setting) dark image with
        dark[2] being the gain 1 (least sensitive) dark image.
    flat : array_like, optional
        Input array for the flatfield correction. This should be of shape
        (y, x)
    gain : tuple, optional
        These are the gain multiplication factors for the three different
        gain settings
    dask : bool, optional
        Do computation in dask instead of in C extension over full array.
        This returns a DaskArray or DaskArrayClient with pending execution instead of a numpy array.
        You can use the .compute() method to get the numpy array.
        Default is False.

    Returns
    -------
    array_like
        Array of corrected images of shape (N, y, x)

    """

    t = ttime.time()

    logger.info("Correcting image stack of shape %s", images.shape)

    if dark is None:
        dark = np.zeros(images.shape[-2:], dtype=np.float32)
        dark = np.array((dark, dark, dark))
        logger.info("Not correcting for darkfield. No input.")
    if flat is None:
        flat = np.ones(images.shape[-2:], dtype=np.float32)
        logger.info("Not correcting for flatfield. No input.")
    else:
        flat = np.asarray(flat, dtype=np.float32)

    if dask:
        data = dask_correct_images(images.astype(np.uint16), dark, flat, gain)
    else:
        data = fastccd.correct_images(images.astype(np.uint16), dark, flat, gain)
    t = ttime.time() - t

    logger.info("Corrected image stack in %.3f seconds", t)

    return data
