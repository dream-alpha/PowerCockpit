from enigma import quitMainloop
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
import Screens.Standby
from Components.config import config
from Tools import Notifications
from .__init__ import _
from .Standby import Standby
from .RecordingUtils import isLiveRecordingOrRecordingSoon, stopTimeshift
from .JobUtils import getPendingJobs
from .Debug import logger


class TryQuitMainloop(MessageBox):
    def __init__(self, session, retvalue=1, timeout=-1, default_yes=True):
        logger.info("retvalue: %s, timeout: %s", retvalue, timeout)
        self.retval = retvalue
        reason = ""
        recordings = isLiveRecordingOrRecordingSoon(session)
        if recordings:
            reason += _("Recording(s) are in progress or coming up in few seconds!") + '\n'
        jobs = len(getPendingJobs())
        if jobs:
            reason += _("Job(s) are in progress!") + "\n"
        if retvalue == 1 and not recordings and hasattr(config.plugins, "moviecockpit"):
            if config.plugins.moviecockpit.archive_enable.value:
                reason += _("Archiving will be done!") + "\n"
            if config.plugins.moviecockpit.trashcan_clean.value:
                reason += _("Purging trashcan will be done!") + "\n"
        self.enter_standby = retvalue == 1 and reason != ""
        reason = "" if self.enter_standby and not config.plugins.powercockpit.show_idle_msg.value else reason
        if retvalue == 16:
            reason = _("Really reboot into Recovery Mode?\n")
        logger.debug("reason: %s", reason)
        if reason:
            if retvalue == 1:
                MessageBox.__init__(self, session, reason + _(
                    "Entering idle mode to complete recording(s)/job(s) before powering off."), type=MessageBox.TYPE_INFO, timeout=10)
            elif retvalue == 2:
                MessageBox.__init__(self, session, reason + _("Really reboot now?"),
                                    type=MessageBox.TYPE_YESNO, timeout=timeout, default=default_yes)
            elif retvalue == 4:
                pass
            elif retvalue == 16:
                MessageBox.__init__(self, session, reason + _("You won't be able to leave Recovery Mode without physical access to the device!"),
                                    type=MessageBox.TYPE_YESNO, timeout=timeout, default=default_yes)
            else:
                MessageBox.__init__(self, session, reason + _("Really restart now?"),
                                    type=MessageBox.TYPE_YESNO, timeout=timeout, default=default_yes)
            self.skinName = "MessageBox"
            self.onShow.append(self.__onShow)
            self.onHide.append(self.__onHide)
        else:
            self.skin = """<screen name="TryQuitMainloop" position="0,0" size="0,0" flags="wfNoBorder"/>"""
            Screen.__init__(self, session)
            self.close(True)

    def close(self, value):
        logger.info("value: %s, enter_standby: %s", value, self.enter_standby)
        if value:
            if self.enter_standby:
                Notifications.AddNotification(Standby, True)
                Screen.close(self, False)
            else:
                logger.debug("stopping timeshift")
                stopTimeshift()
                logger.debug("shutting down now...")
                quitMainloop(self.retval)
        else:
            MessageBox.close(self, True)

    def __onShow(self):
        logger.info("...")
        Screens.Standby.inTryQuitMainloop = True

    def __onHide(self):
        logger.info("...")
        Screens.Standby.inTryQuitMainloop = False
