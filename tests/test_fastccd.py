import numpy as np
from csxtools.fastccd import correct_images, photon_count
from numpy.testing import assert_array_equal


def test_correct_images():
    images = np.full((1, 10, 10), 100, dtype=np.float32)
    dark = np.full((10, 10), 20, dtype=np.float32)
    flat = np.full((10, 10), 2.0, dtype=np.float32)

    corrected = correct_images(images, dark=dark, flat=flat)

    expected = np.full((1, 10, 10), 40.0, dtype=np.float32)

    assert corrected.shape == images.shape
    assert_array_equal(corrected, expected)


def test_photon_count():
    image = np.array([[[0.1, 1.0], [3.1, 4.0]]], dtype=np.float32)  # shape (1, 2, 2)
    mean_filter = np.array([[[0.0, 0.0], [3.0, 3.0]]], dtype=np.float32)
    std_filter = np.array([[[1.0, 1.0], [0.5, 0.5]]], dtype=np.float32)

    result = photon_count(image, mean_filter, std_filter)

    # (3.1 - 3.0) / 0.5 = 0.2 => not a photon
    # (4.0 - 3.0) / 0.5 = 2.0 => photon
    expected = np.array([[[0, 0], [0, 1]]], dtype=np.uint8)

    assert result.shape == image.shape
    assert_array_equal(result, expected)
