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
import serialem as sem

from ..common import BaseSetup
from ..utils import plot_fft_and_text, pretty_date
from ..config import SCOPE_NAME


class GoldDiffr(BaseSetup):
    """ Take high mag image of gold and check the diffraction spots up to 1 A in all directions. """

    def __init__(self, log_fn="gold_diffr", **kwargs):
        super().__init__(log_fn, **kwargs)
        self.defocus = kwargs.get("defocus", -0.5)
        self.specification = kwargs.get("spec", 0.1)  # for Krios, in nm

    def _run(self):
        sem.Pause("Please change C2 aperture to 150um")
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(exp=3, binning=4, preset="F")
        self.setup_area(exp=3, binning=4, preset="R")
        self.autofocus(self.defocus, 0.05, do_coma=True)
        self.check_drift()
        self.setup_area(self.exp, self.binning, preset="R")
        self.check_before_acquire()

        sem.SetDivideBy2(1)
        sem.Record()
        params = sem.ImageProperties("A")
        pix = params[4] * 10
        sem.FFT("A")
        sem.SaveToOtherFile("AF", "JPG", "NONE", self.logDir + f"/gold_diffr_{self.ts}.jpg")
        data = np.asarray(sem.bufferImage("AF")).astype("int16")

        textstr = f"""
                    DIFFRACTION LIMIT at 0 degrees tilt

                    Measurement performed       {pretty_date(get_time=True)}
                    Microscope type             {SCOPE_NAME}
                    Recorded at magnification   {self.mag // 1000} kx
                    Defocus                     {-self.defocus} um
                    Camera used                 {sem.ReportCameraName(self.CAMERA_NUM)}

                    One should see gold diffraction spots beyond 1 A.

                    Specification: {self.specification} nm
        """

        fig, axes = plot_fft_and_text(data, spec=self.specification, pix=pix, text=textstr)
        fig.savefig(f"gold_diffr_{self.ts}.png")
