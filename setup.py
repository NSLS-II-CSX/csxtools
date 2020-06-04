from __future__ import (absolute_import, division, print_function)
import setuptools
from distutils.core import setup, Extension
import numpy as np
import versioneer

with open('requirements.txt') as f:
    requirements = f.read().split()

with open('requirements-extras.txt') as f:
    extras_require = {'complete': f.read().split()}

fastccd = Extension('fastccd',
                    sources=['src/fastccdmodule.c',
                             'src/fastccd.c'],
                    extra_compile_args=['-fopenmp'],
                    extra_link_args=['-lgomp'])

image = Extension('image',
                  sources=['src/imagemodule.c',
                           'src/image.c'],
                  extra_compile_args=['-fopenmp'],
                  extra_link_args=['-lgomp'])

phocount = Extension('phocount',
                     sources=['src/phocountmodule.c',
                              'src/phocount.c'],
                     extra_compile_args=['-fopenmp'],
                     extra_link_args=['-lgomp'])
setup(
    name='csxtools',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Brookhaven National Laboratory',
    packages=setuptools.find_packages(exclude=['src', 'tests']),
    ext_package='csxtools.ext',
    include_dirs=[np.get_include()],
    ext_modules=[fastccd, image, phocount],
    tests_require=['pytest'],
    install_requires=requirements,
    extras_require=extras_require,
    url='http://github.com/NSLS-II_CSX/csxtools',
    keywords='Xray Analysis',
    license='BSD'
)
