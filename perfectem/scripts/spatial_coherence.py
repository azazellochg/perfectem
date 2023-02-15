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
import scipy.ndimage as ndimg
import serialem as sem

from ..common import BaseSetup
from ..config import DEBUG


class C2Fringes(BaseSetup):
    """
        Name: Source spatial coherence test
        Desc: Take a picture of a flood beam to see if the fringes
              from C2 aperture extend all the way to the center (non-FFI systems).
              On FFI system there are should be only 1-2 fringes at low defocus
    """

    def __init__(self, log_fn="C2_fringes", **kwargs):
        super().__init__(log_fn, **kwargs)
        self.defocus = kwargs.get("defocus", -1)  # relevant only for FFI
        self.integrate = 200  # line profile width, px

    def _run(self):
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="R")
        sem.SetEucentricFocus(1)
        sem.Pause("Please move stage to an empty area and center the beam such that it can fit into the FOV")
        ffi = sem.YesNoBox("Does this system have Fringe-Free Illumination (FFI)?")
        if ffi:
            sem.SetDefocus(self.defocus)
        sem.Record()
        sem.SetDefocus(0)
        params = sem.ImageProperties("A")
        dim_x, dim_y = params[0], params[1]
        data = np.asarray(sem.bufferImage("A")).astype("int16")
        if DEBUG:
            sem.SaveToOtherFile("A", "JPG", "NONE", self.logDir + f"/C2_fringes_{self.ts}.jpg")

        # Rotate img by -45 deg and extract a line profile of certain wodth
        data = ndimg.rotate(data, -45)
        num = int(np.sqrt((dim_x//2) ** 2 + (dim_y//2) ** 2))
        half_width = self.integrate // 2
        rect = data[num-half_width:num+half_width, num//4:num]
        line_profile = np.average(rect, axis=0)
        weights = np.kaiser(22, 14)
        smooth_line_profile = np.convolve(weights / weights.sum(), line_profile)

        fig, axes = plt.subplots(nrows=2, figsize=(19.2, 14.4))
        axes[0].imshow(rect, cmap='gray')
        axes[1].plot(smooth_line_profile)
        plt.ylabel('Counts')
        plt.minorticks_on()
        plt.xlim(0)
        plt.grid(True)

        fig.tight_layout()
        fig.savefig(f"C2_fringes_{self.ts}.png")
