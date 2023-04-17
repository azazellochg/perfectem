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
from typing import Any
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

              1) The spatial coherence is given by the size of the source.
              Moreover, the illumination is never perfectly parallel and is actually
              slightly convergent at the best imaging condition. With a Cs-corrector, the dependence
              of spatial coherence on beam convergence may be eliminated completely at Cs = 0.
              2) In EM the condenser aperture is used to exclude electrons emitted at high angles
              from the electron gun, which will decrease the brightness but improve the quality
              of the illumination because these peripheral electrons are less coherent.
              3) When the C2 aperture is imaged out of focus, wave interference at the edge
              of the condenser beam appears as Fresnel fringes

    """

    def __init__(self, log_fn: str = "C2_fringes", **kwargs: Any) -> None:
        super().__init__(log_fn, **kwargs)
        self.defocus = kwargs.get("defocus", -1)  # relevant only for FFI
        self.integrate = 200  # line profile width, px

    def _run(self) -> None:
        self.change_aperture("c2", 50)
        self.setup_beam(self.mag, self.spot, self.beam_size, check_dose=False)
        sem.Pause("Please go to an empty area and center the beam")
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="R")
        sem.SetAbsoluteFocus(0)
        #sem.AutoCenterBeam()
        ffi = sem.YesNoBox("Does this system have Fringe-Free Illumination (FFI)?")
        if ffi:
            sem.ChangeFocus(self.defocus)
        self.check_before_acquire()
        sem.Record()
        params = sem.ImageProperties("A")
        dim_x, dim_y = params[0], params[1]
        data = np.asarray(sem.bufferImage("A")).astype("int16")
        if DEBUG:
            sem.SaveToOtherFile("A", "JPG", "NONE", f"C2_fringes_{self.timestamp}.jpg")

        # Rotate img by -45 deg and extract a line profile of certain width
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
        fig.savefig(f"C2_fringes_{self.timestamp}.png")
