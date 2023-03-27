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

krios2_falcon4 = {
    "StageDrift": {"beam": 1.1, "spot": 4, "mag": 96000, "exp": 0.5, "binning": 2},
    "Anisotropy": {"beam": 1.1, "spot": 4, "mag": 96000, "exp": 0.5, "binning": 2},
    "InfoLimit": {"beam": 1.05, "spot": 4, "mag": 600000, "exp": 3, "binning": 2, "defocus": -0.1, "spec": 0.14},  # use nanoProbe C2 150
    "ThonRings": {"beam": 1.1, "spot": 3, "mag": 250000, "exp": 1, "binning": 2, "defocus": -1, "spec": 0.33},
    "PointRes": {"beam": 1.1, "spot": 3, "mag": 380000, "exp": 1, "binning": 2, "defocus": -0.087, "spec": 0.20},
    "GoldDiffr": {"beam": 1.1, "spot": 4, "mag": 600000, "exp": 3, "binning": 2, "defocus": -0.1, "spec": 0.1},  # use nanoProbe C2 150
    "C2Fringes": {"beam": 0.42, "spot": 6, "mag": 75000, "exp": 0.1, "binning": 1},
    "TiltAxis": {"beam": 1.1, "spot": 5, "mag": 75000, "exp": 0.5, "binning": 2},
    "GainRef": {"beam": 1.1, "spot": 7, "mag": 96000, "exp": 1, "binning": 1},
    "AFIS": {"beam": 1.1, "spot": 7, "mag": 96000, "exp": 1, "binning": 2, "defocus": -2, "max_imgsh": 12.0, "spec": (750, 10)},  # specs: (coma in nm, astig in nm)
}

krios3_k3 = {
    "StageDrift": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2},
    "Anisotropy": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2},
    "InfoLimit": {"beam": 0.66, "spot": 5, "mag": 250000, "exp": 2, "binning": 1, "defocus": -0.5, "spec": 0.14},
    "ThonRings": {"beam": 0.66, "spot": 5, "mag": 250000, "exp": 1, "binning": 2, "defocus": -0.5, "spec": 0.33},
    "PointRes": {"beam": 0.66, "spot": 5, "mag": 380000, "exp": 1, "binning": 2, "defocus": -0.073, "spec": 0.20},
    "GoldDiffr": {"beam": 0.66, "spot": 5, "mag": 600000, "exp": 3, "binning": 2, "defocus": -0.2, "spec": 0.1},
    "C2Fringes": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2, "defocus": -1.0},
    "TiltAxis": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2},
    "GainRef": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 1, "binning": 1},
    "AFIS": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 1, "binning": 2, "defocus": -2, "max_imgsh": 12.0, "spec": (750, 10)},  # specs: (coma in nm, astig in nm)
}

glacios_falcon3 = {
    "StageDrift": {"beam": 44.46, "spot": 3, "mag": 92000, "exp": 0.5, "binning": 2},
    "Anisotropy": {"beam": 44.46, "spot": 3, "mag": 92000, "exp": 1, "binning": 2},
    "InfoLimit": {"beam": 44.46, "spot": 3, "mag": 250000, "exp": 2, "binning": 1, "defocus": -0.5},
    "ThonRings": {"beam": 44.46, "spot": 3, "mag": 250000, "exp": 1, "binning": 2, "defocus": -0.5},
    "PointRes": {"beam": 44.46, "spot": 3, "mag": 380000, "exp": 1, "binning": 2, "defocus": -0.082, "spec": 0.24},
    "GoldDiffr": {"beam": 44.46, "spot": 3, "mag": 600000, "exp": 3, "binning": 2, "defocus": -0.2},
    "C2Fringes": {"beam": 39.701, "spot": 5, "mag": 92000, "exp": 0.1, "binning": 1},
    "TiltAxis": {"beam": 44.46, "spot": 3, "mag": 92000, "exp": 0.5, "binning": 2},
    "GainRef": {"beam": 44.460, "spot": 3, "mag": 92000, "exp": 1, "binning": 1},
    "AFIS": {"beam": 44.460, "spot": 3, "mag": 92000, "exp": 1, "binning": 2, "defocus": -2, "max_imgsh": 6.0, "spec": (1200, 15)},
}

# Set which params dict to use
params_dict = krios2_falcon4
