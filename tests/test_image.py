from csxtools.image import (rotate90, stackmean, stacksum, stackstd,
                            stackvar, stackstderr, images_mean, images_sum)
import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal


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


def test_stacksum():
    x = np.ones((1, 100, 100), dtype=np.float32) * np.nan
    m, n = stacksum(x)
    assert_array_equal(m, np.nan * np.zeros((100, 100), dtype=np.float32))
    assert_array_equal(n, np.zeros((100, 100), dtype=np.float32))

    x = np.ones((1000, 100, 100), dtype=np.float32) * 52.0
    m, n = stacksum(x)
    assert_array_equal(m, np.ones((100, 100), dtype=np.float32) * 52.0 * 1000)
    assert_array_equal(n, np.ones((100, 100), dtype=np.float32) * 1000.0)

    # Now test with nans

    x = np.ones((1000, 100, 100), dtype=np.float32) * 2
    x[10] = np.nan
    x[23] = np.nan
    x[40] = np.nan
    m, n = stacksum(x)
    assert_array_almost_equal(m, np.ones((100, 100), dtype=np.float32) * 2000,
                              decimal=3)
    assert_array_equal(n, np.ones((100, 100), dtype=np.float32) * (1000 - 3))


def test_stackstd():
    x = np.repeat(np.arange(1000, dtype=np.float32), 400).reshape(
        (1000, 20, 20))
    m, n = stackstd(x)
    assert_array_almost_equal(m, np.std(x, axis=0), 2)
    assert_array_equal(n, np.ones((20, 20), dtype=np.float32) * 1000.0)


def test_stackvar():
    x = np.repeat(np.arange(1000, dtype=np.float32), 400).reshape(
        (1000, 20, 20))
    m, n = stackvar(x)
    assert_array_almost_equal(m, np.var(x, axis=0), 0)
    assert_array_equal(n, np.ones((20, 20), dtype=np.float32) * 1000.0)


def test_stackstderr():
    x = np.repeat(np.arange(1000, dtype=np.float32), 400).reshape(
        (1000, 20, 20))
    m, n = stackstderr(x)
    assert_array_almost_equal(m, np.std(x, axis=0) / np.sqrt(n), 3)
    assert_array_equal(n, np.ones((20, 20), dtype=np.float32) * 1000.0)


def test_images_mean():
    x = np.array([np.repeat(ii*np.ones(ii*100, dtype=np.float32), 400).reshape(
                 (ii*100, 20, 20)) for ii in range(1, 11)])
    m = images_mean(x)
    assert_array_equal(m, np.array([np.mean(x1) for x1 in x]), 3)


def test_images_sum():
    x = np.array([np.repeat(ii*np.ones(ii*100, dtype=np.float32), 400).reshape(
                 (ii*100, 20, 20)) for ii in range(1, 11)])
    m = images_sum(x)
    assert_array_equal(m, np.array([np.sum(np.mean(x1, axis=0))
                                    for x1 in x]), 3)
