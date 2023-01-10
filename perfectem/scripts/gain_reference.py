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

from ..common import BaseSetup


class GainRef(BaseSetup):
    """ Gain reference check for Falcon.

    Take a picture of a flood beam and check the auto-correlation. """

    def __init__(self, logFn="gain_ref", **kwargs):
        super().__init__(logFn, **kwargs)

    def run(self):
        sem.Pause("Please move stage to an empty area")
        logging.info(f"Starting test {type(self).__name__} {BaseSetup.timestamp()}")
        BaseSetup.setup_beam(self.mag, self.spot, self.beam_size)
        BaseSetup.setup_area(self.exp, self.binning, preset="R")

        sem.Record()
        sem.SaveToOtherFile("A", "JPG", "NONE", self.logDir + f"/gain_check_{self.ts}.jpg")
        logging.info(f"Completed test {type(self).__name__} {BaseSetup.timestamp()}")
        sem.Exit(1)
