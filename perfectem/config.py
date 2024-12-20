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

SERIALEM_IP = "127.0.0.1"
SERIALEM_PORT = 48888
DEBUG = 0  # set to 1 for more diagnostic output

# beam size in microns (Krios, 3-cond. lenses) or percents (2-cond. lenses)

krios2_falcon4i = {
    "StageDrift": {"beam": 0.7, "spot": 7, "mag": 96000, "exp": 1, "binning": 2},
    "Anisotropy": {"beam": 0.7, "spot": 7, "mag": 96000, "exp": 1, "binning": 2},
    "InfoLimit": {"beam": 0.42, "spot": 2, "mag": 740000, "exp": 3, "binning": 2, "defocus": -0.5, "spec": 0.14},
    "ThonRings": {"beam": 0.7, "spot": 2, "mag": 250000, "exp": 1, "binning": 2, "defocus": -1, "spec": 0.33},
    "PointRes": {"beam": 0.7, "spot": 2, "mag": 380000, "exp": 2, "binning": 2, "defocus": -0.087, "spec": 0.20},
    "GoldDiffr": {"beam": 0.42, "spot": 2, "mag": 740000, "exp": 3, "binning": 2, "defocus": -0.5, "spec": 0.1},
    "C2Fringes": {"beam": 0.7, "spot": 7, "mag": 96000, "exp": 1, "binning": 1},
    "TiltAxis": {"beam": 0.9, "spot": 7, "mag": 75000, "exp": 1, "binning": 2},
    "GainRef": {"beam": 0.7, "spot": 7, "mag": 96000, "exp": 1, "binning": 1},
    "AFIS": {"beam": 0.7, "spot": 7, "mag": 96000, "exp": 1, "binning": 2, "defocus": -2, "max_imgsh": 12.0, "spec": (750, 10)},  # specs: (coma in nm, astig in nm)
    "Eucentricity": {"beam": 0.9, "spot": 7, "mag": 75000, "exp": 1, "binning": 2, "spec": (2, 4)},
}

krios1_k3 = {
    "StageDrift": {"beam": 1.1, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2},
    "Anisotropy": {"beam": 1.1, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2},
    "InfoLimit": {"beam": 0.42, "spot": 2, "mag": 710000, "exp": 3, "binning": 2, "defocus": -0.5, "spec": 0.14},
    "ThonRings": {"beam": 0.7, "spot": 2, "mag": 270000, "exp": 1, "binning": 2, "defocus": -1, "spec": 0.33},
    "PointRes": {"beam": 0.7, "spot": 2, "mag": 350000, "exp": 1, "binning": 2, "defocus": -0.087, "spec": 0.20},
    "GoldDiffr": {"beam": 0.42, "spot": 2, "mag": 710000, "exp": 3, "binning": 2, "defocus": -0.5, "spec": 0.1},
    "C2Fringes": {"beam": 0.42, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 1, "defocus": -1.0},
    "TiltAxis": {"beam": 1.1, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2},
    "GainRef": {"beam": 1.1, "spot": 5, "mag": 105000, "exp": 1, "binning": 1},
    "AFIS": {"beam": 1.1, "spot": 5, "mag": 105000, "exp": 1, "binning": 2, "defocus": -2, "max_imgsh": 12.0, "spec": (750, 10)},
    "Eucentricity": {"beam": 1.1, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2, "spec": (2, 4)},
}

krios3_k3 = {
    "StageDrift": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2},
    "Anisotropy": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2},
    "InfoLimit": {"beam": 1.02, "spot": 2, "mag": 710000, "exp": 3, "binning": 2, "defocus": -0.5, "spec": 0.14},
    "ThonRings": {"beam": 1.02, "spot": 3, "mag": 270000, "exp": 1, "binning": 2, "defocus": -1, "spec": 0.33},
    "PointRes": {"beam": 1.02, "spot": 3, "mag": 350000, "exp": 1, "binning": 2, "defocus": -0.087, "spec": 0.20},
    "GoldDiffr": {"beam": 1.02, "spot": 3, "mag": 710000, "exp": 3, "binning": 2, "defocus": -0.5, "spec": 0.1},
    "C2Fringes": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 1, "defocus": -1.0},
    "TiltAxis": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2},
    "GainRef": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 1, "binning": 1},
    "AFIS": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 1, "binning": 2, "defocus": -2, "max_imgsh": 12.0, "spec": (750, 10)},
    "Eucentricity": {"beam": 0.66, "spot": 5, "mag": 105000, "exp": 0.5, "binning": 2, "spec": (2, 4)},
}

krios4_F4i = {
    "StageDrift": {"beam": 0.8, "spot": 5, "mag": 130000, "exp": 1, "binning": 2},
    "Anisotropy": {"beam": 0.8, "spot": 5, "mag": 130000, "exp": 1, "binning": 2},
    "InfoLimit": {"beam": 0.32, "spot": 2, "mag": 910000, "exp": 3, "binning": 2, "defocus": -0.5, "spec": 0.12},
    "ThonRings": {"beam": 1.0, "spot": 3, "mag": 270000, "exp": 1, "binning": 2, "defocus": -1, "spec": 0.33},
    "PointRes": {"beam": 1.0, "spot": 3, "mag": 350000, "exp": 1, "binning": 2, "defocus": -0.087, "spec": 0.20},
    "GoldDiffr": {"beam": 0.32, "spot": 2, "mag": 910000, "exp": 3, "binning": 2, "defocus": -0.5, "spec": 0.1},
    "C2Fringes": {"beam": 0.8, "spot": 5, "mag": 130000, "exp": 1, "binning": 1, "defocus": -1.0},
    "TiltAxis": {"beam": 0.8, "spot": 5, "mag": 130000, "exp": 1, "binning": 2},
    "GainRef": {"beam": 0.8, "spot": 5, "mag": 130000, "exp": 1, "binning": 1},
    "AFIS": {"beam": 0.8, "spot": 5, "mag": 130000, "exp": 1, "binning": 2, "defocus": -2, "max_imgsh": 12.0, "spec": (750, 10)},
    "Eucentricity": {"beam": 0.8, "spot": 5, "mag": 130000, "exp": 1, "binning": 2, "spec": (2, 4)},
}

glacios_falcon3 = {
    "StageDrift": {"beam": 43.808, "spot": 2, "mag": 92000, "exp": 0.5, "binning": 2},
    "Anisotropy": {"beam": 43.808, "spot": 2, "mag": 92000, "exp": 1, "binning": 2},
    "InfoLimit": {"beam": 38.059, "spot": 2, "mag": 400000, "exp": 1.5, "binning": 1, "defocus": -0.5, "spec": 0.23},
    "ThonRings": {"beam": 38.016, "spot": 2, "mag": 240000, "exp": 1, "binning": 2, "defocus": -2, "spec": 0.37},
    "PointRes": {"beam": 38.059, "spot": 2, "mag": 400000, "exp": 1, "binning": 2, "defocus": -0.082, "spec": 0.24},
    "GoldDiffr": {"beam": 38.059, "spot": 2, "mag": 650000, "exp": 1, "binning": 2, "defocus": -0.5, "spec": 0.2},
    "C2Fringes": {"beam": 38.338, "spot": 5, "mag": 92000, "exp": 0.1, "binning": 1},
    "TiltAxis": {"beam": 43.808, "spot": 2, "mag": 92000, "exp": 0.5, "binning": 2},
    "GainRef": {"beam": 43.808, "spot": 2, "mag": 92000, "exp": 1, "binning": 1},
    "AFIS": {"beam": 43.808, "spot": 2, "mag": 92000, "exp": 1, "binning": 2, "defocus": -2, "max_imgsh": 12.0, "spec": (1200, 15)},
    "Eucentricity": {"beam": 43.808, "spot": 2, "mag": 92000, "exp": 0.5, "binning": 2, "spec": (2, 4)},
    "AtlasRealignment": {"beam": 100.0, "spot": 5, "mag": 170, "exp": 0.5, "binning": 2},
}

microscopes = {
    "Krios_1": krios1_k3,
    "Krios_2": krios2_falcon4i,
    "Krios_3": krios3_k3,
    "Krios_4": krios4_F4i,
    "Glacios": glacios_falcon3,
}
