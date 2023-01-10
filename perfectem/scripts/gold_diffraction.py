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


class GoldDiffr(BaseSetup):
    """ Take high mag image of gold and check the diffraction spots up to 1 A in all directions. """

    def __init__(self, logFn="gold_diffr", **kwargs):
        super().__init__(logFn, **kwargs)
        self.defocus = kwargs.get("defocus", -0.5)

    def run(self):
        sem.Pause("Please change C2 aperture to 150um")

        logging.info(f"Starting test {type(self).__name__} {BaseSetup.timestamp()}")
        #BaseSetup.euc_by_beamtilt()
        BaseSetup.setup_beam(self.mag, self.spot, self.beam_size)
        BaseSetup.setup_area(exp=3, binning=4, preset="F")
        BaseSetup.setup_area(exp=3, binning=4, preset="R")
        BaseSetup.autofocus(self.defocus, 0.05, do_coma=True)
        BaseSetup.check_drift()
        BaseSetup.setup_area(self.exp, self.binning, preset="R")
        BaseSetup.check_before_acquire()

        sem.SetDivideBy2(1)
        sem.Record()
        sem.FFT("A")
        sem.SaveToOtherFile("A", "JPG", "NONE", self.logDir + f"/gold_diffr_{self.ts}.jpg")

        data = np.asarray(sem.bufferImage("AF")).astype("int16")
        fig, ax = plt.subplots(1, figsize=(19.2, 14.4))
        ax.imshow(data, cmap='gray')
        fig.tight_layout()
        fig.savefig(f"gold_diffr_{self.ts}.png")
        logging.info(f"Completed test {type(self).__name__} {BaseSetup.timestamp()}")
        sem.Exit(1)
