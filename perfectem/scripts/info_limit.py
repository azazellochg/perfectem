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

import logging
import numpy as np
import serialem as sem

from ..common import BaseSetup
from ..utils import plot_fft_and_text, pretty_date
from ..config import SCOPE_NAME


class InfoLimit(BaseSetup):
    """ Information limit test.

        Take two images with a small image shift (2 nm), add them together and calculate FFT.
        You should observe Young fringes going up to 1 A (Krios G3i spec is 2.3 A at 0 tilt). """

    def __init__(self, log_fn="info_limit_0-tilt", **kwargs):
        super().__init__(log_fn, **kwargs)
        self.shift = 0.002  # image shift in um
        self.delay = 5  # in sec
        self.defocus = kwargs.get("defocus", -0.5)
        self.specification = kwargs.get("spec", 0.14)  # for Krios, in nm

    def _run(self):
        sem.TiltTo(0)
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(exp=1, binning=2, preset="R")
        self.setup_area(exp=0.5, binning=2, preset="F")
        self.autofocus(self.defocus, 0.05, do_coma=True)
        self.check_drift()
        self.setup_area(self.exp, self.binning, preset="R")
        self.check_before_acquire()

        logging.info(f"Taking two images with {self.shift} um image shift difference")
        sem.SetDivideBy2(1)
        sem.Record()
        sem.ImageShiftByMicrons(self.shift, 0.)
        sem.Delay(self.delay)
        sem.Record()
        params = sem.ImageProperties("A")
        pix = params[4] * 10
        sem.AddImages("A", "B")
        sem.FFT("A")
        sem.SaveToOtherFile("AF", "JPG", "NONE", self.logDir + f"/info_limit_0-tilt_{self.ts}.jpg")
        sem.ImageShiftByMicrons(-self.shift, 0.)
        data = np.asarray(sem.bufferImage("AF")).astype("int16")

        textstr = f"""
                    INFORMATION LIMIT at 0 degrees tilt

                    Measurement performed       {pretty_date(get_time=True)}
                    Microscope name             {SCOPE_NAME}
                    Recorded at magnification   {self.mag // 1000} kx
                    Defocus                     {-self.defocus} um
                    Camera used                 {sem.ReportCameraName(self.CAMERA_NUM)}

                    The information limit is a measure of the highest frequency
                    that is transferred through the optical system. During exposure
                    of the CCD the image is shifted ~2nm to produce Young's fringes
                    in the FFT. The extent of the fringes is a measure of the information limit.

                    Specification: {self.specification} nm
        """

        fig, axes = plot_fft_and_text(data, spec=self.specification, pix=pix, text=textstr)
        fig.savefig(f"info_limit_0-tilt_{self.ts}.png")
