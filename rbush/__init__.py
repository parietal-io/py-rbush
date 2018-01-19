from __future__ import print_function, absolute_import

from rbush.core import RBush
# from rbush.core import to_json, to_dict

from .test import test

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
