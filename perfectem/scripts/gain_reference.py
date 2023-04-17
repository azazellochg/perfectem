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

from typing import Any
import serialem as sem

from ..common import BaseSetup


class GainRef(BaseSetup):
    """
        Name: Gain reference check for Falcon.
        Desc: Take a picture of a flood beam and check the auto-correlation.
    """

    def __init__(self, log_fn: str = "gain_ref", **kwargs: Any) -> None:
        super().__init__(log_fn, **kwargs)

    def _run(self) -> None:
        sem.Pause("Please move stage to an empty area")
        self.setup_beam(self.mag, self.spot, self.beam_size)
        sem.Pause("Please center the beam")
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="R")
        self.check_before_acquire()

        sem.Record()
        #get autocorrelation from sem or otherwise and save it
        sem.SaveToOtherFile("A", "JPG", "NONE", f"gain_check_{self.timestamp}.jpg")
