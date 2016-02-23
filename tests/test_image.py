from csxtools.image import rotate90, stackmean
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


def test_stackmean():
    x = np.ones((1, 100, 100), dtype=np.float32) * np.nan
    m = stackmean(x)
    assert_array_equal(m, np.zeros((100, 100), dtype=np.float32))

    x = np.ones((1000, 100, 100), dtype=np.float32) * 52.0
    m = stackmean(x)
    assert_array_equal(m, np.ones((100, 100), dtype=np.float32) * 52.0)

    # Now test with nans

    x = np.ones((1000, 100, 100), dtype=np.float32) * 52.0
    x[10] = np.nan
    x[23] = np.nan
    x[40] = np.nan
    m = stackmean(x)
    assert_array_equal(m, np.ones((100, 100), dtype=np.float32) * 52.0)
