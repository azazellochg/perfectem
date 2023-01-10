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

try:
    import serialem as sem
except ImportError:
    print("Failed to import SerialEM Python module. "
          "Check https://bio3d.colorado.edu/SerialEM/download.html#PythonModules")

from .config import DEBUG
from .common import BaseSetup
from .scripts import *

__version__ = '0.6'


def main():
    BaseSetup.get_scope_type()
    camera_num = 1
    camera_names = []
    while True:
        name = sem.ReportCameraName(camera_num)
        if name == "NOCAM":
            break
        else:
            camera_names.append(name)
            camera_num += 1

    print("Choose camera to use with SerialEM:\n")
    for i, c in enumerate(camera_names):
        print(f"\t[{i+1}] {c}")

    camera_num = int(input("\nInput the camera number: ").strip())
    if camera_num > len(camera_names) or camera_num < 1:
        raise IndexError("Wrong camera number!")
    else:
        sem.SelectCamera(camera_num)
        _, _, mode = sem.ReportMag()
        if mode == 1:  # EFTEM
            sem.SetSlitIn(0)  # retract slit

    if not sem.ReportColumnOrGunValve():
        sem.SetColumnOrGunValve(1)
    sem.SetLowDoseMode(0)

    print("\nChoose a performance test to run:\n\n"
          "\t[1] Stage drift\n"
          "\t[2] Magnification anisotropy\n"
          "\t[3] Information limit (Young fringes)\n"
          "\t[4] Thon rings\n"
          "\t[5] Gold diffraction\n"
          "\t[6] C2 Fresnel fringes\n"
          "\t[7] Tilt axis offset\n"
          "\t[8] Gain reference check\n"
          "\t[9] AFIS check\n"
          )

    num = int(input("\nInput the test number: ").strip())
    if num in range(1, 10):
        test_dict = {
            # beam size in microns (Krios, 3-cond. lenses) or percents (2-cond. lenses)

            1: (StageDrift, {"beam": 1.0, "spot": 3, "mag": 96000, "exp": 0.5, "binning": 2}),  # For drift test you need an opened Navigator file with Acquire points
            2: (Anisotropy, {"beam": 1.0, "spot": 3, "mag": 96000, "exp": 0.5, "binning": 2}),  # Run this test for both pre-GIF and post-GIF camera
            3: (InfoLimit, {"beam": 0.6, "spot": 3, "mag": 250000, "exp": 2, "binning": 1, "defocus": -0.5}),
            4: (ThonRings, {"beam": 0.6, "spot": 3, "mag": 250000, "exp": 1, "binning": 2, "defocus": -0.5}),  # Titan Krios G3i 195kx -2um defocus - spec is 0.33nm
            5: (GoldDiffr, {"beam": 1.05, "spot": 3, "mag": 600000, "exp": 3, "binning": 2, "defocus": -0.5}),  # For this test you need C2 150um and sample
            6: (C2Fringes, {"beam": 0.4, "spot": 3, "mag": 75000, "exp": 0.1, "binning": 1}),  # For this test you need to go to an empty area
            7: (TiltAxis, {"beam": 1.0, "spot": 3, "mag": 75000, "exp": 0.5, "binning": 2}),
            8: (GainRef, {"beam": 1.1, "spot": 3, "mag": 75000, "exp": 1, "binning": 1, "defocus": -2}),  # For this test you need to go to an empty area
            9: (AFIS, {"beam": 1.0, "spot": 7, "mag": 96000, "exp": 1, "binning": 2, "defocus": -2}),
        }

        test, params = test_dict[num][0], test_dict[num][1]
        test(**params).run()
    else:
        raise IndexError("Wrong test number!")
