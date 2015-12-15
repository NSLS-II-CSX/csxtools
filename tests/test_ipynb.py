import matplotlib
matplotlib.use('Agg')
from csxtools.ipynb import show_image_stack, image_stack_to_movie
import numpy as np


def test_image_stack_to_movie():
    x = np.ones((10, 100, 100))
    image_stack_to_movie(x)
