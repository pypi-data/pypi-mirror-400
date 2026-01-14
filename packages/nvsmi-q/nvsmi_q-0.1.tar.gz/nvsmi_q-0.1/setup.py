#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ref: https://github.com/navdeep-G/setup.py/blob/master/setup.py

import io
import os
import sys
from shutil import rmtree

from setuptools import setup, Command


# Package meta-data.
NAME = 'nvsmi-q'
DESCRIPTION = 'Yet another python wrapper for nvidia-smi, keep it simple & stupid ;)'
URL = 'https://github.com/Kahsolt/nvsmi-q'
EMAIL = 'kahsolt@qq.com'
AUTHOR = 'Kahsolt'
REQUIRES_PYTHON = '>=3.10.0'
VERSION = '0.1'

# What packages are required for this module to be executed?
REQUIRED = []

# What packages are optional?
EXTRAS = {}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
  with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()
except FileNotFoundError:
  long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
  project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
  with open(os.path.join(here, project_slug, '__version__.py')) as f:
    exec(f.read(), about)
else:
  about['__version__'] = VERSION


class UploadCommand(Command):
  """Support setup.py upload."""

  description = 'Build and publish the package.'
  user_options = []

  @staticmethod
  def status(s):
    """Prints things in bold."""
    print('\033[1m{0}\033[0m'.format(s))

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    try:
        self.status('Removing previous builds…')
        rmtree(os.path.join(here, 'dist'))
    except OSError:
        pass

    self.status('Building Source and Wheel (universal) distribution…')
    os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

    self.status('Uploading the package to PyPI via Twine…')
    os.system('twine upload dist/*')

    self.status('Pushing git tags…')
    os.system('git tag v{0}'.format(about['__version__']))
    os.system('git push --tags')

    sys.exit()


# Where the magic happens:
setup(
  name=NAME,
  version=about['__version__'],
  description=DESCRIPTION,
  long_description=long_description,
  long_description_content_type='text/markdown',
  author=AUTHOR,
  author_email=EMAIL,
  python_requires=REQUIRES_PYTHON,
  url=URL,
  py_modules=['nvmsi'],
  install_requires=REQUIRED,
  extras_require=EXTRAS,
  include_package_data=True,
  license='MIT',
  classifiers=[
    # Trove classifiers
    # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Environment :: GPU :: NVIDIA CUDA',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: System :: Monitoring',
    'Topic :: Utilities',
  ],
  # $ setup.py publish support.
  cmdclass={
    'upload': UploadCommand,
  },
)
