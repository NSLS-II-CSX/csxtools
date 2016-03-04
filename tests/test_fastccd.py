import numpy as np
from csxtools.fastccd import correct_images, photon_count
from numpy.testing import (assert_array_max_ulp, assert_array_equal,
                           assert_array_almost_equal)


def test_correct_images():
    x = np.ones((3, 10, 10), dtype=np.uint16)
    x[0] = x[0] * 0x0010
    x[1] = x[1] * 0x8020
    x[2] = x[2] * 0xC030

    y = np.ones((3, 10, 10), dtype=np.float32)
    y[0] = y[0] * 0x0010
    y[1] = y[1] * 0x0020
    y[2] = y[2] * 0x0030
    z = correct_images(x, y)
    assert_array_max_ulp(z, np.zeros_like(x))


def test_photon_count():
    x = np.array([[0,  0,  0,  0,  0,  0,  0,  0],
                  [0,  0,  0,  0,  0,  4,  3,  0],
                  [0,  0,  0, 10,  0,  4,  0,  0],
                  [0,  0,  4,  6,  2,  0,  0,  0],
                  [0,  0,  0,  0,  0,  0,  0,  0],
                  [0,  0,  0,  0,  0,  0,  0,  0]], dtype=np.float32)

    nsum = 3

    y = np.zeros_like(x)
    y[2, 3] = 20
    z = np.zeros_like(x)
    z[2, 3] = np.std(np.array([10, 6, 4, 2, 0, 0, 0, 0, 0],
                              dtype=np.float32)[:nsum])

    op = photon_count(np.array([x, x, x], dtype=np.float32),
                      thresh=(5, 13), mean_filter=(10, 30),
                      std_filter=(0, 100), nsum=nsum)

    assert_array_equal(op[0], np.array([y, y, y]))
    assert_array_almost_equal(op[1], np.array([z, z, z]), decimal=6)
