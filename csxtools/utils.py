import numpy as np
import time as ttime
from databroker import get_images
from pims import pipeline

from .fastccd import correct_images
from .image import rotate90, stackmean
from .settings import detectors

import logging
logger = logging.getLogger(__name__)


def get_fastccd_images(light_header, dark_headers=None,
                       flat=None, gain=(1, 4, 8), tag=None, roi=None):
    """Retreive and correct FastCCD Images from associated headers

    Retrieve FastCCD Images from databroker and correct for:

    -   Bad Pixels (converted to ``np.nan``)
    -   Backgorund.
    -   Multigain bits.
    -   Flatfield correction.
    -   Rotation (returned images are rotated 90 deg cw)

    Parameters
    ----------
    light_header : databorker header
        This header defines the images to convert

    dark_headers : tuple of 3 databroker headers , optional
        These headers are the dark images. The tuple should be formed
        from the dark image sets for the Gain 8, Gain 2 and Gain 1
        (most sensitive to least sensitive) settings. If a set is not
        avaliable then ``None`` can be entered.

    flat : array_like
        Array to use for the flatfield correction. This should be a 2D
        array sized as the last two dimensions of the image stack.

    gain : tuple
        Gain multipliers for the 3 gain settings (most sensitive to
        least sensitive)

    tag : string
        Data tag used to retrieve images. Used in the call to
        ``databroker.get_images()``. If `None`, use the defualt from
        the settings.

    roi : tuple
        coordinates of the upper-left corner and width and height of
        the ROI: e.g., (x, y, w, h) or (col, row, col_len, row_len)

    Returns
    -------
    image : a corrected pims.pipeline of the data

    """

    if tag is None:
        tag = detectors['fccd']

    # Now lets sort out the ROI
    if roi is not None:
        # Convert ROI to start:stop from start:size
        roi[1] = roi[0] + roi[1] + 1
        roi[3] = roi[2] + roi[3] + 1

    if dark_headers is None:
        bgnd = None
        logger.warning("Processing without dark images")
    else:
        if dark_headers[0] is None:
            raise NotImplementedError("Use of header metadata to find dark"
                                      " images is not implemented yet.")

        # Read the images for the dark headers
        t = ttime.time()

        dark = []
        for i, d in enumerate(dark_headers):
            if d is not None:
                # Get the images

                bgnd_events = _get_images(d, tag, roi)

                # We assume that all images are for the background
                # TODO : Perhaps we can loop over the generator
                # If we want to do something lazy

                tt = ttime.time()
                b = get_images_to_4D(bgnd_events, dtype=np.uint16)
                logger.info("Image conversion took %.3f seconds",
                            ttime.time() - tt)

                b = correct_images(b, gain=(1, 1, 1))
                tt = ttime.time()
                b = stackmean(b)
                logger.info("Mean of image stack took %.3f seconds",
                            ttime.time() - tt)

            else:
                logger.warning("Missing dark image"
                               " for gain setting %d", i)
            dark.append(b)

        bgnd = np.array(dark)

        logger.info("Computed dark images in %.3f seconds", ttime.time() - t)

    events = _get_images(light_header, tag, roi)

    # Ok, so lets return a pims pipeline which does the image conversion

    # Crop Flatfield image
    if flat is not None and roi is not None:
        flat = _crop(flat, roi)

    return _correct_fccd_images(events, bgnd, flat, gain)


def get_images_to_4D(images, dtype=None):
    """Convert image stack to 4D numpy array

    This function converts an image stack from
    :func: get_images() into a 4D numpy ndarray of a given datatype.
    This is useful to just get a simple array from detector data

    Parameters
    ----------
    images : the result of get_images()
    dtype : the datatype to use for the conversion

    Example
    -------
    >>> header = DataBroker[-1]
    >>> images = get_images(header, "my_detector')
    >>> a = get_images_to_4D(images, dtype=np.float32)

    """
    im = np.array([np.asarray(im, dtype=dtype) for im in images],
                  dtype=dtype)
    return im


def _get_images(header, tag, roi=None):
    t = ttime.time()
    images = get_images(header, tag)
    t = ttime.time() - t
    logger.info("Took %.3f seconds to read data using get_images", t)

    if roi is not None:
        images = _crop_images(images, roi)

    return images


@pipeline
def _correct_fccd_images(image, bgnd, flat, gain):
    image = correct_images(image, bgnd, flat, gain)
    image = rotate90(image, 'cw')
    return image


@pipeline
def _crop_images(image, roi):
    return _crop(image, roi)


def _crop(image, roi):
    image_shape = image.shape
    # Assuming ROI is specified in the "rotated" (correct) orientation
    roi = [image_shape[-2]-roi[3], roi[0], image_shape[-1]-roi[1], roi[2]]
    return image.T[roi[1]:roi[3], roi[0]:roi[2]].T
