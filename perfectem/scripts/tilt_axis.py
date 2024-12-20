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
from typing import List, Any
import matplotlib.pyplot as plt
import scipy.optimize as opt
import serialem as sem

from ..common import BaseSetup


class TiltAxis(BaseSetup):
    """
        Name: Tilt axis offset check
        Desc: Estimates tilt axis offset for PACEtomo.
              More information at https://github.com/eisfabian/PACEtomo
        Author: Fabian Eisenstein
        Created: 2022/05/10
        Revision: v1.8
    """

    def __init__(self, log_fn: str = "tilt_axis", **kwargs: Any):
        super().__init__(log_fn, **kwargs)
        self.increment = 5  # tilt step
        self.maxTilt = 25  # maximum +/- tilt angle
        self.offset = 5  # +/- offset for measured positions in microns from tilt axis
        # (also accepts lists e.g. [2, 4, 6])

    @staticmethod
    def _dz(alpha: float, y0: float) -> Any:
        return y0 * np.tan(np.radians(-alpha))

    def _tilt(self, tilt: int, offsets: List[int],
              focus0: List[float], focus: List[List],
              angles: List[float]) -> None:
        sem.TiltTo(tilt)

        for i in range(len(offsets)):
            sem.ImageShiftByMicrons(0, offsets[i])
            sem.DriftWaitTask(2.0, "A", 180, 1, 1, "F")
            sem.AutoFocus(-1)
            defocus, *_ = sem.ReportAutoFocus()
            focus[i].append(float(defocus))
            sem.SetImageShift(0, 0)

        if tilt == 0:
            for j in range(len(offsets)):
                focus0.append(focus[j][-1])

        angles.append(float(tilt))

    def plot_results(self, offsets: List[int],
                     rel_focus: List[List],
                     angles: List[float]) -> None:
        offsets, rel_focus = zip(*sorted(zip(offsets, rel_focus)))  # ensure right order for plot points
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title("Tilt axis offset")
        ax.set_xlabel("Z shift, um")
        ax.set_ylabel("Defocus offset, um")
        for i in range(len(angles)):
            values = []
            for j in range(len(offsets)):
                values.append(rel_focus[j][i])
            ax.plot(offsets, values, label=str(angles[i]) + " deg")

        ax.legend()
        fig.tight_layout()
        fig.savefig(f"tilt_axis_offset_{self.timestamp}.png")

    def _run(self) -> None:
        # Rough eucentricity first
        self.change_aperture("c2", 50)
        if not self.SCOPE_HAS_C3:
            self.setup_beam(mag=6700, spot=3, beamsize=58.329, mode="micro")
        else:
            self.setup_beam(mag=6500, spot=7, beamsize=11)

        self.setup_area(self.exp, self.binning, preset="T")
        old_offset = sem.ReportTiltAxisOffset()[0]
        logging.info(f"Currently set tilt axis offset: {old_offset}")
        self.check_before_acquire()
        self.euc_by_stage()

        # Autofocus
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="F")
        self.autofocus(-2, 0.1, do_ast=False)

        starttilt = -self.maxTilt
        sem.TiltTo(starttilt)
        sem.TiltBy(-self.increment)

        offsets = [0]
        if isinstance(self.offset, (list, tuple)):
            for val in self.offset:
                offsets.extend([-val, val])
        else:
            offsets.extend([-self.offset, self.offset])

        angles: List[float] = []
        focus: List[List] = [[] for _ in range(len(offsets))]
        focus0: List[float] = []

        steps = 2 * self.maxTilt / self.increment + 1
        tilt = starttilt
        for i in range(int(steps)):
            logging.info(f"Tilt to {tilt} deg")
            self._tilt(tilt, offsets, focus0, focus, angles)
            tilt += self.increment

        rel_focus = focus
        for i in range(len(angles)):
            for j in range(len(offsets)):
                rel_focus[j][i] -= focus0[j]

        y0 = np.zeros(len(offsets))
        y0_neg = np.zeros(len(offsets))
        y0_pos = np.zeros(len(offsets))
        for j in range(len(offsets)):
            y0[j], *_ = opt.curve_fit(self._dz, angles, rel_focus[j], p0=0)
            y0_neg[j], *_ = opt.curve_fit(self._dz, [angle for angle in angles if angle <= 0],
                                          rel_focus[j][:len([angle for angle in angles if angle <= 0])],
                                          p0=0)
            y0_pos[j], *_ = opt.curve_fit(self._dz, [angle for angle in angles if angle >= 0],
                                          rel_focus[j][len([angle for angle in angles if angle < 0]):],
                                          p0=0)

        logging.info(f"Remaining tilt axis offsets:")
        for i in range(0, len(offsets)):
            logging.info(f"[{offsets[i]}]: {y0[i] + offsets[i]}, neg: "
                         f"{y0_neg[i] + offsets[i]}, pos: {y0_pos[i] + offsets[i]}")

        avg_offset = sum(y0) / len(offsets)
        avg_offset_neg = sum(y0_neg) / len(offsets)
        avg_offset_pos = sum(y0_pos) / len(offsets)

        logging.info(f"Average remaining tilt axis offset: {avg_offset:0.2f}, "
                     f"neg: {avg_offset_neg:0.2f}, pos: {avg_offset_pos:0.2f}")

        total_offset = avg_offset + old_offset
        logging.info(f"Total tilt axis offset is {total_offset:0.2f}")

        sem.TiltTo(0)
        sem.ResetImageShift()

        self.plot_results(offsets, rel_focus, angles)
