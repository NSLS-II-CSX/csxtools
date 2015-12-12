import numpy as np
from ..ext import fastccd as fccd


def get_fastccd_images(light, dark = None):
    """Retreive the

    """


def correct_images(images, dark=None, flat=None, gain=(1, 4, 8)):
    """Subtract backgrond and gain correct images

    This routine subtrtacts the backgrond and corrects the images
    for the multigain fastccd ADC.

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

    Returns
    -------
    array_like
        Array of corrected images of shape (N, y, x)

    """

    if dark is None:
        dark = np.zeros(images.shape[-2:], dtype=np.float32)
        dark = np.array((dark, dark, dark))
    if flat is None:
        flat = np.ones(images.shape[-2:], dtype=np.float32)

    return fccd.correct_images(images, dark, flat, gain)
