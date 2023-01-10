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

from ..common import BaseSetup
from ..config import DEBUG


class StageDrift(BaseSetup):
    """ Stage drift test.

    At each Navigator position perform the following: move the stage in 4 directions by 1 um,
    3 times each direction, followed by drift estimation."""

    def __init__(self, logFn="stage_drift", **kwargs):
        super().__init__(logFn, **kwargs)
        self.drift_crit = 1  # stop after reaching this A/sec
        self.max_time = 180.  # give up after max_time in sec
        self.times = 3  # times to move/measure in one direction
        self.delay = 0  # delay in sec after moving to a stage position

    def measure_drift(self, nav_label):
        """ Measure drift in 4 directions N times. Return a dict with results. """
        moves = {"+X": (1, 0),
                 "-X": (-1, 0),
                 "+Y": (0, 1),
                 "-Y": (0, -1)}

        res = {
            "+X": [],
            "-X": [],
            "+Y": [],
            "-Y": []
        }

        logging.info(f"Starting test {type(self).__name__} {BaseSetup.timestamp()}")
        logging.info(f"Moving stage to a measuring position and settling for {self.delay}s")
        nav_index = int(sem.NavIndexWithLabel(nav_label))
        sem.MoveToNavItem(nav_index)
        sem.Delay(self.delay)

        stage = sem.ReportStageXYZ()
        logging.info(f"Current position is: {stage}")

        for move in moves.items():
            logging.info(f"Moving 1um in {move[0]} direction")
            for i in range(self.times):
                logging.info(f"Measure #{i + 1}")
                sem.MoveStage(move[1][0], move[1][1])
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

    def plot_results(self, res, avg_res, stage, nav_item):
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(19.2, 14.4),
                                                     gridspec_kw={'wspace': 0.5,
                                                                  'hspace': 0.5})
        ax = [ax1, ax2, ax3, ax4]

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

        fig.suptitle(f'Drift measurement at XYZ: {stage[0]:0.2f},{stage[1]:0.2f},{stage[2]:0.2f}')
        lines, labels = fig.axes[-1].get_legend_handles_labels()
        fig.legend(lines, labels, bbox_to_anchor=(1.25, 0.8))
        fig.tight_layout()
        fig.savefig(f"stage_drift_pos{nav_item}_{self.ts}.png")

        # plt.ion()
        # plt.show()
        # plt.pause(0.1)

    def run(self):
        """ Run the actual test for all points that have Acquire flag. """
        logging.info(f"Starting test {type(self).__name__} {BaseSetup.timestamp()}")
        BaseSetup.setup_beam(self.mag, self.spot, self.beam_size)
        BaseSetup.setup_area(self.exp, self.binning, preset="F")
        BaseSetup.autofocus(-2, 0.05, do_ast=False)

        isNavOpen = sem.ReportIfNavOpen()
        if not isNavOpen:
            sem.Exit(1, "Please open Navigator and add a few points for drift measuring")
        items = int(sem.ReportNumTableItems())
        items_to_use = list(range(1, items+1))
        sem.Pause("Found %d navigator items" % items)

        for nav_item in items_to_use:
            logging.info(f"Moving to item {nav_item}")
            res, avg_res, stage = self.measure_drift("%s" % nav_item)
            if DEBUG:
                logging.debug(f"Results for position at item {nav_item}: {res}")
            self.plot_results(res, avg_res, stage, nav_item)

        if not items_to_use:
            logging.error("No Acquire points found in Navigator. Exiting.")

        logging.info(f"Completed test {type(self).__name__} {BaseSetup.timestamp()}")
        sem.Exit(1)
