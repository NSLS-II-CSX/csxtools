from __future__ import absolute_import, division, print_function

import sys
from setuptools import Extension
from os import path

import setuptools
from setuptools.command.build_ext import build_ext
import versioneer


# Custom build_ext to delay NumPy import and strip suffix
class CustomBuildExt(build_ext):
    def finalize_options(self):
        super().finalize_options()
        import numpy  # <== DELAY numpy import until now

        self.include_dirs.append(numpy.get_include())

    def get_ext_filename(self, ext_name):
        filename = super().get_ext_filename(ext_name)
        return filename.split(".")[0] + ".so"


min_version = (3, 8)
if sys.version_info < min_version:
    error = f"""
csxtools does not support Python {sys.version_info[0]}.{sys.version_info[1]}.
Python {min_version[0]}.{min_version[1]} and above is required.
"""
    sys.exit(error)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    requirements = f.read().split()

with open("requirements-extras.txt") as f:
    extras_require = {"complete": f.read().split()}

# C extensions
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

# Setup
setuptools.setup(
    name="csxtools",
    version=versioneer.get_version(),
    cmdclass={
        **versioneer.get_cmdclass(),
        "build_ext": CustomBuildExt,
    },
    author="Brookhaven National Laboratory",
    description="Python library for tools to be used at the Coherent Soft X-ray scattering (CSX) beamline at NSLS-II.",
    packages=setuptools.find_packages(exclude=["src", "tests"]),
    python_requires=">={}".format(".".join(str(n) for n in min_version)),
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    extras_require=extras_require,
    ext_package="csxtools.ext",
    ext_modules=[fastccd, axis1, image, phocount],
    url="https://github.com/NSLS-II-CSX/csxtools",
    keywords="Xray Analysis",
    license="BSD",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
)
