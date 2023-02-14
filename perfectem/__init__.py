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

from .config import params_dict

__version__ = '0.8'

test_dict = {
    # num: [Func name, Name, Desc]
    1: ["StageDrift", "Stage Drift", ""],
    2: ["Anisotropy", "Magnification anisotropy", ""],
    3: ["InfoLimit", "Information limit (Young fringes)"],
    4: ["ThonRings", "Thon Rings", ""],
    5: ["GoldDiffr", "Gold diffraction", ""],
    6: ["C2Fringes", "C2 Fresnel fringes", ""],
    7: ["TiltAxis", "Tilt axis offset", ""],
    8: ["GainRef", "Gain reference check", ""],
    9: ["AFIS", "AFIS check", ""]
}


def show(extra=False):
    for t in test_dict:
        print(f"\t[{t}] {test_dict[t][1]}")
        if extra:
            module = importlib.import_module("perfectem.scripts")
            func = getattr(module, test_dict[t][0])
            print(func.__doc__)
            print("="*80)


def main(argv=None):
    try:
        import serialem
    except ImportError:
        raise ImportError("This program must be run on the computer with SerialEM Python module")

    parser = argparse.ArgumentParser(description="This script launches selected TEM performance test")
    parser.add_argument("-l", "--list", default=False, action='store_true',
                        help="List all available tests")
    parser.add_argument("-d", "--desc", default=False, action='store_true',
                        help="Show description for each test")

    args = parser.parse_args(argv)

    if args.list or args.desc:
        print("\nAvailable tests:")
        show(args.desc)
        exit(0)
    else:
        print("\nChoose a performance test to run:")
        show()
        num = int(input("\nInput the test number: ").strip())

        if num in range(1, 10):
            funcname = test_dict[num][0]
            module = importlib.import_module("perfectem.scripts")
            func = getattr(module, funcname)
            print(func.__doc__)
            func(**params_dict[funcname]).run()
        else:
            raise IndexError("Wrong test number!")
