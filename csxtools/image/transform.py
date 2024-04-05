from ..ext import image as extimage
from .dask import rotate90 as dask_rotate90


def rotate90(a, sense="ccw", *, dask=True):
    """Rotate a stack of images by 90 degrees

    This routine rotates a stack of images by 90. The rotation is performed
    on the last two axes. i.e. For a stack of images of shape (N, y, x)
    N rotations of the image of size (y, x) are performed.

    Parameters
    ----------
        a : array_like
            Input array to be rotated. This should be of shape (N, y, x).
        sense : string
            'cw' to rotate clockwise, 'ccw' to rotate anitclockwise
        dask : bool, optional
            Do computation in dask instead of in C extension over full array.
            This returns a DaskArray or DaskArrayClient with pending execution instead of a numpy array.
            You can use the .compute() method to get the numpy array.
            Default is False.

    Returns
    -------
        array
            Rotated stack of images of shape (N, x, y)

    """

    if sense == "ccw":
        sense = 1
    elif sense == "cw":
        sense = 0
    else:
        raise ValueError("sense must be 'cw' or 'ccw'")

    if dask:
        return dask_rotate90(a, sense)
    else:
        return extimage.rotate90(a, sense)
