# set version string using versioneer
from .._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ['correct_images', 'phocount']

# Now import useful functions

from .images import correct_images
from .phocount import phocount
