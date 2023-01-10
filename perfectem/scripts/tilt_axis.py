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
import scipy.optimize as opt

from ..common import BaseSetup


class TiltAxis(BaseSetup):
    """ Tilt axis offset check

        Purpose:  Estimates tilt axis offset for PACEtomo. (Thanks to Wim Hagen for the suggestion!)
                  More information at http://github.com/eisfabian/PACEtomo
        Author:	  Fabian Eisenstein
        Created:  2022/05/10
        Revision: v1.1
    """

    def __init__(self, logFn="tilt_axis", **kwargs):
        super().__init__(logFn, **kwargs)
        self.increment = 5  # tilt step
        self.maxTilt = 15  # maximum +/- tilt angle
        self.offset = 5  # +/- offset for measured positions in microns from tilt axis
        # (also accepts lists e.g. [2, 4, 6])

    def _dZ(self, alpha, y0):
        return y0 * np.tan(np.radians(-alpha))

    def _Tilt(self, tilt, offsets, focus0, focus, angles):
        sem.TiltTo(tilt)

        for i in range(len(offsets)):
            sem.ImageShiftByMicrons(0, offsets[i])
            sem.AutoFocus(-1)
            defocus, *_ = sem.ReportAutoFocus()
            focus[i].append(float(defocus))
            sem.SetImageShift(0, 0)

        if tilt == 0:
            for j in range(len(offsets)):
                focus0.append(focus[j][-1])

        angles.append(float(tilt))

    def plot_results(self, offsets, relFocus, angles):
        offsets, relFocus = zip(*sorted(zip(offsets, relFocus)))  # ensure right order for plot points
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title('Z Shifts [microns]')
        for i in range(len(angles)):
            values = []
            for j in range(len(offsets)):
                values.append(relFocus[j][i])
            ax.plot(offsets, values, label=str(angles[i]) + " deg")

        ax.legend()
        fig.tight_layout()
        fig.savefig(f"tilt_axis_offset_{self.ts}.png")

    def run(self):
        logging.info(f"Starting test {type(self).__name__} {BaseSetup.timestamp()}")
        sem.ResetClock()
        # Rough eucentricity first
        BaseSetup.setup_beam(mag=11000, spot=5, beamsize=11)
        BaseSetup.setup_area(self.exp, self.binning, preset="V")
        oldOffset = sem.ReportTiltAxisOffset()[0]
        logging.info(f"Currently set tilt axis offset: {oldOffset}")
        sem.Eucentricity(1)

        # Autofocus
        BaseSetup.setup_beam(self.mag, self.spot, self.beam_size)
        BaseSetup.setup_area(self.exp, self.binning, preset="F")
        BaseSetup.autofocus(-2, 0.1, do_ast=False)

        starttilt = -self.maxTilt
        sem.TiltTo(starttilt)
        sem.TiltBy(-self.increment)

        offsets = [0]
        if isinstance(self.offset, (list, tuple)):
            for val in self.offset:
                offsets.extend([-val, val])
        else:
            offsets.extend([-self.offset, self.offset])

        angles = []
        focus = [[] for _ in range(len(offsets))]
        focus0 = []

        steps = 2 * self.maxTilt / self.increment + 1
        tilt = starttilt
        for i in range(int(steps)):
            logging.info(f"Tilt to {tilt} deg")
            self._Tilt(tilt, offsets, focus0, focus, angles)
            tilt += self.increment

        relFocus = focus
        for i in range(len(angles)):
            for j in range(len(offsets)):
                relFocus[j][i] -= focus0[j]

        y0 = np.zeros(len(offsets))
        for j in range(len(offsets)):
            y0[j], cov = opt.curve_fit(self._dZ, angles, relFocus[j], p0=0)

        logging.info(f"Remaining tilt axis offsets:")
        for i in range(0, len(offsets)):
            logging.info(f"[{offsets[i]}]: {round(y0[i] + offsets[i], 2)}")

        avgOffset = sum(y0) / len(offsets)
        logging.info(f"Average remaining tilt axis offset: {avgOffset:0.2f}")
        totalOffset = round(avgOffset + oldOffset, 2)
        logging.info(f"Total tilt axis offset is {totalOffset}")

        sem.TiltTo(0)
        sem.ResetImageShift()
        sem.ReportClock()

        self.plot_results(offsets, relFocus, angles)
        logging.info(f"Completed test {type(self).__name__} {BaseSetup.timestamp()}")
        sem.Exit(1)
