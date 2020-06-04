from .animation import image_stack_to_movie, show_image_stack
from .nbviewer import notebook_to_nbviewer

# set version string using versioneer
from .._version import get_versions
__version__ = get_versions()['version']
del get_versions

__all__ = ['image_stack_to_movie', 'show_image_stack',
           'notebook_to_nbviewer']
