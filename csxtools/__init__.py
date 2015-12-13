# set version string using versioneer
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# Now import useful functions

from .utils import get_fastccd_images
