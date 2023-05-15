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
from typing import Any
import serialem as sem

from ..common import BaseSetup
from ..utils import pretty_date, mrad_to_invA


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

    def __init__(self, log_fn: str = "afis",
                 **kwargs: Any) -> None:
        super().__init__(log_fn, **kwargs)
        self.defocus = kwargs.get("defocus", -2)
        self.shift = kwargs.get("max_imgsh", 12.0)
        self.specification = kwargs.get("spec", (750, 100))  # for Krios (coma in nm, astig in nm)

    def _mrad_to_nm(self, mrad):
        return mrad_to_invA(mrad, sem.ReportHighVoltage() * 1000) * 10

    def _run(self) -> None:
        sem.Pause("Open EPU and set Acquisition mode = Faster in the Session Setup. Also change C2 aperture to 50 um")
        self.setup_beam(self.mag, self.spot, self.beam_size, check_dose=False)
        sem.Pause("Please center the beam, roughly focus the image, check beam tilt pp and rotation center")
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="R")
        self.setup_area(exp=1, binning=2, preset="F")
        sem.SetImageShift(0, 0)
        sem.SetUserSetting("DriftProtection", 0)  # to speed up
        self.autofocus(self.defocus, 0.05, do_ast=True, do_coma=True)

        bis_positions = [
            (-self.shift, -self.shift),
            (-self.shift, 0),
            (self.shift, 0),
            (0, -self.shift),
            (0, self.shift),
            (self.shift, self.shift)
        ]
        res = []
        
        sem.NoMessageBoxOnError()
        self.check_before_acquire()
        for img in bis_positions:
            sem.SetImageShift(img[0], img[1], self.DELAY)  # units ~ match microns in delphi scripting exampler
            try:
                sem.AutoFocus(-2)
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

        textstr = f"""
                    AFIS calibration check

                    Measurement performed       {pretty_date(get_time=True)}
                    Microscope type             {self.scope_name}
                    Recorded at magnification   {self.mag // 1000} kx
                    Defocus                     {self.defocus} um
                    Camera used                 {sem.ReportCameraName(self.CAMERA_NUM)}

                    Remaining coma and astigmatism are measured at +/- {self.shift} um positions.

                    Specification (Krios): coma < 750 nm, astigmatism < 10 nm for 5 um shift
                    Specification (Talos): coma < 1200 nm, astigmatism < 15 nm for 6 um shift
        """

        logging.info(textstr)
