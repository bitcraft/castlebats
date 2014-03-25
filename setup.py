#!/usr/bin/env python
#encoding: utf-8

import os
from setuptools import setup
import castlebats

print('not complete')
import sys
sys.exit()


def read(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as fd:
        return fd.read()


setup(name="PyTMX",
      version=pytmx.__version__,
      description='Simple Game - python3',
      author='bitcraft',
      packages=['castlebats'],
      install_requires=['pygame', 'pytmx', 'pyscroll'],
      license="LGPLv3",
      long_description='see https://github.com/bitcraft/castlebats',
      classifiers=[
          "Intended Audience :: Developers",
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
          "Programming Language :: Python :: 3.3",
          "Topic :: Games/Entertainment",
      ],
)
