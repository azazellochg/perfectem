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
import math
import logging
import serialem as sem
from datetime import datetime

from .utils import pretty_date


class BaseSetup:
    """ Initialization and common functions. """

    def __init__(self, log_fn, scope_name, **kwargs):
        """ Setup logger, camera settings and set common SerialEM params. """

        self.scope_name = scope_name
        sem.NoMessageBoxOnError()
        self.SCOPE_HAS_C3 = self.func_is_implemented("ReportIlluminatedArea")
        self.SCOPE_HAS_AUTOFILL = self.func_is_implemented("AreDewarsFilling")
        self.SCOPE_HAS_APER_CTRL = self.func_is_implemented("ReportApertureSize", 1)
        self.CAMERA_NUM = 1
        self.CAMERA_HAS_DIVIDEBY2 = False
        self.DELAY = 3
        sem.NoMessageBoxOnError(0)

        self.setup_log(log_fn)
        logging.info(f"Microscope type detected: "
                     f"hasC3={self.SCOPE_HAS_C3}, "
                     f"hasAutofill={self.SCOPE_HAS_AUTOFILL}, "
                     f"hasApertureControl={self.SCOPE_HAS_APER_CTRL}")

        self.select_camera()

        sem.SetUserSetting("DriftProtection", 1, 1)

        # Set settings for astig & coma correction to match Record
        sem.SetUserSetting("CtfBinning", 0)
        sem.SetUserSetting("CtfDoFullArray", 0)
        sem.SetUserSetting("CtfDriftSettling", 0.)
        sem.SetUserSetting("CtfExposure", 0)
        sem.SetUserSetting("UserMaxCtfFitRes", 0)
        sem.SetUserSetting("MinCtfBasedDefocus", -0.4)
        sem.SetUserSetting("ComaIterationThresh", 0.02)
        sem.SetUserSetting("CtfUseFullField", 0)
        sem.SetUserSetting("UsersComaTilt", 5)

        # set common params for linear mode
        self.exp = kwargs.get("exp", 1.0)
        self.binning = kwargs.get("binning", 1)
        self.mag = kwargs.get("mag", 75000)
        self.beam_size = kwargs.get("beam", 1.1 if self.SCOPE_HAS_C3 else 44.46)
        self.spot = kwargs.get("spot", 3)

    def setup_log(self, log_fn):
        """ Create a log file for the script run. """

        self.ts = pretty_date()
        cwd = os.path.dirname(os.path.realpath(__file__))
        self.logDir = os.path.join(cwd, f"{self.scope_name} {self.ts}")
        os.makedirs(self.logDir, exist_ok=True)
        os.chdir(self.logDir)
        logging.basicConfig(level=logging.INFO,
                            datefmt='%d-%m-%Y %H:%M:%S',
                            format='%(asctime)s %(message)s',
                            handlers=[
                                logging.FileHandler(f"{log_fn}_{self.ts}.log", "w", "utf-8"),
                                logging.StreamHandler()])

        sem.SuppressReports()
        sem.ErrorsToLog()

    def select_camera(self):
        """ Choose camera to use. """

        camera_num = 1
        camera_names = []
        while True:
            name = sem.ReportCameraName(camera_num)
            if name == "NOCAM":
                break
            else:
                camera_names.append(name)
                camera_num += 1

        print("Choose camera to use with SerialEM:\n")
        for i, c in enumerate(camera_names):
            print(f"\t[{i + 1}] {c}")

        camera_num = int(input("\nInput the camera number: ").strip())
        if camera_num > len(camera_names) or camera_num < 1:
            raise IndexError("Wrong camera number!")
        else:
            sem.SelectCamera(camera_num)
            self.CAMERA_NUM = camera_num
            if "Falcon" not in sem.ReportCameraName(self.CAMERA_NUM):  # TODO: check this
                self.CAMERA_HAS_DIVIDEBY2 = True
            _, _, mode = sem.ReportMag()
            if mode == 1:  # EFTEM
                sem.SetSlitIn(0)  # retract slit

        if not sem.ReportColumnOrGunValve():
            print("Opening col. valves...")
            sem.SetColumnOrGunValve(1)
        sem.SetLowDoseMode(0)

    def func_is_implemented(self, func, arg=None):
        """ Check is SerialEM supports a certain command. """

        try:
            func = f"sem.{func}({arg if arg else ''})"
            eval(func)
            return True
        except:
            return False

    def _run(self):
        """ Should be implemented in a script. """

        raise NotImplementedError

    def run(self):
        """ Main function to execute a script. """

        test_name = type(self).__name__
        _dt = datetime.now()
        logging.info(f"Starting script {test_name} {_dt.strftime('%d/%m/%Y %H:%M:%S')}")

        try:
            if abs(sem.ReportTiltAngle()) > 0.1:
                sem.TiltTo(0)
            self._run()
        except Exception as e:
            logging.error(f"Script {test_name} has failed: {str(e)}")

        elapsed = datetime.now() - _dt
        logging.info(f"Completed script {test_name}, elapsed time: {elapsed}")

        sem.Exit(1)

    def check_eps(self):
        """ Check max eps after setup beam but before area setup. """

        logging.info("Checking dose rate...")
        old_exp, _ = sem.ReportExposure("F")
        old_bin = int(sem.ReportBinning("F"))

        self.setup_area(exp=0.25, binning=1, preset="F")
        sem.Focus()
        _, _, _, _, eps = sem.ElectronStats("A")
        logging.info(f"Dose rate: {eps} eps")
        spot = int(sem.ReportSpotSize())
        while True:
            if eps < 120.0:  # keep below 120 eps
                break
            else:
                eps /= 2
                spot += 1

        if spot != int(sem.ReportSpotSize()) and spot < 12:
            logging.info(f"Increasing spot size to {spot} to reduce dose rate below 120 eps")
            sem.SetSpotSize(spot)
            sem.NormalizeLenses(4)

        # Restore previous settings
        sem.SetExposure("F", old_exp)
        sem.SetBinning("F", old_bin)

    def check_drift(self, crit=2.0, interval=2, timeout=60):
        """ Wait for drift to go below crit in Angstroms/s.
        :param crit: A/s target rate
        :param interval: repeat every N seconds
        :param timeout: give up and raise error after N seconds
        """
        x, y = sem.ReportFocusDrift()[0], sem.ReportFocusDrift()[1]
        drift = math.sqrt(x**2 + y**2)
        if (10 * drift - crit) > 0.01:
            logging.info(f"Waiting for drift to get below {crit} A/sec...")
            sem.DriftWaitTask(crit, "A", timeout, interval, 1, "A")

    def setup_beam(self, mag, spot, beamsize, mode="nano", check_dose=False):
        """ Set illumination params. """

        logging.info(f"Setting illumination: probe={mode}, mag={mag}, spot={spot}, beam={beamsize}")

        new_probe = 0 if mode == "nano" else 1
        probe_changed = sem.ReportProbeMode() != new_probe
        old_mag, old_lm, _ = sem.ReportMag()
        mag_changed = old_mag != mag
        spot_changed = int(sem.ReportSpotSize()) != spot

        normalize = dict()
        if probe_changed:
            sem.SetProbeMode(mode)
            normalize.update({"PROJ": 1, "OBJ": 2, "COND": 4})
        if spot_changed:
            sem.SetSpotSize(spot)
            normalize.update({"COND": 4})
        if mag_changed:
            sem.SetMag(mag)
            normalize.update({"PROJ": 1, "COND": 4})
            _, new_lm, _ = sem.ReportMag()
            if new_lm != old_lm:
                normalize.update({"PROJ": 1, "OBJ": 2})

        norm = sum(normalize.values())
        if norm != 0:
            logging.info(f"Normalizing lenses... ({norm})")
            sem.NormalizeLenses(norm)

        if not self.SCOPE_HAS_C3:
            sem.SetPercentC2(beamsize)
        else:  # (illum. area, fraction)
            sem.SetIlluminatedArea(beamsize * 0.01)

        sem.Delay(self.DELAY)

        logging.info("Setting illumination: done!")
        if check_dose:
            self.check_eps()

    def setup_area(self, exp, binning, area="F", preset="F"):
        """ Setup camera settings for a certain preset. """

        logging.info(f"Setting camera: preset={preset}, exp={exp}, binning={binning}, area={area}")
        sem.SetExposure(preset, exp)
        sem.SetBinning(preset, binning)
        sem.SetCameraArea(preset, area)  # full area
        sem.SetProcessing(preset, 2)  # gain-normalized

        if sem.ReportReadMode(preset) != 0:
            sem.NoMessageBoxOnError()
            try:
                sem.SetK2ReadMode(preset, 0)  # linear mode
                sem.SetDoseFracParams(preset, 0, 0, 0)  # no frames
            except sem.SEMerror or sem.SEMmoduleError:
                pass
            sem.NoMessageBoxOnError(0)

        logging.info("Setting camera: done!")

    def euc_by_stage(self, fine=False):
        """ Check FOV before running eucentricity by stage. """

        min_FOV = sem.ReportProperty("EucentricityCoarseMinField")  # um
        pix = sem.ReportCurrentPixelSize("T")  # nm
        binning = sem.ReportBinning("T")
        area_x, area_y, _, _, _, _ = sem.ReportCameraSetArea("T")  # binned pix
        area = area_x * binning * pix / 1000  # um
        if area < min_FOV:
            logging.error(f"With current View settings, the FOV is "
                          f"{area} um < {min_FOV}, decrease the magnification!")
            sem.Exit()
        else:
            sem.SetAbsoluteFocus(0)
            sem.ChangeFocus(-50)
            sem.Eucentricity(2 if fine else 1)
            sem.ChangeFocus(50)

    def euc_by_beamtilt(self):
        """ Adapted from https://sphinx-emdocs.readthedocs.io/en/latest/serialEM-note-more-about-z-height.html#z-byv2-function """

        old_mag, _, _ = sem.ReportMag()
        old_spot = sem.ReportSpotSize()
        old_beam = sem.ReportIlluminatedArea()

        if not self.SCOPE_HAS_C3:
            self.setup_beam(mag=6700, spot=3, beamsize=58.329, mode="micro")
        else:
            self.setup_beam(mag=6500, spot=7, beamsize=11)
        self.setup_area(exp=0.5, binning=2, preset="F")

        sem.SaveFocus()
        sem.SetAbsoluteFocus(0)
        sem.ChangeFocus(-30)

        for i in range(2):
            sem.AutoFocus(-1)
            res = sem.ReportAutofocus()[0]
            if abs(res) < 0.3:
                break
            z = round(-1 * 0.72 * res, 2)  # 0.72 is to compensate the non-linear behavior of autofocus measurement
            sem.MoveStage(0, 0, z)
            print(f"Z changed by {z} um")

        sem.RestoreFocus()
        sem.SetMag(old_mag)
        sem.SetSpotSize(old_spot)
        sem.SetIlluminatedArea(old_beam)

    def autofocus(self, target, precision=0.05, do_ast=True, do_coma=False, high_mag=False):
        """ Autofocus until the result is within precision (um) from a target. """

        if do_ast:
            sem.SetAutofocusOffset(0)
            sem.SetTargetDefocus(-0.75 if high_mag else -2)
            sem.AutoFocus()

            try:
                logging.info("Correcting astigmatism...")
                sem.FixAstigmatismByCTF()
                if do_coma:
                    logging.info("Correcting coma...")
                    sem.FixComaByCTF()
            except Exception as e:
                logging.error(str(e))
                sem.Exit()

        sem.SetTargetDefocus(target)
        sem.SetAutofocusOffset(target / 2)
        logging.info(f"Autofocusing to {target} um...")
        sem.AutoFocus()
        v = sem.ReportAutoFocus()[0]
        while abs(v - target) > precision:
            sem.AutoFocus()
            v = sem.ReportAutoFocus()[0]

        logging.info(f"Autofocusing: done!")

    def check_before_acquire(self):
        """ Check dewars and pumps before acquiring. """

        logging.info("Checking dewars and pumps...")

        def _test():
            if self.SCOPE_HAS_AUTOFILL:
                return sem.AreDewarsFilling() == 0. and sem.IsPVPRunning() == 0.
            else:
                return sem.IsPVPRunning() == 0.

        for i in range(10):
            if _test():
                break
            else:
                logging.info("Dewars are filling or PVP running, waiting for 60 sec..")
                sem.Delay(60)
                i += 1
