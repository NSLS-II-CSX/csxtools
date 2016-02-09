import numpy as np
import time as ttime
try:
    from databroker import get_images
except ImportError:
    from dataportal import get_images

from .fastccd import correct_images
from .image import rotate90

import logging
logger = logging.getLogger(__name__)


def get_fastccd_images(light_header, dark_headers=None,
                       flat=None, gain=(1, 4, 8), tag='fccd_image_lightfield'):
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
    np.array
        Stack of corrected images

    """

    if dark_headers is None:
        bgnd = None
        logger.warning("Processing without dark images")
    else:
        if dark_headers[0] is None:
            raise NotImplemented("Use of header metadata to find dark images is"
                                 "not implemented yet.")

        # Read the images for the dark headers

        dark = []
        for i, d in enumerate(dark_headers):
            if d is not None:
                b = _get_images(d, tag)
                b = np.nanmean(correct_images(b, gain=(1, 1, 1)), axis=0)
            else:
                logger.warning("Missing dark image"
                               " for gain setting {}".format(i))
            dark.append(b)

        bgnd = np.array(dark)

    data = _get_images(light_header, tag)
    data = correct_images(data, bgnd, flat=flat, gain=gain)
    data = rotate90(data, 'cw')
    return data


def _get_images(header, tag):
    t = ttime.time()
    images = get_images(header, tag)[0]
    t = ttime.time() - t
    logger.info("Took {:.3}s to read data using get_images".format(t))

    # Convert to uint16

    images = np.asarray(images, np.uint16)

    return images
