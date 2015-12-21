from ..ext import phocount as ph


def phocount(data, thresh, nsum=3):
    """Do single photon counting on CCD image

    This routine does single photon counting by cluster analysis. The image
    is searched for bright pixels within a threshold
    """
    return ph(data, thresh, nsum)
