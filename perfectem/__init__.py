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

import importlib
import argparse
from typing import List, Optional

from .config import microscopes

__version__ = '0.9.1'

all_tests = (
    ("AFIS", "AFIS validation"),
    ("Anisotropy", "Magnification anisotropy"),
    ("C2Fringes", "C2 Fresnel fringes"),
    ("GainRef", "Gain reference check"),
    ("GoldDiffr", "Gold diffraction"),
    ("InfoLimit", "Information limit (Young fringes)"),
    ("PointRes", "Point resolution"),
    ("StageDrift", "Stage drift"),
    ("ThonRings", "Thon rings"),
    ("TiltAxis", "Tilt axis offset"),
)


def show(extra: bool = False) -> None:
    for test in all_tests:
        print(f"\t[{test[0]}] {test[1]}")
        if extra:
            module = importlib.import_module("perfectem.scripts")
            func = getattr(module, test[0])
            print(func.__doc__)
            print("="*80)


def main(argv: Optional[List] = None) -> None:
    try:
        import serialem
    except ImportError:
        raise ImportError("This program must be run on the computer with SerialEM Python module")

    parser = argparse.ArgumentParser(description="This script launches selected TEM performance test")
    parser.add_argument("-l", "--list", default=False, action='store_true',
                        help="List available tests")
    parser.add_argument("-d", "--desc", default=False, action='store_true',
                        help="Show detailed description for each test")

    args = parser.parse_args(argv)

    if args.list or args.desc:
        print("\nAvailable tests:")
        show(args.desc)
    else:
        print("\nAvailable microscopes:")
        for scope_num, scope in enumerate(microscopes, start=1):
            print(f"\t[{scope_num}] {scope[0]}")

        scope_num = int(input("\nInput the microscope number: ").strip())
        if scope_num in range(1, len(microscopes)):
            scope_name = microscopes[scope_num - 1][0]
            print("\nChoose a performance test to run:")
            show()
            test_num = int(input("\nInput the test number: ").strip())

            if test_num in range(1, len(all_tests)):
                funcname = all_tests[test_num][0]
                module = importlib.import_module("perfectem.scripts")
                func = getattr(module, funcname)
                print(func.__doc__)
                func(scope_name=scope_name, **microscopes[scope_num][1][funcname]).run()
            else:
                raise IndexError("Wrong test number!")

        else:
            raise IndexError("Wrong microscope number!")
