# **************************************************************************
# *
# * Authors:     Grigory Sharov (gsharov@mrc-lmb.cam.ac.uk) [1]
# *
# * [1] MRC Laboratory of Molecular Biology, MRC-LMB
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'gsharov@mrc-lmb.cam.ac.uk'
# *
# **************************************************************************

"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages, Extension
import sys
from os import path
from perfectem import __version__

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

libs = []
if sys.platform.startswith("win"):
    libs.append('wsock32')

serialemmodule = Extension('serialem',
                           define_macros=[('MAJOR_VERSION', '1'),
                                          ('MINOR_VERSION', '0')],
                           sources=['perfectem/SEM_python/SerialEMModule.cpp',
                                    'perfectem/SEM_python/PySEMSocket.cpp'],
                           libraries=libs,
                           depends=['perfectem/SEM_python/PySEMSocket.h',
                                    'perfectem/SEM_python/MacroMasterList.h'])

setup(
    name='perfectem',
    version=__version__,
    description='Run TEM performance tests with SerialEM',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/azazellochg/perfectem',
    author='Grigory Sharov',
    author_email='gsharov@mrc-lmb.cam.ac.uk',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows'
    ],
    keywords='cryo-em python serialem',
    packages=find_packages(),
    ext_modules=[serialemmodule],
    install_requires=['mrcfile', 'numpy', 'scipy', 'matplotlib'],
    extras_require={
      "dev": ["mypy"]
    },
    python_requires='>=3.8',
    entry_points={'console_scripts': ['perfectem=perfectem:main']},
    project_urls={
        'Bug Reports': 'https://github.com/azazellochg/perfectem/issues',
        'Source': 'https://github.com/azazellochg/perfectem',
    },
)
