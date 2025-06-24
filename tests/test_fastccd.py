import numpy as np
from csxtools.fastccd import correct_images, photon_count
from numpy.testing import assert_array_equal


def test_correct_images():
    # Simulate a dummy image stack of shape (n_images, height, width)
    images = np.full((5, 10, 10), 100, dtype=np.uint16)
    dark = np.full((10, 10), 20, dtype=np.uint16)
    flat = np.full((10, 10), 2.0, dtype=np.float32)

    corrected = correct_images(images, dark=dark, flat=flat)

    # Expected corrected values: (100 - 20) / 2 = 40
    expected = np.full((5, 10, 10), 40.0, dtype=np.float32)

    assert corrected.shape == images.shape
    assert_array_equal(corrected, expected)


def test_photon_count():
    image = np.array(
        [[0.1, 1.0, 2.0], [2.9, 3.1, 4.0], [5.0, 5.9, 6.1]], dtype=np.float32
    )

    threshold = 3.0
    result = photon_count(image, threshold=threshold)

    # Expect binary output: pixels >= threshold set to 1
    expected = np.array([[0, 0, 0], [0, 1, 1], [1, 1, 1]], dtype=np.uint8)

    assert result.shape == image.shape
    assert_array_equal(result, expected)
