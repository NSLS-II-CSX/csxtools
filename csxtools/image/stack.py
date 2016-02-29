import numpy as np
from ..ext import image as extimage


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


def stacksum(array):
    """Cacluate the sum of a stack

    This function calculates the sum of a stack of images (or any array).
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
        tuple of 2 arrays of the sum and number of points in the sum
    """
    X, Y = extimage.stackprocess(array, 0)
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


def ccdmean(images):
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


def ccdsum(images):
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


def convert_to_3d(images):
    """Return a 3D array from the "slicerator" object

    Parameters
    ----------
    slicerator object : generator returning pims images
        This is the output of get_fastccd_images

    Returns
    -------
    array: 3D numpy array
    """

    # images = [np.asarray(im) for im in images]
    ims = images[0]
    for im in images[1:]:
        ims = np.vstack((ims, im))

    return ims
