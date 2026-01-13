#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages
from codecs import open
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))
sys.path.append(here)
import versioneer  # noqa: E402


CLASSIFIERS = """
Development Status :: 3 - Alpha
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Programming Language :: Python :: 3
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Programming Language :: Python :: 3.13
Programming Language :: Python :: Implementation :: CPython
Topic :: Scientific/Engineering
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

PACKAGE_DATA = ["setups/*/assets.json", "setups/*/*.npy", "setups/*/*.png"]

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join(here, "requirements.txt"), encoding="utf-8") as f:
    install_requires = [line.strip() for line in f]

setup(
    name='veros-extra-setups',
    license='MIT',
    author='Dion Häfner (NBI Copenhagen)',
    author_email='dion.haefner@nbi.ku.dk',
    keywords='oceanography python parallel numpy multi-core geophysics ocean-model mpi4py jax',
    description='Extra setups for Veros, the versatile ocean simulator.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://veros-extra-setups.readthedocs.io',
    python_requires='>=3.10',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'veros.setup_dirs': [
            'extra = veros_extra_setups.setups'
        ]
    },
    package_data={
        'veros_extra_setups': PACKAGE_DATA
    },
    classifiers=[c for c in CLASSIFIERS.split('\n') if c],
    zip_safe=False,
)
