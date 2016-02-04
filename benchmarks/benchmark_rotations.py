from csxtools.image import rotate90
import numpy as np
import timeit
import os


big_array = np.ones((10000, 960, 960), dtype=np.float32)
loops = 20
print('{},{}'.format(os.environ['OMP_NUM_THREADS'], loops), end='')
t = timeit.timeit('rotate90(big_array, "cw")', globals=globals(),
                  number=loops)
print(',{}'.format(t))
