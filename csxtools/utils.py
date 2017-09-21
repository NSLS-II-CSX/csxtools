import numpy as np
import dask.array as da
import time as ttime

from databroker import Broker

from .image import rotate90, stackmean
from .settings import detectors

import logging
logger = logging.getLogger(__name__)


def get_fastccd_images(light_header, dark_headers=None,
                       flat=None, gain=(1, 4, 8), config_name='csx',
                       device_tag='fccd', overscan=None):
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

    config_name : string
        Databroker config string (for example 'csx')

    device_tag : string
        Device tag used to get information on the fccd device

    device_stream : string
        Stream to use for fccd device

    overscan : integer
        Number of overscan rows in the data. If None, read from the
        configuration attrs of the header for that information.

    Returns
    -------
        An uncomputed dask array of the corrected data.

    """

    image_tag = "{}_image".format(device_tag)

    if overscan is None:
        cfg = header.config_data(device_tag)[device_stream][0]
        if "{}_cam_overscan".format(device_tag) in cfg:
            overscan = cfg["{}_cam_overscan".format(device_tag)]
        else:
            raise RuntimeError("Could not find overscan information in"
                               " header config. Please specify")

    if dark_headers == (None, None, None):
        bgnd = None
        logger.warning("Processing without dark images")
    else:
        if dark_headers is None:
            dark_headers = _get_dark_stack(config_tag, device_tag, stream_tag)
            for d,g in zip(('8x', '2x', '1x'), dark_headers):
                logger.info("Using dark images from "
                            "{} for gain {}".format(g, d))


        # Read the images for the dark headers
        t = ttime.time()

        dark = []
        for g, d in zip(('8x', '2x', '1x'), dark_headers):
            if d is not None:
                # Get the images

                bgnd_stack = _get_images(d, image_tag)
                _s = bgnd_stack.shape

                bgnd_stack = bgnd_stack.reshape((-1, _s[-2], _s[-1]))
                bgnd_stack = da.nanmean(bgnd_stack, axis=0)

            else:
                logger.warning("Missing dark image for gain"
                               " setting {}".format(g))

            dark.append(bgnd_stack)

        dark = da.stack(dark).compute()

        logger.info("Computed dark images in %.3f seconds", ttime.time() - t)

    light = _get_images(light_header, image_tag)
    light = _correct_images(light, dark, gain)

    # Now remove overscan and return

    if overscan > 0:
        light, overscan_data = _extract_overscan(light, overscan)
    else:
        overscan_data = None

    return light, overscan_data


def _get_images(header, tag):
    images = header.data(tag)
    images = da.stack(list(images), axis=0)
    return images


def _extract_overscan(stack, overscan):
    rows = stack.shape[-1]
    cols = stack.shape[-2] / 2

    data_rows_1 = [x for x in range(rows) if ((x % (10 + overscan)) < 10)]
    data_rows_2 = [x for x in range(rows) if ((x % (10 + overscan)) >= overscan)]

    os_rows_1 = [x for x in range(rows) if ((x % (10 + overscan)) >= 10)]
    os_rows_2 = [x for x in range(rows) if ((x % (10 + overscan)) < overscan)]

    data_stack = da.concatenate([stack[:,:,:cols,data_rows_1],
                                 stack[:,:,cols:,data_rows_2]],
                                 axis=2)

    os_stack= da.concatenate([stack[:,:,:cols,os_rows_1],
                              stack[:,:,cols:,os_rows_2]],
                              axis=2)

    return data_stack, os_stack


def _get_dark_stack(header, name, device, stream):

    exposure = header.config_data(device)[stream]
    exposure = exposure[0]["{}_cam_acquire_time".format(device)]

    db = Broker.named(name, auto_register=False)

    dark_headers = list()

    for gain in ('auto', '2x', '1x'):

        query = {'$and': [{"{}.gain".format(device): gain},
                          {"{}.image".format(device): 'dark'},
                          {"{}.exposure".format(device): exposure}]}

        results = db(stop_time=header['start']['time'], **query)

        try:
            h = next(iter(results))
        except StopIteration:
            if gain == 'auto':
                raise RuntimeError("Could not locate dark image data "
                                   "for auto (8x) gain by searching"
                                   " metadata.")
            else:
                dark_headers.append(None)
        else:
            dark_headers.append(h['start']['uid'])

    return dark_headers


def get_fastccd_flatfield(light, dark, flat=None, limits=(0.6, 1.4)):
    """Calculate a flatfield from two headers

    This routine calculates the flatfield using the
    :func:calculate_flatfield() function after obtaining the images from
    the headers.

    Parameters
    ----------
    light : databroker header
        The header containing the light images
    dark : databroker header
        The header from the run containin the dark images
    flat : flatfield image (optional)
        The array to be used for the initial flatfield

    Returns
    -------
    array_like
        Flatfield correction
    """
    images = get_images_to_3D(get_fastccd_images(light, dark, flat))
    images = stackmean(images)
    flat = calculate_flatfield(images, limits)
    removed = np.sum(np.isnan(flat))
    if removed != 0:
        logger.warning("Flatfield correction removed %d pixels (%.2f %%)" %
                       (removed, removed * 100 / flat.size))
    return flat


def fccd_mask():
    """Return the initial flatfield mask for the FastCCD

    Returns
    -------
    np.array of flatfield

    """
    flat = np.ones((960, 960))
    flat[120:250, 0:480] = np.nan
    flat[:, 476:484] = np.nan
    flat = np.rot90(flat)

    return flat


def _correct_images(light, dark, gain=(1, 4, 8)):

    gain1 = ((light & 0xC000) == 0xC000)
    gain2 = ((light & 0x8000) == 0x8000)
    gain8 = ((light & 0xE000) == 0x0000)

    gain = (gain1 * gain[2]) + (gain2 * gain[1]) + (gain8 * gain[0])
    bgnd = (dark[0] * gain8) + (dark[1] * gain2) + (dark[2] * gain1)

    images = (light - bgnd) * gain
    return images

