import numpy as np
from ..ext import fastccd as fccd


def subtract_background(images, dark, gain=(1, 4, 8)):
    """Subtract backgrond and gain correct images

    This routine subtrtacts the backgrond and corrects the images
    for the multigain fastccd ADC.

    Parameters
    ----------
    in : array_like
        Input array of images to correct of shape (N, x, y)  where N is the
        number of images and x and y are the image size.
    dark : array_like
        Input array of dark images. This should be of shape (3, x, y).
        dark[0] is the gain 8 (most sensitive setting) dark image with
        dark[2] being the gain 1 (least sensitive) dark image.
    gain : tuple
        These are the gain multiplication factors for the three different
        gain settings

    Returns
    -------
    array_like
        Array of corrected images of shape (N, x, y)

    """

    return fccd.correct_images(images, dark)


