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

import datetime as dt
import logging
import numpy as np
import matplotlib.pyplot as plt

from ..common import BaseSetup
from ..config import SCOPE
from ..utils import radial_profile


class ThonRings(BaseSetup):
    """ Thon rings limit test.

        Take a high-resolution image on carbon and fit CTF rings as far as you can.
        Calculate a radial average from one quadrant and mark 0.33nm specification (Krios)

    """

    def __init__(self, logFn="thon_rings", **kwargs):
        super().__init__(logFn, **kwargs)
        self.defocus = kwargs.get("defocus", -0.5)

    def run(self):
        logging.info(f"Starting test {type(self).__name__} {BaseSetup.timestamp()}")
        BaseSetup.setup_beam(self.mag, self.spot, self.beam_size)
        BaseSetup.setup_area(self.exp, self.binning, preset="R")
        BaseSetup.setup_area(exp=0.5, binning=2, preset="F")
        BaseSetup.autofocus(self.defocus, 0.05)
        BaseSetup.check_drift()
        BaseSetup.check_before_acquire()

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
        sem.SaveToOtherFile("A", "JPG", "NONE", self.logDir + f"/thon_rings_{self.ts}.jpg")

        fig = plt.figure(figsize=(19.2, 14.4))
        gs = fig.add_gridspec(2, 2)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, :])

        # set X ticks to nm
        step = dim // 20
        a = np.arange(0, dim // 2, step)
        b = np.round(np.array([dim * pix / (i + 1e-5) for i in a]) / 10, 2)
        b[0] = np.inf

        textstr = f"""
                    THON RINGS

                    Measurement performed       {dt.datetime.now().strftime('%d-%m-%Y')}
                    Microscope type             {SCOPE}
                    Recorded at magnification   {self.mag // 1000} kx
                    Defocus                     {-self.defocus} um
                    Camera used                 {sem.ReportCameraName()}

                    The Thon ring profile is calculated from the FFT
                    of a high-resolution image.The profile itself is
                    a radial average of one top right quadrant.
        """

        ax1.imshow(data, cmap='gray')
        ax1.axis('off')
        ax2.text(0, 0.2, textstr, fontsize=20)
        ax2.axis('off')
        ax3.plot(rad)
        plt.xlabel('Resolution (nm)')
        plt.xticks(a.tolist(), b.tolist())
        plt.minorticks_on()
        plt.xlim(0)

        # mark 3.3A
        mark = dim * pix / 3.3
        value = rad[int(mark)]
        plt.annotate('0.33nm', xy=(mark, value + 0.01),
                     xytext=(mark, value + 0.1), fontsize=20,
                     arrowprops=dict(facecolor='red',
                                     shrink=0.05))

        fig.tight_layout()
        plt.grid()
        fig.savefig(f"thon_rings_{self.ts}.png")
        logging.info(f"Completed test {type(self).__name__} {BaseSetup.timestamp()}")
        sem.Exit(1)
