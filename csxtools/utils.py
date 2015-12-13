import numpy as np
from databroker import get_images
from .fastccd import correct_images
from .image import rotate90


def get_fastccd_images(light_header, dark_headers=(None, None, None),
                       tag='fccd_image_lightfield'):
    """Retreive the FastCCD Images from associated headers

    """
    if dark_headers[0] == None:
        raise NotImplemented("Use of header metadata to find dark images is"
                             "not implemented yet.")

    # Read the images for the dark headers

    dark = []
    for d in dark_headers:
        if d is not None:
            b = np.asarray(get_images(d, tag)[0],
                           dtype=np.uint16)
            b = np.nanmean(correct_images(b, gain=(1, 1, 1)), axis=0)
        dark.append(b)

    bgnd = np.array(dark)
    data = np.asarray(get_images(light_header, tag)[0], dtype=np.uint16)
    data = correct_images(data, bgnd)
    data = rotate90(data, 'cw')
    return data
