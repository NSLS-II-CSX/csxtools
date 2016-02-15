import numpy as np
import time as ttime
from databroker import get_images
from pims import pipeline

from .fastccd import correct_images
from .image import rotate90

import logging
logger = logging.getLogger(__name__)


def get_fastccd_images(light_header, dark_headers=None,
                       flat=None, gain=(1, 4, 8), tag='fccd_image'):
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
        ``databroker.get_images()``

    Returns
    -------
    image : array_like
        This is the corrected detector array

    """

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

                bgnd_events = _get_images(d, tag)

                # We assume that all images are for the background
                # TODO : Perhaps we can loop over the generator
                # If we want to do something lazy

                b = get_images_to_4D(bgnd_events, dtype=np.uint16)

                b = correct_images(b, gain=(1, 1, 1))
                b = b.reshape((-1, b.shape[-2], b.shape[-1]))
                b = np.nanmean(b, axis=0)

            else:
                logger.warning("Missing dark image"
                               " for gain setting %d", i)
            dark.append(b)

        bgnd = np.array(dark)

        logger.info("Computed dark images in %.3f seconds", ttime.time() - t)

    events = _get_images(light_header, tag)

    # Ok, so lets now make a generator

    return [_correct_fccd_images(event, bgnd, flat, gain)
            for event in events]


@pipeline
def _correct_fccd_images(image, bgnd, flat, gain):
    return rotate90(correct_images(image, bgnd, flat, gain), 'cw')


def _get_images(header, tag):
    t = ttime.time()
    images = get_images(header, tag)
    t = ttime.time() - t
    logger.info("Took %.3f seconds to read data using get_images", t)

    return images


def get_images_to_4D(images, dtype=None):
    im = np.array([np.asarray(im, dtype=dtype) for im in images],
                  dtype=dtype)
    return im
