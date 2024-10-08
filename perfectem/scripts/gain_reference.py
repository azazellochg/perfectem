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

from typing import Any
import numpy as np
from scipy.signal import correlate
import serialem as sem

from ..common import BaseSetup
from ..utils import plot_fft_and_text


class GainRef(BaseSetup):
    """
        Name: Gain reference check for a camera.
        Desc: Take a picture of a flood beam and check the auto-correlation.
    """

    def __init__(self, log_fn: str = "gain_ref", **kwargs: Any) -> None:
        super().__init__(log_fn, **kwargs)

    def _run(self) -> None:
        self.setup_beam(self.mag, self.spot, self.beam_size)
        sem.Pause("Please move stage to an empty area and center the beam")
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="R")
        self.check_before_acquire()

        sem.Record()
        data = np.asarray(sem.bufferImage("A")).astype("int16")
        # Subtract the mean to center the data
        data = data - np.mean(data)
        acf = correlate(data, data, method='fft')
        # Normalize the ACF
        acf /= np.max(acf)
        # Get the center of the ACF
        acf = acf[acf.shape[0] // 2:, acf.shape[1] // 2:]

        fig, axes = plot_fft_and_text(acf)
        fig.savefig(f"gain_check_acf_{self.timestamp}.png")
