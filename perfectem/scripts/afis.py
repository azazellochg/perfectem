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
import serialem as sem

from ..common import BaseSetup


class AFIS(BaseSetup):
    """ AFIS calibration check. SerialEM beam-tilt adjustment is ignored. EPU needs to be opened, acq mode = Faster

        Measure residual beam tilt at +-12 image shift positions. Shifts are along tilt axis! """

    def __init__(self, log_fn="afis", **kwargs):
        super().__init__(log_fn, **kwargs)
        self.defocus = kwargs.get("defocus", -2)
        self.shift = kwargs.get("max_imgsh", 12.0)

    def _run(self):
        sem.Pause("Open EPU and set Acquisition mode = Faster in the Session Setup")
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="R")
        self.setup_area(exp=0.5, binning=2, preset="F")
        sem.SetImageShift(0, 0)
        self.autofocus(self.defocus, 0.05, do_ast=True, do_coma=True)

        bis_positions = [(-self.shift, -self.shift),
                         (-self.shift, 0),
                         (-self.shift, self.shift),
                         (0, -self.shift),
                         (0, self.shift),
                         (self.shift, -self.shift),
                         (self.shift, self.shift)]
        
        sem.NoMessageBoxOnError()
        for img in bis_positions:
            sem.SetImageShift(img[0], img[1], self.DELAY+2)  # units match microns in delphi adapter    
            try:
                sem.FixComaByCTF(1, 1, 0)
            except sem.SEMerror as e:
                logging.error(str(e))
                continue
            bt_x, bt_y = sem.ReportComaTiltNeeded()
            logging.info(f"Residual beam tilt at {img} um: {round(bt_x, 3)}, {round(bt_y, 3)} mrad")

        sem.SetImageShift(0, 0)
        sem.NoMessageBoxOnError(0)
