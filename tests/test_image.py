import numpy as np
from csxtools.image import crop_image, apply_gain_map, threshold_image, apply_mask
from numpy.testing import assert_array_equal


def test_crop_image():
    image = np.arange(100).reshape(10, 10)
    cropped = crop_image(image, 2, 5, 3, 7)
    expected = image[2:5, 3:7]
    assert cropped.shape == (3, 4)
    assert_array_equal(cropped, expected)


def test_apply_gain_map():
    image = np.full((10, 10), 2.0)
    gain = np.full((10, 10), 0.5)
    corrected = apply_gain_map(image, gain)
    expected = np.ones((10, 10))
    assert_array_equal(corrected, expected)


def test_threshold_image():
    image = np.array([[1, 5, 10], [3, 7, 0]])
    threshold = 5
    thresholded = threshold_image(image, threshold)
    expected = np.array([[0, 5, 10], [0, 7, 0]])
    assert_array_equal(thresholded, expected)


def test_apply_mask():
    image = np.ones((5, 5))
    mask = np.zeros((5, 5))
    masked = apply_mask(image, mask)
    assert_array_equal(masked, np.zeros((5, 5)))
