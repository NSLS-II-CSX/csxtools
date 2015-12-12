import numpy as np
from csxtools.fastccd import subtract_background
from numpy.testing import assert_array_max_ulp


def test_subtract_background():
    x = np.ones((3,10,10), dtype=np.uint16)
    x[0] = x[0] * 0x0010
    x[1] = x[1] * 0x8020
    x[2] = x[2] * 0xC030

    y = np.ones((3,10,10), dtype=np.float32)
    y[0] = y[0] * 0x0010
    y[1] = y[1] * 0x0020
    y[2] = y[2] * 0x0030
    z = subtract_background(x,y)
    assert_array_max_ulp(z, np.zeros_like(x))

