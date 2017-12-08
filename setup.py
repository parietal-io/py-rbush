from setuptools import find_packages, setup

import versioneer

setup(name='py-rbush',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Python port of JS rbush library',
      url='http://github.com/parietal-io/py-rbush',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True)
