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

if __name__ == '__main__':
    test()
