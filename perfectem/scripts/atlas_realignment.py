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

import os
import random
import numpy as np
from typing import Any, List
import matplotlib.pyplot as plt
import serialem as sem

from ..common import BaseSetup
from ..config import DEBUG
from ..utils import pretty_date


class AtlasRealignment(BaseSetup):
    """
        Name: Atlas realignment test.
        Desc: Compare the shift and rotation between two atlases acquired when reloading the same grid.
        Specification: < 5um, < 10deg?
    """

    def __init__(self, log_fn: str = "atlas_realign", **kwargs: Any) -> None:
        super().__init__(log_fn, **kwargs)
        self.min_shift = 5  # X/Y um shift
        self.max_rotation = 10  # degrees

    def prepare_for_plot(self, data: List[List]) -> None:
        avg = np.mean(np.asarray(data), 0)

        fig = plt.figure(figsize=(19.2, 14.4))
        ax1 = fig.add_subplot()
        textstr = f"""
                    Autoloader reproducibility test

                    Measurement performed       {pretty_date(get_time=True)}
                    Microscope type             {self.scope_name}
                    Recorded at magnification   {self.mag // 1000} kx
                    Camera used                 {sem.ReportCameraName(self.CAMERA_NUM)}
                    
                    Avg shiftX = {avg[1]:.1f}um, shiftY = {avg[2]:.1f}um, rotation = {avg[0]:.1f}deg

                    Atlas realignment is checked after reloading the same grid.
        """
        ax1.text(0, 0, textstr, fontsize=20)
        ax1.axis('off')

        fig.tight_layout()
        fig.savefig(f"atlas_realignment_{self.timestamp}.png")

    def _run(self) -> None:
        occupied_slots = []
        for grid in range(1, 13):
            status = sem.ReportSlotStatus(grid)
            if status == 1:
                occupied_slots.append(grid)

        min_choice = min(3, len(occupied_slots))
        grids_to_load = random.choices(occupied_slots, k=min_choice)
        results = []
        for grid in grids_to_load:
            # load and acquire
            sem.LoadCartridge(grid)
            if sem.ReportSlotStatus(grid) != 0:
                raise RuntimeError(f"Failed to load grid {grid}")
            sem.MoveStageTo(0, 0)
            if not self.SCOPE_HAS_C3:  # For Talos / Glacios
                self.change_aperture("c2", 150)
            self.setup_beam(self.mag, self.spot, self.beam_size, check_dose=False)
            self.setup_area(self.exp, self.binning, preset="R")
            self.check_before_acquire()
            sem.OpenNewMontage(2, 2, f"atlas_{grid}.mrc")
            sem.SetMontageParams(1)  # stage shift
            sem.Montage()
            sem.Copy("B", "M")  # copy overview
            sem.CloseFile()

            # reload
            sem.UnloadCartridge(grid)
            if sem.ReportSlotStatus(grid) != 1:
                raise RuntimeError(f"Failed to unload grid {grid}")
            sem.LoadCartridge(grid)
            if sem.ReportSlotStatus(grid) != 0:
                raise RuntimeError(f"Failed to load grid {grid}")
            sem.MoveStageTo(0, 0)

            # realign
            sem.Record()
            params = sem.ImageProperties("A")
            pix = params[4] / 1000  # um
            rot, x, y = sem.AlignWithRotation("M", 0, 40)
            x *= pix
            y *= pix
            results.append([x, y, rot])
            if not DEBUG:
                os.remove(f"atlas_{grid}.mrc")
                os.remove(f"atlas_{grid}.mrc.mdoc")

        self.prepare_for_plot(results)
