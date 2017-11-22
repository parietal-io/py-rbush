from __future__ import print_function, absolute_import

from rbush.core import RBush

__version__ = '0.0.1'


def test():
    """Run the rbush test suite."""
    import os
    try:
        import pytest
    except ImportError:
        import sys
        sys.stderr.write("You need to install pytest to run tests.\n\n")
        raise
    pytest.main([os.path.dirname(__file__)])
