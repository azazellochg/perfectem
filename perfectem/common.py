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
import datetime as dt
import logging

from .config import SCOPE

SCOPE_HAS_C3 = True


class BaseSetup:
    """ Initialization and common functions. """

    def __init__(self, logFn, **kwargs):
        """ Setup log, set common SerialEM params and camera settings. """

        self.ts = self.timestamp()
        cwd = os.path.dirname(os.path.realpath(__file__))
        self.logDir = os.path.join(cwd, f"{SCOPE}-{self.ts.split('_')[0]}")
        os.makedirs(self.logDir, exist_ok=True)
        os.chdir(self.logDir)
        logging.basicConfig(level=logging.INFO,
                            format='%(message)s',
                            handlers=[
                                logging.FileHandler(f"{logFn}_{self.ts}.log"),
                                logging.StreamHandler()])

        sem.SuppressReports()
        # sem.NoMessageBoxOnError()
        sem.ErrorsToLog()
        sem.SetUserSetting("DriftProtection", 1, 1)

        # Set settings for astig & coma correction to match Record
        sem.SetUserSetting("CtfBinning", 0)
        sem.SetUserSetting("CtfDoFullArray", 0)
        sem.SetUserSetting("CtfDriftSettling", 0.)
        sem.SetUserSetting("CtfExposure", 0)
        sem.SetUserSetting("MinCtfBasedDefocus", -0.4)
        sem.SetUserSetting("ComaIterationThresh", 0.02)
        sem.SetUserSetting("CtfUseFullField", 0)
        sem.SetUserSetting("UsersComaTilt", 5)

        # set common params for linear mode
        self.exp = kwargs.get("exp", 1.0)
        self.binning = kwargs.get("binning", 1)
        self.mag = kwargs.get("mag", 75000)
        self.beam_size = kwargs.get("beam", 1.0)
        self.spot = kwargs.get("spot", 3)

    @classmethod
    def timestamp(cls):
        return dt.datetime.now().strftime("%d%m%y_%H%M")

    @classmethod
    def get_scope_type(cls):
        global SCOPE_HAS_C3
        value1, value2 = sem.ReportPercentC2()
        if (value1 * 0.01 - value2) < 0.00001:  # (percents, fraction) 2-condenser lens system
            SCOPE_HAS_C3 = False
        else:  # (illum. area, fraction)
            SCOPE_HAS_C3 = True

    @classmethod
    def check_eps(cls):
        """ Check max eps after setup beam but before area setup. """
        old_exp, _ = sem.ReportExposure("F")
        old_bin = sem.reportBinning("F")

        cls.setup_area(exp=0.1, binning=1, preset="F")
        sem.Focus()
        _, _, _, _, eps = sem.ElectronStats("A")
        spot = sem.ReportSpotSize()
        while True:
            eps /= 2
            spot += 1
            if eps < 120:  # keep below 120 eps
                break

        if spot != sem.ReportSpotSize() and spot < 12:
            logging.info(f"Increasing spot size to {spot} to reduce dose rate below 120 eps")
            sem.SetSpotSize(spot)

        # Restore previous settings
        sem.setExposure(old_exp)
        sem.setBinning(old_bin)

    @classmethod
    def check_drift(cls, crit=2.0, interval=2, timeout=60):
        """ Wait for drift to go below crit in Angstroms/s.
        :param crit: A/s target rate
        :param interval: repeat every N seconds
        :param timeout: give up and raise error after N seconds
        """
        if (10 * sem.ReportFocusDrift() - crit) > 0.01:
            sem.DriftWaitTask(crit, "A", timeout, interval, 1, "A")

    @classmethod
    def setup_beam(cls, mag, spot, beamsize, mode="nano"):
        """ Set illumination params. """

        sem.SetProbeMode(mode)
        sem.SetMag(mag)
        sem.SetSpotSize(spot)

        if not SCOPE_HAS_C3:
            sem.SetPercentC2(beamsize)
        else:  # (illum. area, fraction)
            sem.SetIlluminatedArea(beamsize * 0.01)

        cls.check_eps()

    @classmethod
    def setup_area(cls, exp, binning, area="F", preset="F"):
        """ Setup camera settings for a certain preset. """

        sem.SetExposure(preset, exp)
        sem.SetBinning(preset, binning)
        sem.SetCameraArea(preset, area)  # full area
        sem.SetProcessing(preset, 2)  # gain-normalized
        try:
            sem.SetK2ReadMode(preset, 0)  # linear mode
        except:
            pass

    @classmethod
    def euc_by_beamtilt(cls):
        old_mag, _, _ = sem.ReportMag()
        old_spot = sem.ReportSpotSize()
        old_beam = sem.ReportIlluminatedArea()
        cls.setup_beam(mag=6500, spot=3, beamsize=11)
        cls.setup_area(exp=0.5, binning=2, preset="F")

        sem.SaveFocus()
        old_offset = sem.ReportAutofocusOffset()
        sem.SetEucentricFocus()
        sem.SetAutofocusOffset(-30)
        sem.AutoFocus(-1)
        res = sem.ReportAutofocus()[0]

        while abs(res + 30) >= 0.7:
            sem.MoveStage(0, 0, -1 * (res + 30))
            print(f"Z changed by {-1 * (res + 30):0.2f} um")
            sem.AutoFocus(-1)
            res = sem.ReportAutofocus()[0]

        sem.RestoreFocus()
        sem.SetAutofocusOffset(old_offset)
        sem.SetMag(old_mag)
        sem.SetSpotSize(old_spot)
        sem.SetIlluminatedArea(old_beam)

    @classmethod
    def autofocus(cls, target, precision=0.05, do_ast=True, do_coma=False):
        """ Autofocus until the result is within precision (um) from a target. """

        if do_ast:
            sem.SetAutofocusOffset(0)
            sem.SetTargetDefocus(-1)
            sem.AutoFocus()

            try:
                logging.info("Correcting astigmatism...")
                sem.FixAstigmatismByCTF()
                if do_coma:
                    logging.info("Correcting coma...")
                    sem.FixComaByCTF()
            except Exception as e:
                logging.error(e)
                sem.Exit()

        sem.SetTargetDefocus(target)
        sem.SetAutofocusOffset(target / 2)
        sem.AutoFocus()
        v = sem.ReportAutoFocus()[0]
        while abs(v - target) > precision:
            sem.AutoFocus()
            v = sem.ReportAutoFocus()[0]

    @classmethod
    def check_before_acquire(cls):
        """ Check dewars and pumps before acquiring. """
        for i in range(10):
            if sem.AreDewarsFilling() == 0. and sem.IsPVPRunning() == 0.:
                break
            else:
                logging.info("Dewars are filling or PVP running, waiting for 60 sec..")
                sem.Delay(60)
                i += 1
