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
import matplotlib.pyplot as plt

from ..common import BaseSetup


class InfoLimit(BaseSetup):
    """ Information limit test.

        Take two images with a small image shift (2 nm), add them together and calculate FFT.
        You should observe Young fringes going up to 1 A (Krios G3i spec is 2.3 A at 0 tilt). """

    def __init__(self, logFn="info_limit_0-tilt", **kwargs):
        super().__init__(logFn, **kwargs)
        self.shift = 0.002  # image shift in um
        self.delay = 5  # in sec
        self.defocus = kwargs.get("defocus", -0.5)

    def run(self):
        logging.info(f"Starting test {type(self).__name__} {BaseSetup.timestamp()}")
        BaseSetup.setup_beam(self.mag, self.spot, self.beam_size)
        BaseSetup.setup_area(exp=1, binning=2, preset="R")
        BaseSetup.setup_area(exp=0.5, binning=2, preset="F")
        BaseSetup.autofocus(self.defocus, 0.05, do_coma=True)
        BaseSetup.check_drift()
        BaseSetup.setup_area(self.exp, self.binning, preset="R")
        BaseSetup.check_before_acquire()

        logging.info(f"Taking two images with {self.shift} um image shift difference")
        sem.SetDivideBy2(1)
        sem.Record()
        sem.ImageShiftByMicrons(self.shift, 0.)
        sem.Delay(self.delay)
        sem.Record()
        sem.AddImages("A", "B")
        sem.FFT("A")
        sem.SaveToOtherFile("A", "JPG", "NONE", self.logDir + f"/info_limit_0-tilt_{self.ts}.jpg")
        data = np.asarray(sem.bufferImage("AF")).astype("int16")
        params = sem.ImageProperties("A")
        dim, pix = params[0], params[4] * 10
        if 2*pix >= 1.0:
            logging.error(f"At this mag the Nyquist is at {2*pix}, cannot plot 1A ring!")
            sem.Exit(1)

        # plot 1A ring on FFT
        rad = dim * pix / 1
        ring = plt.Circle((dim/2, dim/2), rad, color='w', fill=False)
        fig, ax = plt.subplots(1, figsize=(19.2, 14.4))
        ax.imshow(data, cmap='gray')
        ax.add_patch(ring)
        plt.text(dim/2-rad-50, dim/2, "1A", color="w", size="xx-large")

        fig.tight_layout()
        fig.savefig(f"info_limit_0-tilt_{self.ts}.png")

        sem.ImageShiftByMicrons(-self.shift, 0.)
        logging.info(f"Completed test {type(self).__name__} {BaseSetup.timestamp()}")
        sem.Exit(1)
