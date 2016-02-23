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
    X, Y = extimage.stackmean(array, 1)
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
    X, Y = extimage.stackmean(array, 0)
    return X, Y
