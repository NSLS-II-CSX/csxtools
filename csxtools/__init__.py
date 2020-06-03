# Now import useful functions

from .utils import (get_fastccd_images, get_fastccd_timestamps)  # noqa F401
from .plotting import make_panel_plot  # noqa F401

# set version string using versioneer
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
