import numpy as np
import time as ttime
from pims import pipeline

from .fastccd import correct_images
from .image import rotate90, stackmean
from .settings import detectors
from databroker.assets.handlers import AreaDetectorHDF5TimestampHandler

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
        the ROI: e.g., (x, y, w, h)

    Returns
    -------
        A corrected pims.pipeline of the data

    """

    if tag is None:
        tag = detectors['fccd']

    # Now lets sort out the ROI
    if roi is not None:
        roi = list(roi)
        # Convert ROI to start:stop from start:size
        roi[2] = roi[0] + roi[2]
        roi[3] = roi[1] + roi[3]
        logger.info("Computing with ROI of %s", str(roi))

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
                b = get_images_to_3D(bgnd_events, dtype=np.uint16)
                logger.info("Image conversion took %.3f seconds",
                            ttime.time() - tt)

                b = correct_images(b, gain=(1, 1, 1))
                tt = ttime.time()
                b = stackmean(b)
                logger.info("Mean of image stack took %.3f seconds",
                            ttime.time() - tt)

            else:
                if (i == 0):
                    logger.warning("Missing dark image"
                                   " for gain setting 8")
                elif (i == 1):
                    logger.warning("Missing dark image"
                                   " for gain setting 2")
                elif (i == 2):
                    logger.warning("Missing dark image"
                                   " for gain setting 1")

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


def get_images_to_3D(images, dtype=None):
    """Convert image stack to 3D numpy array

    This function converts an image stack from
    :func: get_images() into a 3D numpy ndarray of a given datatype.
    This is useful to just get a simple array from detector data

    Parameters
    ----------
    images : the result of get_images()
    dtype : the datatype to use for the conversion

    Example
    -------
    >>> header = DataBroker[-1]
    >>> images = get_images(header, "my_detector')
    >>> a = get_images_to_3D(images, dtype=np.float32)

    """
    im = np.vstack([np.asarray(im, dtype=dtype) for im in images])
    return im


def _get_images(header, tag, roi=None):
    t = ttime.time()
    if isinstance(header, (list, tuple)):
        # assumes all headers are coming from the same db
        db = header[0].db
        for h in header:
            if h.db is not db:
                raise ValueError("All headers need to come from the same "
                                 "Broker instance.")
        images = db.get_images(header, tag)
    else:
        images = header.db.get_images(header, tag)
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


def get_fastccd_timestamps(header, tag='fccd_image'):
    """Return the FastCCD timestamps from the Areadetector Data File

    Return a list of numpy arrays of the timestamps for the images as
    recorded in the datafile.

    Parameters
    ----------
    header : databorker header
        This header defines the run
    tag : string
        This is the tag or name of the fastccd.

    Returns
    -------
        list of arrays of the timestamps

    """
    with header.db.reg.handler_context(
            {'AD_HDF5': AreaDetectorHDF5TimestampHandler}):
        timestamps = list(header.data(tag))

    return timestamps


def calculate_flatfield(image, limits=(0.6, 1.4)):
    """Calculate a flatfield from fluo data

    This routine calculates the flatfield correction from fluorescence data
    The image is thresholded by limits from the median value of the image.
    The flatfield is then constructed from the mean of the image divided by
    the masked (by NaN) image resulting in a true flatfield correction

    Parameters
    ----------
    image : array_like
        This is the 2D image to convert to a flatfield correction.
    limits : tuple
        Pixels outwith the median value multiplied by these limits will be
        excluded by setting to NaN.

    Returns
    -------
        Array of flatfield correction.

    """

    flat = image
    limits = np.array(limits)
    limits = np.nanmedian(image) * limits

    flat[flat < limits[0]] = np.nan
    flat[flat > limits[1]] = np.nan
    flat = np.nanmean(flat) / flat
    flat = np.rot90(flat)

    return flat



def get_fastccd_flatfield(light, dark, flat=None, limits=(0.6, 1.4), half_interval=False):
    """Calculate a flatfield from two headers 

    This routine calculates the flatfield using the
    :func:calculate_flatfield() function after obtaining the images from
    the headers.

    Parameters
    ----------
    light : databroker header
        The header containing the light images
    dark : databroker header(s)
        The header(s) from the run containin the dark images. See get_fastccd_images for details
    flat : flatfield image (optional)
        The array to be used for the initial flatfield
    limits : tuple limits used for returning corrected pixel flatfield
        The tuple setting lower and upper bound. np.nan returned value is outside bounds
    half_interval : boolean or tuple to perform calculation for only half of the FastCCD
        Default is False. If True, then the hard-code portion is retained.  Customize image 
        manipulation using a tuple of length 2 for (row_start, row_stop).


    Returns
    -------
    array_like
        Flatfield correction.  The correction is orientated as "raw data" not final data generated by get_fastccd_images().
    """
    images = get_images_to_3D(get_fastccd_images(light, dark, flat))
    images = stackmean(images)
    if half_interval:
        if isinstance(half_interval, bool):
            row_start, row_stop = (7, 486) #hard coded for the broken half of the fccd
        else:
            row_start, row_stop = half_interval
            print(row_start, row_stop)
        images[:, row_start:row_stop] = np.nan
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
