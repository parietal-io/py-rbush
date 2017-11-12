from setuptools import find_packages, setup

from rbush import __version__

setup(name='py-rbush',
      version=__version__,
      description='Python port of JS rbush library',
      url='http://github.com/parietal-io/py-rbush',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True)
