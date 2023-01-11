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

from .config import params_dict

__version__ = '0.6'


def main():
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
        if num == 1:
            from .scripts import StageDrift
            StageDrift(**params_dict['StageDrift']).run()
        elif num == 2:
            from .scripts import Anisotropy
            Anisotropy(**params_dict['Anisotropy']).run()
        elif num == 3:
            from .scripts import InfoLimit
            InfoLimit(**params_dict['InfoLimit']).run()
        elif num == 4:
            from .scripts import ThonRings
            ThonRings(**params_dict['ThonRings']).run()
        elif num == 5:
            from .scripts import GoldDiffr
            GoldDiffr(**params_dict['GoldDiffr']).run()
        elif num == 6:
            from .scripts import C2Fringes
            C2Fringes(**params_dict['C2Fringes']).run()
        elif num == 7:
            from .scripts import TiltAxis
            TiltAxis(**params_dict['TiltAxis']).run()
        elif num == 8:
            from .scripts import GainRef
            GainRef(**params_dict['GainRef']).run()
        elif num == 9:
            from .scripts import AFIS
            AFIS(**params_dict['AFIS']).run()
    else:
        raise IndexError("Wrong test number!")
