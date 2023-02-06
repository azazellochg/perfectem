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

# set to 1 for more diagnostic output
DEBUG = 1

SCOPE_NAME = "Krios2"

# beam size in microns (Krios, 3-cond. lenses) or percents (2-cond. lenses)

krios_falcon4 = {
    "StageDrift": {"beam": 1.0, "spot": 3, "mag": 96000, "exp": 0.5, "binning": 2},  # For drift test you need an opened Navigator file with Acquire points
    "Anisotropy": {"beam": 1.0, "spot": 3, "mag": 96000, "exp": 0.5, "binning": 2},  # Run this test for both pre-GIF and post-GIF camera
    "InfoLimit": {"beam": 0.6, "spot": 3, "mag": 250000, "exp": 2, "binning": 1, "defocus": -0.5},
    "ThonRings": {"beam": 0.6, "spot": 3, "mag": 250000, "exp": 1, "binning": 2, "defocus": -0.5},  # Titan Krios G3i 195kx -2um defocus - spec is 0.33nm
    "GoldDiffr": {"beam": 1.05, "spot": 4, "mag": 600000, "exp": 3, "binning": 2, "defocus": -0.5},  # For this test you need C2 150um and sample
    "C2Fringes": {"beam": 0.42, "spot": 6, "mag": 75000, "exp": 0.1, "binning": 1},  # For this test you need to go to an empty area
    "TiltAxis": {"beam": 1.0, "spot": 5, "mag": 75000, "exp": 0.5, "binning": 2},
    "GainRef": {"beam": 1.1, "spot": 3, "mag": 75000, "exp": 1, "binning": 1},  # For this test you need to go to an empty area
    "AFIS": {"beam": 1.0, "spot": 7, "mag": 96000, "exp": 1, "binning": 2, "defocus": -2},
}

glacios_falcon3 = {
    "StageDrift": {"beam": 1.0, "spot": 3, "mag": 92000, "exp": 0.5, "binning": 2},  # For drift test you need an opened Navigator file with Acquire points
    "Anisotropy": {"beam": 44.460, "spot": 3, "mag": 92000, "exp": 1, "binning": 2},  # Run this test for both pre-GIF and post-GIF cameras
    "InfoLimit": {"beam": 0.6, "spot": 3, "mag": 250000, "exp": 2, "binning": 1, "defocus": -0.5},
    "ThonRings": {"beam": 0.6, "spot": 3, "mag": 250000, "exp": 1, "binning": 2, "defocus": -0.5},  # Titan Krios G3i 195kx -2um defocus - spec is 0.33nm
    "GoldDiffr": {"beam": 1.05, "spot": 3, "mag": 600000, "exp": 3, "binning": 2, "defocus": -0.5},  # For this test you need C2 150um and sample
    "C2Fringes": {"beam": 39.701, "spot": 5, "mag": 92000, "exp": 0.1, "binning": 1},  # For this test you need to go to an empty area
    "TiltAxis": {"beam": 1.0, "spot": 3, "mag": 92000, "exp": 0.5, "binning": 2},
    "GainRef": {"beam": 44.460, "spot": 3, "mag": 92000, "exp": 1, "binning": 1},  # For this test you need to go to an empty area
    "AFIS": {"beam": 44.460, "spot": 3, "mag": 92000, "exp": 1, "binning": 2, "defocus": -2, "max_imgsh": 6.0},
}

# Set which params dict to use
params_dict = krios_falcon4
