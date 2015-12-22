from ..ext import phocount as ph


def phocount(data, thresh, nsum=3):
    """Do single photon counting on CCD image

    This routine does single photon counting by cluster analysis. The image
    is searched for bright pixels within a threshold and then the energy
    deposited by each photon is calculated.

    Parameters
    ----------
    data : array_like
        Stack of CCD images. This array should be of shape (N, y, x) where
        N is the number of images
    thresh : tuple
        Threshold to use for identifying photons. This should be a tuple of
        (min, max)
    nsum : int
        The number of pixels to use to calculate the energy deposited by the
        photon. This should be 0 < nsum <= 9.

    Returns
    -------
    tuple
        Two arrays are returned. The first is an array of size (N, y, x)
        where the elements are the integrated energy calculated for each
        photon hit. The second array is the standard deviation for the
        integrated intensity on each photon hit.
    """
    return ph(data, thresh, nsum)
