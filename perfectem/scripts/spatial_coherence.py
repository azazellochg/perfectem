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
import scipy.ndimage as ndimg
from scipy.signal import savgol_filter

from ..common import BaseSetup


class C2Fringes(BaseSetup):
    """ Source spatial coherence test

    Take a picture of a flood beam to see if the fringes from C2 aperture extend all the way to the center. """

    def __init__(self, logFn="C2_fringes", **kwargs):
        super().__init__(logFn, **kwargs)

    def run(self):
        sem.Pause("Please move stage to an empty area")
        logging.info(f"Starting test {type(self).__name__} {BaseSetup.timestamp()}")
        BaseSetup.setup_beam(self.mag, self.spot, self.beam_size)
        BaseSetup.setup_area(self.exp, self.binning, preset="R")

        sem.Record()
        params = sem.ImageProperties("A")
        dimX, dimY = params[0], params[1]
        data = np.asarray(sem.bufferImage("A")).astype("int16")
        sem.SaveToOtherFile("A", "JPG", "NONE", self.logDir + f"/C2_fringes_{self.ts}.jpg")

        # Extract the line
        x1, y1 = dimX/2, dimY/2
        num = int(np.sqrt((dimX/2) ** 2 + (dimY/2) ** 2))
        x, y = np.linspace(0, x1, num), np.linspace(0, y1, num)

        # Extract the values along the line, using cubic interpolation
        line_profile = ndimg.map_coordinates(data, np.vstack((x, y)))
        line_profile = savgol_filter(line_profile, 51, 3)  # window size 51, polynomial order 3

        fig, axes = plt.subplots(nrows=2, figsize=(19.2, 14.4))
        axes[0].imshow(data, cmap='gray')
        axes[0].plot([0, x1], [0, y1], 'ro-')
        axes[1].plot(line_profile)
        plt.ylabel('Counts')
        plt.minorticks_on()
        plt.xlim(0)
        plt.grid(True)

        fig.tight_layout()
        fig.savefig(f"C2_fringes_{self.ts}.png")
        logging.info(f"Completed test {type(self).__name__} {BaseSetup.timestamp()}")
        sem.Exit(1)
