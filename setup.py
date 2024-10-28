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
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys


libs = []
if sys.platform.startswith("win"):
    libs.append('wsock32')

serialemmodule = Extension('serialem',
                           define_macros=[('MAJOR_VERSION', '1'),
                                          ('MINOR_VERSION', '0')],
                           sources=['perfectem/SEM_python/SerialEMModule.cpp',
                                    'perfectem/SEM_python/PySEMSocket.cpp'],
                           libraries=libs,
                           optional=True,
                           depends=['perfectem/SEM_python/PySEMSocket.h',
                                    'perfectem/SEM_python/MacroMasterList.h'])


class BuildSEMPython(build_ext):
    def run(self):
        try:
            import serialem
        except ImportError:
            build_ext.run(self)


setup(
    ext_modules=[serialemmodule],
    cmdclass={"build_ext": BuildSEMPython}
)
