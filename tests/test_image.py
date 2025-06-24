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
    image = np.array([[1, 2], [3, 4]])
    rotated = rotate90(image)
    expected = np.array([[2, 4], [1, 3]])
    assert_array_equal(rotated, expected)


def test_stackmean():
    stack = np.ones((2, 3, 3)) * np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    result = stackmean(stack)
    expected = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    assert_allclose(result, expected)


def test_stacksum():
    stack = np.ones((2, 2, 2), dtype=np.float32)
    result = stacksum(stack)
    expected = np.full((2, 2), 2.0)
    assert_array_equal(result, expected)


def test_stackstd():
    stack = np.array(
        [
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
        ]
    )
    result = stackstd(stack)
    expected = np.std(stack, axis=0)
    assert_allclose(result, expected)


def test_stackvar():
    stack = np.array(
        [
            [[2, 2], [2, 2]],
            [[4, 4], [4, 4]],
        ]
    )
    result = stackvar(stack)
    expected = np.var(stack, axis=0)
    assert_allclose(result, expected)


def test_stackstderr():
    stack = np.array(
        [
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]],
        ]
    )
    result = stackstderr(stack)
    # Standard error = std / sqrt(N)
    expected = np.std(stack, axis=0, ddof=1) / np.sqrt(stack.shape[0])
    assert_allclose(result, expected)


def test_images_mean():
    img1 = np.array([[1, 2], [3, 4]])
    img2 = np.array([[5, 6], [7, 8]])
    result = images_mean(img1, img2)
    expected = np.array([[3, 4], [5, 6]])
    assert_allclose(result, expected)


def test_images_sum():
    img1 = np.array([[1, 2], [3, 4]])
    img2 = np.array([[5, 6], [7, 8]])
    result = images_sum(img1, img2)
    expected = np.array([[6, 8], [10, 12]])
    assert_array_equal(result, expected)
