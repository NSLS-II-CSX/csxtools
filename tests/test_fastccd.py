import numpy as np
from csxtools.fastccd import correct_images, photon_count
from numpy.testing import assert_array_equal


def test_correct_images():
    image = np.ones((1, 2, 2), dtype=np.float32) * 100
    dark = np.ones((2, 2), dtype=np.float32) * 20
    flat = np.ones((2, 2), dtype=np.float32) * 2.0

    output = correct_images(image, dark, flat)
    expected = np.ones((1, 2, 2), dtype=np.float32) * 40

    assert_array_equal(output, expected)


def test_photon_count():
    image = np.array([[[2.0, 4.0], [6.0, 8.0]]], dtype=np.float32)
    mean_filter = np.array([[[1.0, 2.0], [3.0, 4.0]]], dtype=np.float32)
    std_filter = np.array([[[1.0, 1.0], [1.0, 1.0]]], dtype=np.float32)

    result = photon_count(image, mean_filter, std_filter)
    expected = np.array([[[1, 1], [1, 1]]], dtype=np.uint8)

    assert_array_equal(result, expected)
