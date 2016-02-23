# set version string using versioneer
from .._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ['rotate90', 'stackmean']

# Now import useful functions

from .transform import rotate90
from .stack import stackmean
