import numpy as np
from csxtools.image import (
    rotate90,
    stackmean,
    stacksum,
    stackstd,
    stackvar,
    stackstderr,
    images_mean,
    images_sum,
)
from numpy.testing import assert_array_equal, assert_allclose


def test_rotate90():
    image = np.array([[[1, 2], [3, 4]]], dtype=np.float32)
    result = rotate90(image)
    expected = np.array([[[2, 4], [1, 3]]], dtype=np.float32)
    assert_array_equal(result, expected)


def test_stackmean():
    stack = np.array(
        [
            [[1, 2], [3, 4]],
            [[1, 2], [3, 4]],
        ],
        dtype=np.float32,
    )
    result = stackmean(stack)
    expected = np.mean(stack, axis=0)
    assert_allclose(result, expected)


def test_stacksum():
    stack = np.array(
        [
            [[1, 1], [1, 1]],
            [[1, 1], [1, 1]],
        ],
        dtype=np.float32,
    )
    result = stacksum(stack)
    expected = np.sum(stack, axis=0)
    assert_array_equal(result, expected)


def test_stackstd():
    stack = np.array(
        [
            [[0, 1], [2, 3]],
            [[2, 3], [4, 5]],
        ],
        dtype=np.float32,
    )
    result = stackstd(stack)
    expected = np.std(stack, axis=0)
    assert_allclose(result, expected)


def test_stackvar():
    stack = np.array(
        [
            [[0, 1], [2, 3]],
            [[2, 3], [4, 5]],
        ],
        dtype=np.float32,
    )
    result = stackvar(stack)
    expected = np.var(stack, axis=0)
    assert_allclose(result, expected)


def test_stackstderr():
    stack = np.array(
        [
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
        ],
        dtype=np.float32,
    )
    expected = np.std(stack, axis=0, ddof=1) / np.sqrt(stack.shape[0])
    result = stackstderr(stack)
    assert_allclose(result, expected)


def test_images_mean():
    stack = np.array(
        [
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
        ],
        dtype=np.float32,
    )
    result = images_mean(stack)
    expected = np.mean(stack, axis=0)
    assert_allclose(result, expected)


def test_images_sum():
    stack = np.array(
        [
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
        ],
        dtype=np.float32,
    )
    result = images_sum(stack)
    expected = np.sum(stack, axis=0)
    assert_array_equal(result, expected)
