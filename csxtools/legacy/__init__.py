# set version string using versioneer
from .._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ['PrincetonSPEFile']

# Now import useful functions

from .files import PrincetonSPEFile
