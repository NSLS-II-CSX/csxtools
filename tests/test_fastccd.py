import numpy as np
from csxtools.fastccd import correct_images, photon_count
from numpy.testing import assert_array_equal


def test_correct_images():
    image = np.full((1, 2, 2), 100, dtype=np.float32)
    dark = np.full((2, 2), 20, dtype=np.float32)
    flat = np.full((2, 2), 2.0, dtype=np.float32)

    result = correct_images(image, dark, flat)
    expected = np.full((1, 2, 2), 40.0, dtype=np.float32)

    assert_array_equal(result, expected)


def test_photon_count():
    image = np.array([[[0.1, 1.0], [3.1, 4.0]]], dtype=np.float32)
    mean_filter = np.array([[[0.0, 0.0], [3.0, 3.0]]], dtype=np.float32)
    std_filter = np.array([[[1.0, 1.0], [0.5, 0.5]]], dtype=np.float32)

    result = photon_count(image, mean_filter, std_filter)

    expected = np.array([[[0, 0], [0, 1]]], dtype=np.uint8)
    assert_array_equal(result, expected)
