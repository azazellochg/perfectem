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
from typing import List, Any, Optional
import matplotlib.pyplot as plt
import serialem as sem

from ..common import BaseSetup, pretty_date


class Eucentricity(BaseSetup):
    """
        Name: Stage eucentricity check
        Desc: Estimates X,Y and defocus offset while tilting the stage.
    """

    def __init__(self, log_fn: str = "eucentricity", **kwargs: Any):
        super().__init__(log_fn, **kwargs)
        self.increment = 5  # tilt step
        self.specification = kwargs.get("spec", (1, 3))

    def _tilt(self, tilt, x0, y0) -> Optional[List[float]]:
        sem.TiltTo(tilt)
        logging.info(f"Tilting to {tilt} deg.")
        x, y, z = sem.ReportStageXYZ()
        sem.AutoFocus(-1)
        defocus, *_ = sem.ReportAutoFocus()
        if sem.ReportMeanCounts("A") < 5:  # avoid grid bars
            return None

        return [tilt, abs(x-x0), abs(y-y0), abs(defocus+2)]

    def plot_results(self, results, x0, y0, z0) -> None:
        results = np.asarray(results)
        results = results[results[:, 0].argsort()]

        fig = plt.figure(figsize=(19.2, 14.4))
        gs = fig.add_gridspec(2, 2)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])

        ax1.plot(results[:, 0], results[:, 1], marker='o', label="X displacement (um)")
        ax1.plot(results[:, 0], results[:, 2], marker='o', label="Y displacement (um)")
        ax1.plot(results[:, 0], results[:, 3], marker='o', label="Defocus difference (um)")
        ax1.axhline(y=self.specification[0], color='r', linestyle='--')
        ax1.axhline(y=self.specification[1], color='r', linestyle='--')
        ax1.set_xlabel("Tilt angle, deg.")
        ax1.set_ylabel("Offset, um")

        ax1.grid(True)
        ax1.legend()

        textstr = f"""
                            Eucentricity test

                            Measurement performed       {pretty_date(get_time=True)}
                            Microscope type             {self.scope_name}
                            Recorded at magnification   {self.mag // 1000} kx
                            Stage position:             {[round(x, 2) for x in [x0,y0,z0]]}
                            Camera used                 {sem.ReportCameraName(self.CAMERA_NUM)}

                            Tilt the stage from 0 to max in both directions with
                            {self.increment} deg. increment and measure offset in X, Y and defocus

                            Specification (Krios G4): <1 um in X/Y, <3 um defocus
                """
        ax2.text(0, 0, textstr, fontsize=20)
        ax2.axis('off')

        lines, labels = fig.axes[-1].get_legend_handles_labels()
        fig.legend(lines, labels, bbox_to_anchor=(1.25, 0.8))
        fig.tight_layout()
        fig.savefig(f"eucentricity_{self.timestamp}.png")

    def _run(self) -> None:
        # Rough eucentricity first
        self.change_aperture("c2", 50)
        if not self.SCOPE_HAS_C3:
            self.setup_beam(mag=6700, spot=3, beamsize=58.329, mode="micro")
        else:
            self.setup_beam(mag=6500, spot=7, beamsize=11)

        self.setup_area(self.exp, self.binning, preset="T")
        offset = sem.ReportTiltAxisOffset()[0]
        logging.info(f"Currently set tilt axis offset: {offset}")
        self.check_before_acquire()
        self.euc_by_stage()

        # Autofocus
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="F")
        self.autofocus(-2, 0.1, do_ast=False)

        results: List[List] = []
        sem.TiltTo(0)
        x0, y0, z0 = sem.ReportStageXYZ()
        logging.info(f"Current stage position: {x0}, {y0}, {z0}")
        results.append([0, 0, 0, 0])

        for tilt in range(-5, -75, -self.increment):
            res = self._tilt(tilt, x0, y0)
            if res is not None:
                results.append(res)

        sem.TiltTo(0)
        sem.Delay(3)

        for tilt in range(5, 75, self.increment):
            res = self._tilt(tilt, x0, y0)
            if res is not None:
                results.append(res)

        sem.TiltTo(0)

        self.plot_results(results, x0, y0, z0)
