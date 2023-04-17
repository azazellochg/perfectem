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
from typing import Tuple, Any, List
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
import serialem as sem

from ..common import BaseSetup
from ..utils import pretty_date
from ..config import DEBUG


class Anisotropy(BaseSetup):
    """
        Name: Magnification anisotropy test.
        Desc: Acquire a defocus series and plot astigmatism versus defocus.
              Calculate anisotropy by estimating deviation from linear behaviour.
        Notes: Calculation funcs are written by Greg McMullan @ MRC-LMB.
               Run this test for both pre-GIF and post-GIF camera
        Specification: < 1%
    """

    def __init__(self, log_fn: str = "mag_anisotropy", **kwargs: Any) -> None:
        super().__init__(log_fn, **kwargs)
        self.num_img = 10  # number of images
        self.def_min = 5000  # min def in Angstroms
        self.def_max = 50000  # max def in Angstroms

    def _find_limits(self, defocus: float, var: np.ndarray) -> Tuple[float, ...]:
        """ The analytic expressions are very ugly and
            so it is simpler to just search over the range. """

        fmax = -1000000000.0
        fmin = 1000000000.0
        amax = -1000000000.0
        amin = 1000000000.0

        nsearch = 200
        dphi = math.pi / nsearch
        for i in range(nsearch):
            phi = -0.5 * math.pi + dphi * i
            mt = 1.0 + 0.5 * var[0] * math.cos(2 * (phi - var[1]))
            at = defocus + 0.5 * var[2] * math.cos(2 * (phi - var[3]))
            tst = mt * mt * at
            if tst > fmax:
                fmax = tst
                amax = phi

            if tst < fmin:
                fmin = tst
                amin = phi

        while 2 * amax > math.pi:
            amax -= math.pi

        while 2 * amax + math.pi < 0.0:
            amax += math.pi

        return fmax, fmin, amax, amin

    def _fun(self, var: np.ndarray, data: np.ndarray) -> float:
        """
           Integral of 0 to 2pi of the square of the difference. This can
           be done analytically but the expressions are awful and so
           it is simpler (and numerically accurate) to just use the
           numerical integration -- here it is the DFT which is exact
           for low order cos/sin functions.
        """
        _sum = 0.0
        nsteps = 8
        dphi = 2 * math.pi / nsteps
        for i in range(nsteps):
            phi = dphi * i
            mt = 1.0 + 0.5 * var[0] * math.cos(2 * (phi - var[1]))
            mtt = mt * mt
            dast = 0.5 * var[2] * math.cos(2 * (phi - var[3]))

            for d in data:
                defocus_data = d[0]
                astig_data = d[1]
                phi_data = d[2]

                di = defocus_data + 0.5 * astig_data * math.cos(2 * (phi - phi_data))
                ti = mtt * (defocus_data + dast)
                _sum += (di - ti) * (di - ti)

        _sum = dphi * _sum

        return _sum

    def prepare_for_plot(self, data: List[List]) -> None:
        b = np.asarray(data)
        #dfmax = b[:, 0]
        #dfmin = b[:, 1]
        input_angles = np.copy(b[:, 2])

        b[:, 1] = (b[:, 0] - b[:, 1])
        b[:, 0] = b[:, 0] - 0.5 * b[:, 1]
        b[:, 2] = (math.pi / 180.0) * b[:, 2]

        var = np.array([0.0, 0.0, 0.10, 2.0])
        results = opt.minimize(self._fun, var, args=b, method='Powell')

        # Fill var with the optimised results -- should check if
        # the optimiser was successful...
        var = results.x

        # Put the angles between -pi/2 and pi/2
        while 2 * var[1] > math.pi:
            var[1] -= math.pi
        while 2 * var[1] + math.pi < 0.0:
            var[1] += math.pi

        while 2 * var[3] > math.pi:
            var[3] -= math.pi
        while 2 * var[3] + math.pi < 0.0:
            var[3] += math.pi

        # Prepare data for plotting the fit
        # Cheating by numerically searching for max/min values
        nout = 100
        xout = np.zeros(nout)
        yout = np.zeros(nout)
        aout = np.zeros(nout)
        dmax = np.amax(b, axis=0)
        dfstep = 1.05 * dmax[0] / nout
        for i in range(nout):
            df = dfstep * i
            res = self._find_limits(df, var)
            xout[i] = df
            yout[i] = res[0] - res[1]
            aout[i] = 180.0 * res[2] / math.pi

        fig = plt.figure(figsize=(19.2, 14.4))
        gs = fig.add_gridspec(2, 2)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])

        ax1.plot(b[:, 0], b[:, 1], 'ro', label="Ast. magnitude (A)")
        ax1.plot(b[:, 0], input_angles, 'go', label="Ast. direction (deg)")
        ax1.plot(xout, yout, 'r')
        ax1.plot(xout, aout, 'g')
        ax1.grid(True)
        ax1.legend()

        astig_str = 'Residual astigmatism ' + '{:6.1f}'.format(var[2]) + u'\u212b'
        angast_str = 'Direction ' + '{:6.1f}'.format(180.0 * var[3] / math.pi) + '\u00b0'
        anisomag_str = 'Anisotropy ' + '{:6.2f}'.format(100 * var[0]) + '%'
        anisoang_str = 'Aniso angle ' + '{:6.1f}'.format(180.0 * var[1] / math.pi) + '\u00b0'

        ax1.set_xlabel(r'Defocus ($\mathrm{\AA}$)')
        ax1.set_ylabel('Astigmatism magnitude and direction')

        label = "\n".join([astig_str, angast_str, anisomag_str, anisoang_str])
        logging.info("############# Results #############")
        logging.info(f"Detector: {sem.ReportCameraName(self.CAMERA_NUM)}")
        logging.info(label)

        textstr = f"""
                    Linear magnification anisotropy

                    Measurement performed       {pretty_date(get_time=True)}
                    Microscope type             {self.scope_name}
                    Recorded at magnification   {self.mag // 1000} kx
                    Defocus range               {self.def_min // 10000}-{self.def_max // 10000} um
                    Camera used                 {sem.ReportCameraName(self.CAMERA_NUM)}

                    Anisotropy is measured as a deviation from linear
                    dependence of astigmatism vs defocus.

                    {astig_str}
                    {angast_str}
                    {anisomag_str}
                    {anisoang_str}

                    Specification: anisotropy <1%
        """
        ax2.text(0, 0, textstr, fontsize=20)
        ax2.axis('off')

        fig.tight_layout()
        fig.savefig(f"mag_anisotropy_{self.timestamp}.png")

    def _run(self) -> None:
        self.change_aperture("c2", 50)
        self.setup_beam(self.mag, self.spot, self.beam_size, check_dose=False)
        sem.Pause("Please center the beam, roughly focus the image, check beam tilt pp and rotation center")
        self.setup_beam(self.mag, self.spot, self.beam_size)
        self.setup_area(self.exp, self.binning, preset="R")
        self.setup_area(self.exp, self.binning, preset="F")
        self.autofocus(0, 0.05)
        sem.ResetDefocus()
        sem.SaveFocus()
        self.check_before_acquire()

        results = []
        step = (self.def_max - self.def_min) // self.num_img
        def_set = self.def_min
        while True:
            if def_set > self.def_max:
                break
            logging.info(f"Acquiring image with defocus of {-def_set} A")
            sem.SetDefocus(-def_set / 10000)
            sem.Record()
            if DEBUG:
                sem.SaveToOtherFile("A", "JPG", "NONE", f"def_{def_set}.jpg")
            sem.FFT("A")
            try:
                min_limit = -def_set/10000+2
                if min_limit >= 0:
                    min_limit = -def_set/10000/2
                def_get, ast_get, astang_get, _, _, _ = sem.CtfFind("A", min_limit,
                                                                    (-def_set/10000)-2, 0, 640)
                logging.info(f"--> Estimated defocus = {def_get * 10000:0.0f} A, "
                             f"astigmatism = {ast_get * 10000:0.0f} A, "
                             f"angle = {astang_get:0.1f}")
                # save defmax, defmin, astang
                results.append([(-2 * def_get * 10000 + ast_get * 10000)/2,
                                (-2 * def_get * 10000 - ast_get * 10000)/2,
                                astang_get])
                def_set += step
            except Exception as e:
                logging.error(str(e))

        self.prepare_for_plot(results)
        sem.RestoreFocus()
