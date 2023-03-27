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

import math
import logging
import matplotlib.pyplot as plt
import serialem as sem

from ..common import BaseSetup
from ..utils import pretty_date
from ..config import SCOPE_NAME, DEBUG


class StageDrift(BaseSetup):
    """
        Name: Stage drift test.
        Desc: 1) From a starting position move 1 um in each
              direction and measure drift until it is below threshold.
              2) Repeat the same test by tilting to +/- 45 deg instead of shift
        Specification: < 0.5 nm/min
    """

    def __init__(self, log_fn="stage_drift", **kwargs):
        super().__init__(log_fn, **kwargs)
        self.drift_crit = 1  # stop after reaching this A/sec
        self.max_time = 180.  # give up after max_time in sec
        self.shift = 1  # shift in um to use
        self.tilt = 45  # tilt in deg to use
        self.times = 3  # times to move/measure in one direction

    def measure_drift(self):
        """ Measure drift in different directions N times. Return a dict with results. """
        moves = {"+X": (self.shift, 0),
                 "-X": (-self.shift, 0),
                 "+Y": (0, self.shift),
                 "-Y": (0, -self.shift),
                 "-A": -self.tilt,
                 "+A": self.tilt}

        res = {
            "+X": [],
            "-X": [],
            "+Y": [],
            "-Y": [],
            "-A": [],
            "+A": []
        }

        stage = sem.ReportStageXYZ()
        logging.info(f"Current position is: {stage}")

        def timer():
            """ Measure drift and save (drift, time) values"""
            sem.ResetClock()
            r = []
            while True:
                sem.AutoFocus(-2)
                (x, y) = sem.ReportFocusDrift()
                drift = 10 * math.sqrt(x ** 2 + y ** 2)
                t = sem.ReportClock()
                r.append((drift, t))
                if drift <= self.drift_crit:
                    logging.info(f"--> Drift reached {self.drift_crit} A/s after {t:0.2f}s")
                    break
                else:
                    logging.info(f"--> Elapsed time {t:0.2f}s: drift {drift:0.2f} A/s")
                if t > self.max_time:
                    logging.info(f"--> Reached {self.max_time}s limit. Giving up.")
                    break
            return r

        for move in moves.items():
            if "A" in move[0]:
                logging.info(f"Tilting in {move[0]} direction")
                sem.TiltTo(move[1], 1)
                r = timer()
                res[move[0]].append(r)
                sem.TiltTo(0, 1)
            else:
                logging.info(f"Moving 1um in {move[0]} direction")
                for i in range(self.times):
                    logging.info(f"Measure #{i + 1}")
                    sem.MoveStage(move[1][0], move[1][1])
                    r = timer()
                    res[move[0]].append(r)
            logging.info("-" * 40)

        if DEBUG:
            for i in res:
                logging.debug(f"{i}: {res[i]}")

        logging.info(f"Average of {self.times} trials:")
        avg_res = {}
        for move in res:
            t = []
            for trial in res[move]:
                if trial[-1][0] <= self.drift_crit:
                    t.append(trial[-1][1])
            if t:
                avg_time = sum(t) / len(t)
                logging.info(f"{move} drift reached {self.drift_crit} A/s in {avg_time:0.2f}s")
                avg_res[move] = avg_time
            else:
                logging.error(f"Target {self.drift_crit} A/s never reached.")

        return res, avg_res, stage

    def plot_results(self, res, avg_res, position):
        fig = plt.figure(figsize=(19.2, 14.4))
        gs = fig.add_gridspec(4, 2)
        ax0 = fig.add_subplot(gs[0, :])  # text
        ax1 = fig.add_subplot(gs[1, 1])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[2, 1])
        ax4 = fig.add_subplot(gs[2, 0])
        ax5 = fig.add_subplot(gs[3, 1])
        ax6 = fig.add_subplot(gs[3, 0])

        ax = [ax1, ax2, ax3, ax4, ax5, ax6]

        for r, a in zip(res, ax):
            data = res[r]

            for ind, i in enumerate(data):
                x = [k[1] for k in i]
                y = [k[0] for k in i]
                a.plot(x, y, marker='.', label="measure #%d" % (ind + 1))
                a.set_title('%s axis' % r)
                a.axhline(y=self.drift_crit, color='r', linestyle='--')
                if avg_res:
                    a.text(0.5, 0.5, 'Avg time: %0.2f s' % avg_res[r], transform=a.transAxes)
                else:
                    a.text(0.5, 0.5, 'Target drift not reached', transform=a.transAxes)
                a.grid(True)

        textstr = f"""
                            Stage drift test

                            Measurement performed       {pretty_date(get_time=True)}
                            Microscope type             {SCOPE_NAME}
                            Recorded at magnification   {self.mag // 1000} kx
                            Stage position:             {[round(x, 2) for x in position]}
                            Camera used                 {sem.ReportCameraName(self.CAMERA_NUM)}

                            1) From a starting position move {self.shift} um in each direction and 
                            measure drift until it is below threshold.
                            2) Measure drift after tilting to +/- {self.tilt} deg.

                            Specification (Krios): < 0.5 nm/min ?
                """
        ax0.text(0, 0, textstr, fontsize=20)
        ax0.axis('off')

        lines, labels = fig.axes[-1].get_legend_handles_labels()
        fig.legend(lines, labels, bbox_to_anchor=(1.25, 0.8))
        fig.tight_layout()
        fig.savefig(f"stage_drift_{self.ts}.png")

        #plt.ion()
        #plt.show()

    def _run(self):
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="F")
        self.autofocus(-2, 0.1, do_ast=False)
        self.check_before_acquire()

        res, avg_res, position = self.measure_drift()
        position = sem.ReportStageXYZ()
        self.plot_results(res, avg_res, position)
