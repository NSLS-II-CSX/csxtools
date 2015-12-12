from __future__ import (absolute_import, division, print_function)
import setuptools
from distutils.core import setup, Extension
import numpy as np
import versioneer

fastccd = Extension('fastccd',
                    sources=['src/fastccdmodule.c',
                             'src/fastccd.c'],
                    extra_compile_args=['-fopenmp'],
                    extra_link_args=['-lgomp'])

setup(
    name='csxtools',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Brookhaven National Laboratory',
    packages=setuptools.find_packages(exclude=['src']),
    ext_package='csxtools.ext',
    include_dirs=[np.get_include()],
    ext_modules=[fastccd],
    install_requires=['numpy'],  # essential deps only
    url='http://github.com/NSLS-II_CSX/csxtools',
    keywords='Xray Analysis',
    license='BSD'
)
