from __future__ import absolute_import, division, print_function

import sys
from distutils.core import Extension, setup
from os import path

import numpy as np
import setuptools
from setuptools.command.build_ext import build_ext  # Import build_ext
import versioneer


# Custom build_ext to remove cpython-XX suffix
class CustomBuildExt(build_ext):
    def get_ext_filename(self, ext_name):
        # Default filename: fastccd.cpython-38-x86_64-linux-gnu.so
        filename = super().get_ext_filename(ext_name)
        # Strip platform-specific suffix: fastccd.so
        return filename.split(".")[0] + ".so"


min_version = (3, 8)
if sys.version_info < min_version:
    error = """
bluesky-adaptive does not support Python {0}.{1}.
Python {2}.{3} and above is required. Check your Python version like so:

python3 --version

This may be due to an out-of-date pip. Make sure you have pip >= 9.0.1.
Upgrade pip like so:

pip install --upgrade pip
""".format(
        *(sys.version_info[:2] + min_version)
    )
    sys.exit(error)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as readme_file:
    readme = readme_file.read()


with open("requirements.txt") as f:
    requirements = f.read().split()

with open("requirements-extras.txt") as f:
    extras_require = {"complete": f.read().split()}

fastccd = Extension(
    "fastccd",
    sources=["src/fastccdmodule.c", "src/fastccd.c"],
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-lgomp"],
)

axis1 = Extension(
    "axis1",
    sources=["src/axis1module.c", "src/axis1.c"],
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-lgomp"],
)

image = Extension(
    "image",
    sources=["src/imagemodule.c", "src/image.c"],
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-lgomp"],
)

phocount = Extension(
    "phocount",
    sources=["src/phocountmodule.c", "src/phocount.c"],
    extra_compile_args=["-fopenmp"],
    extra_link_args=["-lgomp"],
)
setup(
    name="csxtools",
    version=versioneer.get_version(),
    # cmdclass=versioneer.get_cmdclass(),
    cmdclass={
        **versioneer.get_cmdclass(),
        "build_ext": CustomBuildExt,  # Use the custom build_ext
    },
    author="Brookhaven National Laboratory",
    description="Python library for tools to be used at the Coherent Soft X-ray scattering (CSX) beamline at NSLS-II.",
    packages=setuptools.find_packages(exclude=["src", "tests"]),
    python_requires=">={}".format(".".join(str(n) for n in min_version)),
    long_description=readme,
    long_description_content_type="text/markdown",
    ext_package="csxtools.ext",
    include_dirs=[np.get_include()],
    # ext_modules=[fastccd, image, phocount],
    ext_modules=[fastccd, axis1, image, phocount],
    tests_require=["pytest"],
    install_requires=requirements,
    extras_require=extras_require,
    url="https://github.com/NSLS-II-CSX/csxtools",
    keywords="Xray Analysis",
    license="BSD",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
)
