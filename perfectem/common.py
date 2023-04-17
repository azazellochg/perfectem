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
import time
import serialem as sem
from datetime import datetime
from typing import Optional, Any

from .utils import pretty_date
from .config import SERIALEM_PORT, SERIALEM_IP


class BaseSetup:
    """ Initialization and common functions. """

    def __init__(self, log_fn: str, scope_name: str, **kwargs: Any) -> None:
        """ Setup logger, camera settings and common SerialEM params. """

        sem.ConnectToSEM(SERIALEM_PORT, SERIALEM_IP)
        sem.NoMessageBoxOnError()
        self.scope_name = scope_name
        self.SCOPE_HAS_C3 = self.func_is_implemented("ReportIlluminatedArea")
        self.SCOPE_HAS_AUTOFILL = self.func_is_implemented("AreDewarsFilling")
        self.SCOPE_HAS_APER_CTRL = self.func_is_implemented("ReportApertureSize", 1)
        self.CAMERA_NUM = 1
        self.CAMERA_HAS_DIVIDEBY2 = False
        self.CAMERA_MODE = 0  # linear
        self.DELAY = 3
        sem.NoMessageBoxOnError(0)

        self.setup_log(log_fn)
        logging.info(f"Microscope type detected: "
                     f"hasC3={self.SCOPE_HAS_C3}, "
                     f"hasAutofill={self.SCOPE_HAS_AUTOFILL}, "
                     f"hasApertureControl={self.SCOPE_HAS_APER_CTRL}")

        self.select_camera()

        sem.ClearPersistentVars()
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

        # set default kwargs
        self.exp = kwargs.get("exp", 1.0)
        self.binning = kwargs.get("binning", 1)
        self.mag = kwargs.get("mag", 75000)
        self.beam_size = kwargs.get("beam", 1.1 if self.SCOPE_HAS_C3 else 44.46)
        self.spot = kwargs.get("spot", 3)

    def setup_log(self, log_fn: str) -> None:
        """ Create a log file for the script run. """

        self.timestamp = pretty_date()
        self.log_dir = f"{self.scope_name}_{self.timestamp}"
        os.makedirs(self.log_dir, exist_ok=True)
        os.chdir(self.log_dir)
        logging.basicConfig(level=logging.INFO,
                            datefmt='%d-%m-%Y %H:%M:%S',
                            format='%(asctime)s %(message)s',
                            handlers=[
                                logging.FileHandler(f"{log_fn}_{self.timestamp}.log", "w", "utf-8"),
                                logging.StreamHandler()])

        sem.SuppressReports()
        sem.ErrorsToLog()
        sem.SetDirectory(os.getcwd())

    def select_camera(self) -> None:
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
            cam_name = sem.ReportCameraName(self.CAMERA_NUM)
            if "Falcon" in cam_name:
                self.CAMERA_MODE = 0
                self.CAMERA_HAS_DIVIDEBY2 = False
            elif "K2" or "K3" in cam_name:
                self.CAMERA_MODE = 1  # always counting
                self.CAMERA_HAS_DIVIDEBY2 = True

            _, _, mode = sem.ReportMag()
            if mode == 1:  # EFTEM
                sem.SetSlitIn(0)  # retract slit

        if not sem.ReportColumnOrGunValve():
            print("Opening col. valves...")
            sem.SetColumnOrGunValve(1)

        sem.SetLowDoseMode(0)

        if self.SCOPE_HAS_APER_CTRL:
            # Retract objective aperture
            self.change_aperture("obj", 0)

    def func_is_implemented(self, func: str, arg: Optional[Any] = None) -> bool:
        """ Check is SerialEM supports a certain command. """

        try:
            func = f"sem.{func}({arg if arg else ''})"
            eval(func)
            return True
        except:
            return False

    def _run(self) -> None:
        """ Should be implemented in a script. """

        raise NotImplementedError

    def run(self) -> None:
        """ Main function to execute a script. """

        test_name = type(self).__name__
        start_time = datetime.now()
        logging.info(f"Starting script {test_name} {start_time.strftime('%d/%m/%Y %H:%M:%S')}")

        try:
            if abs(sem.ReportTiltAngle()) > 0.1:
                sem.TiltTo(0)
            self._run()
        except Exception as e:
            logging.error(f"Script {test_name} has failed: {str(e)}")

        elapsed = datetime.now() - start_time
        logging.info(f"Completed script {test_name}, elapsed time: {elapsed}")

        sem.Exit(1)

    def check_eps(self) -> None:
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
            if eps < 200.0:  # keep below 200 eps
                break
            else:
                eps /= 2
                spot += 1

        if spot != int(sem.ReportSpotSize()) and spot < 12:
            logging.info(f"Increasing spot size to {spot} to reduce dose rate below 120 eps")
            sem.SetSpotSize(spot)

        # Restore previous settings
        sem.SetExposure("F", old_exp)
        sem.SetBinning("F", old_bin)

    def check_drift(self, crit: float = 1.0,
                    interval: int = 1,
                    timeout: int = 180) -> None:
        """ Wait for drift to go below crit in Angstroms/s.
        :param crit: A/s target rate
        :param interval: repeat every N seconds
        :param timeout: give up and raise error after N seconds
        """

        (x, y) = sem.ReportFocusDrift()
        drift = math.sqrt(x**2 + y**2)
        if (10*drift - crit) > 0.01:
            logging.info(f"Waiting for drift to get below {crit} A/sec...")
            sem.DriftWaitTask(crit, "A", timeout, interval, 1, "F")

    def setup_beam(self, mag: int, spot: int, beamsize: float,
                   mode: str = "nano",
                   check_dose: bool = False) -> None:
        """ Set illumination params. """

        logging.info(f"Setting illumination: probe={mode}, mag={mag}, spot={spot}, beam={beamsize}")
        new_probe = 0 if mode == "nano" else 1
        probe_changed = sem.ReportProbeMode() != new_probe
        old_mag, old_lm, _ = sem.ReportMag()
        mag_changed = old_mag != mag
        spot_changed = int(sem.ReportSpotSize()) != spot

        if probe_changed:
            sem.SetProbeMode(mode)
        if spot_changed:
            sem.SetSpotSize(spot)
        if mag_changed:
            sem.SetMag(mag)

        if not self.SCOPE_HAS_C3:
            sem.SetPercentC2(beamsize)
        else:  # (illum. area, fraction)
            sem.SetIlluminatedArea(beamsize * 0.01)

        sem.Delay(self.DELAY)

        logging.info("Setting illumination: done!")
        if check_dose:
            self.check_eps()

    def setup_area(self, exp: float, binning: int,
                   area: str = "F",
                   preset: str = "F",
                   mode: Optional[str] = None) -> None:
        """ Setup camera settings for a certain preset. """

        logging.info(f"Setting camera: preset={preset}, exp={exp}, binning={binning}, area={area}")
        sem.SetExposure(preset, exp)
        sem.SetBinning(preset, binning)
        sem.SetCameraArea(preset, area)  # full area
        sem.SetProcessing(preset, 2)  # gain-normalized
        camera_mode = mode if mode is not None else self.CAMERA_MODE

        sem.NoMessageBoxOnError()
        try:
            sem.SetK2ReadMode(preset, camera_mode)  # linear=0, counting=1
            sem.SetDoseFracParams(preset, 0, 0, 0)  # no frames
        except sem.SEMerror or sem.SEMmoduleError:
            pass
        sem.NoMessageBoxOnError(0)

        logging.info("Setting camera: done!")

    def euc_by_stage(self, fine: bool = False) -> None:
        """ Check FOV before running eucentricity by stage. """

        min_fov = sem.ReportProperty("EucentricityCoarseMinField")  # um
        pix = sem.ReportCurrentPixelSize("T")  # nm, with binning
        area_x, area_y, _, _, _, _ = sem.ReportCameraSetArea("T")  # binned pix
        area = area_x * pix / 1000  # um
        if area < min_fov:
            logging.warning(f"With current View settings, the FOV is "
                            f"{area} um < EucentricityCoarseMinField={min_fov}, "
                            "SerialEM will decrease the magnification automatically")
        sem.SetAbsoluteFocus(0)
        sem.ChangeFocus(-50)
        sem.Eucentricity(2 if fine else 1)
        sem.ChangeFocus(50)

    def euc_by_beamtilt(self) -> None:
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

    def autofocus(self, target: float, precision: float = 0.05,
                  do_ast: bool = True, do_coma: bool = False,
                  high_mag: bool = False) -> None:
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

        if high_mag:
            # fix astigmatism again, closer to focus
            sem.FixAstigmatismByCTF()

        v = sem.ReportAutoFocus()[0]
        while abs(v - target) > precision:
            sem.AutoFocus()
            v = sem.ReportAutoFocus()[0]

        logging.info(f"Autofocusing: done!")

    def check_before_acquire(self) -> None:
        """ Check dewars and pumps before acquiring. """

        logging.info("Checking dewars and pumps...")

        def _test() -> bool:
            if self.SCOPE_HAS_AUTOFILL:
                return bool(sem.AreDewarsFilling() == 0. and sem.IsPVPRunning() == 0.)
            else:
                return bool(sem.IsPVPRunning() == 0.)

        while True:
            if _test():
                break
            logging.info("Dewars are filling or PVP running, waiting for 30 sec..")
            time.sleep(30)

    def change_aperture(self, name: str = "c2", size: int = 50) -> None:
        """ Change, retract or insert C2 or OBJ apertures.

        :param name: Name, "c2" or "obj"
        :param size: in um, 0 to retract, 1 to reinsert
        """
        aperture = 1 if name.lower() == "c2" else 2

        if self.SCOPE_HAS_APER_CTRL and sem.ReportApertureSize(aperture) != size:
            logging.info(f"Changing {name.upper()} aperture to: {size}")
            sem.SetApertureSize(aperture, size)
        else:
            sem.Pause(f"Please change {name.upper()} aperture to: {size}")
