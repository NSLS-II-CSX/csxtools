# Now import useful functions

from .utils import (
    get_fastccd_images,
    get_fastccd_flatfield,
    get_fastccd_timestamps,
)  # noqa F401
from .utils import (
    get_axis_images,
    get_axis_flatfield,
    get_axis_timestamps,
)
from .plotting import make_panel_plot  # noqa F401

# set version string using versioneer
from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
