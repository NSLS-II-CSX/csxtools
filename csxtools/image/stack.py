import numpy as np
from ..ext import image as extimage

import logging
logger = logging.getLogger(__name__)


def stackmean(array):
    """Cacluate the mean of a stack

    This function calculates the mean of a stack of images (or any array).
    It ignores values that are np.NAN and does not include them in the mean
    calculation. It assumes an array of shape (.. i, j, x, y) where x and y
    are the size of the returned array (x, y).

    Parameters
    ----------
    array : array_like
        Input array of at least 3 dimensions.

    Returns
    -------
    array
        2D Array of mean of stack.
    """
    X, Y = extimage.stackprocess(array, 1)
    return X


def stacksum(array, norm=True):
    """Cacluate the sum of a stack

    This function calculates the sum of a stack of images (or any array).
    It ignores values that are np.NAN and does not include them in the sum
    calculation. It assumes an array of shape (.. i, j, x, y) where x and y
    are the size of the returned array (x, y).

    The output sum is corrected for elements where NaNs are encountered if
    norm is set to True.  The values are renormalized to a sum which would
    have occured if all elements had been polulated. If no values are present
    in a stack, then NaN is returned.

    If norm is false, the actual sum is returned.

    size.

    Parameters
    ----------
    array : array_like
        Input array of at least 3 dimensions.

    Returns
    -------
    tuple
        tuple of 2 arrays of the sum and number of points in the sum
    """
    X, Y = extimage.stackprocess(array, 0)

    if norm:
        # Set zero values to NaN
        _Y = Y.astype(np.float32)
        _Y[Y == 0] = np.nan

        total_elements = array.size / (array.shape[-1] * array.shape[-2])

        X = X * (total_elements / _Y)

    return X, Y


def stackstd(array):
    """Cacluate the standard deviation of a stack

    This function calculates the standard deviation of a stack of images
    It ignores values that are np.NAN and does not include them in the sum
    calculation. It assumes an array of shape (.. i, j, x, y) where x and y
    are the size of the returned array (x, y).

    Parameters
    ----------
    array : array_like
        Input array of at least 3 dimensions.

    Returns
    -------
    tuple
        tuple of 2 arrays of the standard deviation and number of points
        in the calculation
    """
    X, Y = extimage.stackprocess(array, 3)
    return X, Y


def stackvar(array):
    """Cacluate the varience of a stack

    This function calculates the variance of a stack of images (or any array).
    It ignores values that are np.NAN and does not include them in the
    calculation. It assumes an array of shape (.. i, j, x, y) where x and y
    are the size of the returned array (x, y).

    Parameters
    ----------
    array : array_like
        Input array of at least 3 dimensions.

    Returns
    -------
    tuple
        tuple of 2 arrays of the varience and number of points in the
        calculation
    """
    X, Y = extimage.stackprocess(array, 2)
    return X, Y


def stackstderr(array):
    """Cacluate the standard error of a stack

    This function calculates the standard error of a stack of images
    (or any array).  It ignores values that are np.NAN and does not include
    them in the calculation. It assumes an array of shape (.. i, j, x, y)
    where x and y are the size of the returned array (x, y).

    Parameters
    ----------
    array : array_like
        Input array of at least 3 dimensions.

    Returns
    -------
    tuple
        tuple of 2 arrays of the standard error and number of points in the
        calculation
    """
    X, Y = extimage.stackprocess(array, 4)
    return X, Y


def images_mean(images):
    """Cacluate the mean ccd counts per event

    This function calculates the mean of ccd counts for each event. The
    input is a "slicerator" object returned by get_fastccd_images.

    Parameters
    ----------
    slicerator object : generator returning pims images
        This is the output of get_fastccd_images

    Returns
    -------
    array: 1D numpy array
    """
    return np.array([np.nanmean(stackmean(image)) for image in images])


def images_sum(images):
    """Cacluate the total ccd counts per event

    This function calculates the sum of ccd counts for each event. The
    input is a "slicerator" object returned by get_fastccd_images.

    Parameters
    ----------
    slicerator object : generator returning pims images
        This is the output of get_fastccd_images

    Returns
    -------
    array: 1D numpy array
    """
    return np.array([np.nansum(stackmean(image)) for image in images])
