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

import numpy as np
import matplotlib.pyplot as plt
import logging
from datetime import datetime
from typing import Tuple, Optional, List, Any


def pretty_date(get_time: bool = False) -> str:
    """ Return current datetime in a pretty format. """
    date_str = '%d-%m-%Y'
    if get_time:
        date_str += ' %H:%M:%S'

    return datetime.now().strftime(date_str)


def moving_average(x: np.ndarray, window: int) -> np.ndarray:
    """ Calculate moving avg. Return a numpy array. """
    return np.convolve(x, np.ones(window), 'valid') / window


def radial_profile(data: np.ndarray) -> np.ndarray:
    """ Calculate rotational average, as in https://stackoverflow.com/a/21242776/2641718 """
    y, x = np.indices(data.shape)
    center = np.array([(x.max() - x.min()) / 2.0, (y.max() - y.min()) / 2.0])
    r = np.sqrt((x-center[0])**2 + (y-center[1])**2)
    r = r.astype(int)
    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / nr

    return radialprofile[2:int(center[0])]


def plot_fft_and_text(data: np.ndarray, spec: Optional[float] = None,
                      pix: float = 1.0, text: Optional[str] = None,
                      add_bottom_plot: bool = False) -> Tuple[Any, List[Any]]:
    """ Two subplots arranged horizontally: FFT (with an optional ring) and some text.
    :param data: fft data
    :param spec: specification in nm for plotting a circle onto fft
    :param pix: pixel size in A, required for the spec plot
    :param text: text for the second subplot
    :param add_bottom_plot: create an optional bottom plot (second row)

    """
    fig = plt.figure(figsize=(19.2, 14.4))
    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    axes = [ax1, ax2]
    if add_bottom_plot:
        ax3 = fig.add_subplot(gs[1, :])
        axes.append(ax3)

    ax1.imshow(data, cmap='gray')
    ax1.axis('off')

    if spec is not None:
        # mark specification
        dim = data.shape[0]  # fft should be squared already
        if 2*pix >= spec*10:
            logging.error(f"At this mag the Nyquist is at {2*pix}, cannot plot {spec*10}A ring!")
        else:
            rad = dim*pix / (spec * 10)
            ring = plt.Circle((dim/2, dim/2), rad, color='w', fill=False, linestyle='--')
            ax1.add_patch(ring)

    if text is not None:
        ax2.text(0, 0.2, text, fontsize=20)

    ax2.axis('off')

    fig.tight_layout()

    return fig, axes


def invert_pixel_axis(dims: int = 1024, pixsize: float = 1.0) -> Tuple[Any, List]:
    """ Convert X axis from pixel values to resolution (nm).
        To be used in FFT plots. Returns new X axis ticks and labels.

        :param dims: size of the FFT
        :param pixsize: pixel size in Angstroms
    """
    step = dims // 20
    x_ticks = np.arange(0, dims//2, step)
    x_labels = np.round(np.array([dims*pixsize / (i + 1e-5) for i in x_ticks]) / 10, 2)
    x_labels[0] = np.inf

    return x_ticks.tolist(), x_labels.tolist()


def mrad_to_invA(mrad, eV):
    """ Convert mrad to inverse Angstrom. Taken from https://github.com/HamishGBrown/py_multislice """

    # Planck's constant times speed of light in eV Angstrom
    hc = 1.23984193e4
    # Electron rest mass in eV
    m0c2 = 5.109989461e5
    E = np.sqrt(eV * (eV + 2 * m0c2)) / hc

    return mrad * E / 1000


def invA_to_mrad(invA, eV):
    """ Convert inverse Angstrom to mrad. Taken from https://github.com/HamishGBrown/py_multislice """

    # Planck's constant times speed of light in eV Angstrom
    hc = 1.23984193e4
    # Electron rest mass in eV
    m0c2 = 5.109989461e5
    E = np.sqrt(eV * (eV + 2 * m0c2)) / hc

    return invA / E * 1000
