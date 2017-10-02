from setuptools import find_packages, setup

with open('requirements.txt') as f:
    install_requires = f.read().strip().split('\n')

setup(name='py-rbush',
      version='0.0.1',
      description='Python port of JS rbush library',
      url='http://github.com/parietal-io/py-rbush',
      install_requires=install_requires,
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True)
