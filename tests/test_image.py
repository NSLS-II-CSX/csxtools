from csxtools.image import rotate90
import numpy as np
from numpy.testing import assert_array_equal


def test_rotate90():
    x = np.arange(4*20, dtype=np.float32).reshape(4, 20)
    y = rotate90(np.array([x, x, x, x]), 'ccw')
    for i in y:
        assert_array_equal(i, np.rot90(x, 1))

    y = rotate90(np.array([x, x, x, x]), 'cw')
    for i in y:
        assert_array_equal(i, np.rot90(x, -1))
