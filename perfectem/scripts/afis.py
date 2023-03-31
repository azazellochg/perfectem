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
import matplotlib.pyplot as plt
import numpy as np
import serialem as sem

from ..common import BaseSetup
from ..utils import pretty_date
from ..config import SCOPE_NAME


class AFIS(BaseSetup):
    """
        Name: AFIS calibration check.
        Desc: Measure residual beam tilt and astigmatism at different
              image shift positions.
        Notes: SerialEM beam-tilt adjustment is ignored. EPU needs to be
               opened, Acquisition mode = Faster in the Session Setup.

        Specification (Krios): coma < 750 nm, astigmatism < 10 nm for 5 um shift
        Specification (Talos): coma < 1200 nm, astigmatism < 15 nm for 6 um shift
        Specification (Tundra): coma < 1300 nm, astigmatism < 30 nm for 6 um shift
    """

    def __init__(self, log_fn="afis", **kwargs):
        super().__init__(log_fn, **kwargs)
        self.defocus = kwargs.get("defocus", -2)
        self.shift = kwargs.get("max_imgsh", 12.0)
        self.specification = kwargs.get("spec", (750, 100))  # for Krios (coma in nm, astig in nm)

    def _run(self):
        sem.Pause("Open EPU and set Acquisition mode = Faster in the Session Setup")
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="R")
        self.setup_area(exp=0.5, binning=2, preset="F")
        sem.SetImageShift(0, 0)
        sem.SetUserSetting("DriftProtection", 0)  # to speed up
        self.autofocus(self.defocus, 0.05, do_ast=True, do_coma=True)

        bis_positions = [(-self.shift, 0),
                         (0, 0),
                         (self.shift, 0),
                         (0, -self.shift),
                         (0, 0),
                         (0, self.shift)]
        res = []
        
        sem.NoMessageBoxOnError()
        self.check_before_acquire()
        for img in bis_positions:
            sem.SetImageShift(img[0], img[1], self.DELAY)  # units match microns in delphi scripting exampler
            try:
                sem.FixAstigmatismByCTF(1, 1, 0)
                sem.FixComaByCTF(1, 1, 0)
            except sem.SEMerror as e:
                logging.error(str(e))

            ast_x, ast_y = sem.ReportStigmatorNeeded()
            bt_x, bt_y = sem.ReportComaTiltNeeded()
            logging.info(f"Residual beam tilt at {img} um: {round(bt_x, 3)}, {round(bt_y, 3)} mrad")
            logging.info(f"Residual astigmatism at {img} um: {round(ast_x, 3)}, {round(ast_y, 3)}")
            res.append((bt_x, bt_y, ast_x, ast_y))

        sem.SetImageShift(0, 0)
        sem.NoMessageBoxOnError(0)
        sem.SetUserSetting("DriftProtection", 1, 1)

        self.plot(bis_positions, res)

    def plot(self, positions, results):
        pos = np.asarray(positions)
        res = np.asarray(results)

        fig = plt.figure(figsize=(19.2, 14.4))
        gs = fig.add_gridspec(3, 2)
        ax0 = fig.add_subplot(gs[0, :])
        ax1 = fig.add_subplot(gs[1, 0])
        ax2 = fig.add_subplot(gs[1, 1])
        ax3 = fig.add_subplot(gs[2, 0])
        ax4 = fig.add_subplot(gs[2, 1])

        # image shift X
        ax1.plot(pos[:3, 0], res[:3, 0], 'r', label="Beam tilt X (mrad)")
        ax1.plot(pos[:3, 0], res[:3, 1], 'b', label="Beam tilt Y (mrad)")
        ax1.set_title('Optimized beam tilt')
        ax1.set_xlabel("Image shift X")
        ax1.legend()
        ax1.grid(True)

        ax2.plot(pos[:3, 0], res[:3, 2], 'gray', label="Obj. astigmatism X")
        ax2.plot(pos[:3, 0], res[:3, 3], 'g', label="Obj. astigmatism Y")
        ax2.set_title('Optimized objective astigmatism')
        ax2.set_xlabel("Image shift X")
        ax2.legend()
        ax2.grid(True)

        # image shift Y
        ax3.plot(pos[3:, 1], res[3:, 0], 'r', label="Beam tilt X (mrad)")
        ax3.plot(pos[3:, 1], res[3:, 1], 'b', label="Beam tilt Y (mrad)")
        ax3.set_title('Optimized beam tilt')
        ax3.set_xlabel("Image shift Y")
        ax3.legend()
        ax3.grid(True)

        ax4.plot(pos[3:, 1], res[3:, 2], 'gray', label="Obj. astigmatism X")
        ax4.plot(pos[3:, 1], res[3:, 3], 'g', label="Obj. astigmatism Y")
        ax4.set_title('Optimized objective astigmatism')
        ax4.set_xlabel("Image shift Y")
        ax4.legend()
        ax4.grid(True)

        textstr = f"""
                    AFIS calibration check

                    Measurement performed       {pretty_date(get_time=True)}
                    Microscope type             {SCOPE_NAME}
                    Recorded at magnification   {self.mag // 1000} kx
                    Defocus                     {self.defocus} um
                    Camera used                 {sem.ReportCameraName(self.CAMERA_NUM)}

                    Remaining coma and astigmatism are measured at +/- {self.shift} um positions.

                    Specification (Krios): coma < 750 nm, astigmatism < 10 nm for 5 um shift
                    Specification (Talos): coma < 1200 nm, astigmatism < 15 nm for 6 um shift
        """
        ax0.text(0, 0, textstr, fontsize=20)
        ax0.axis('off')
        fig.tight_layout()

        #plt.ion()
        #plt.show()
        fig.savefig(f"afis_{self.ts}.png")
