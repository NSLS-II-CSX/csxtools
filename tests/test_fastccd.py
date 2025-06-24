import numpy as np
from csxtools.fastccd import correct_image, subtract_dark, average_dark
from numpy.testing import assert_array_equal

def test_correct_image():
    image = np.zeros((10, 10), dtype=np.uint16)
    corrected = correct_image(image)
    assert corrected.shape == image.shape
    assert_array_equal(corrected, np.zeros_like(image))

def test_subtract_dark():
    image = np.full((10, 10), 5, dtype=np.uint16)
    dark = np.full((10, 10), 4, dtype=np.uint16)
    expected = np.ones((10, 10), dtype=np.uint16)
    result = subtract_dark(image, dark)
    assert_array_equal(result, expected)

def test_average_dark():
    stack = np.ones((10, 10, 10), dtype=np.uint16) * 5
    avg = average_dark(stack)
    assert avg.shape == (10, 10)
    assert_array_equal(avg, np.full((10, 10), 5))
