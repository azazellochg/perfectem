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
import serialem as sem

from ..common import BaseSetup
from ..config import DEBUG
from ..utils import radial_profile, plot_fft_and_text, invert_pixel_axis, pretty_date


class ThonRings(BaseSetup):
    """
        Name: Thon rings limit test.
        Desc: Take a high-resolution image on carbon and fit CTF rings as far as you can.
              Calculate a radial average from one quadrant.
        Specification (Krios): rings visible beyond 0.33 nm at -1 um defocus.
        Specification (Glacios): rings visible beyond 0.37 nm at -2 um defocus.
    """

    def __init__(self, log_fn: str = "thon_rings", **kwargs: Any):
        super().__init__(log_fn, **kwargs)
        self.defocus = kwargs.get("defocus", -1)
        self.specification = kwargs.get("spec", 0.33)  # for Krios, in nm

    def _run(self) -> None:
        self.change_aperture("c2", 50)
        self.setup_beam(self.mag, self.spot, self.beam_size, check_dose=False)
        sem.Pause("Please center the beam, roughly focus the image, check beam tilt pp and rotation center")
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="R")
        self.setup_area(exp=0.5, binning=2, preset="F")
        self.autofocus(self.defocus, 0.05, high_mag=True)
        self.check_drift()
        self.check_before_acquire()

        if self.CAMERA_HAS_DIVIDEBY2:
            sem.SetDivideBy2(1)
        sem.Record()
        params = sem.ImageProperties("A")
        dim, pix = params[0], params[4] * 10
        sem.FFT("A")
        sem.CtfFind("A", -0.1, self.defocus-1, 0, 512)

        data = np.asarray(sem.bufferImage("AF")).astype("int16")
        # use only the top right quadrant
        res = np.copy(data)
        halfx, halfy = res.shape[0] // 2 - 1, res.shape[1] // 2 - 1
        res[:, :halfy] = 0
        res[halfx:, halfy:] = 0

        rad = radial_profile(res)
        if DEBUG:
            sem.SaveToOtherFile("AF", "JPG", "NONE", f"thon_rings_{self.timestamp}.jpg")

        textstr = f"""
                    THON RINGS

                    Measurement performed       {pretty_date(get_time=True)}
                    Microscope name             {self.scope_name}
                    Recorded at magnification   {self.mag // 1000} kx
                    Defocus                     {self.defocus} um
                    Camera used                 {sem.ReportCameraName(self.CAMERA_NUM)}

                    The Thon ring profile is calculated from the FFT
                    of a high-resolution image. The profile itself is
                    a radial average of one top right quadrant.

                    Specification: {self.specification} nm

        """

        fig, axes = plot_fft_and_text(data, spec=self.specification,
                                      pix=pix, text=textstr, add_bottom_plot=True)
        axes[-1].plot(rad)
        plt.xlabel('Resolution (nm)')
        x_ticks, x_labels = invert_pixel_axis(dim, pix)
        plt.xticks(x_ticks, x_labels)
        plt.minorticks_on()
        plt.xlim(0)

        # mark 0.33 nm
        mark = dim * pix / (self.specification * 10)
        value = rad[int(mark)]
        plt.annotate(f'{self.specification} nm', xy=(mark, value + 0.01),
                     xytext=(mark, value + 0.1), fontsize=20,
                     arrowprops=dict(facecolor='red',
                                     shrink=0.05))

        fig.tight_layout()
        plt.grid()
        fig.savefig(f"thon_rings_{self.timestamp}.png")
