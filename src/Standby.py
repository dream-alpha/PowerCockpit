from Screens.Screen import Screen
import Screens.Standby
from Components.ActionMap import ActionMap
from Components.config import config
from Components.AVSwitch import AVSwitch
from Components.SystemInfo import SystemInfo
from GlobalActions import globalActionMap
from enigma import eDVBVolumecontrol, eDVBLocalTimeHandler, eServiceReference, eTimer, quitMainloop
from RecordTimer import AFTEREVENT
try:
    from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
except ImportError:
    from .FileManager import FileManager
from .Debug import logger
from .RecordingUtils import isLiveRecording, isLiveRecordingOrRecordingSoon, startTimeshift, stopTimeshift
from .JobUtils import getPendingJobs


class Standby(Screen):
    def Power(self):
        logger.info("leave standby")
        self.avswitch.setInput("ENCODER")
        self.leaveMute()
        self.close(True)

    def setMute(self):
        if eDVBVolumecontrol.getInstance().isMuted():
            self.wasMuted = 1
            print("mute already active")
        else:
            self.wasMuted = 0
            eDVBVolumecontrol.getInstance().volumeToggleMute()

    def leaveMute(self):
        if self.wasMuted == 0:
            eDVBVolumecontrol.getInstance().volumeToggleMute()

    def __init__(self, session, request_shutdown=False):
        logger.info("request_shutdown: %s", request_shutdown)
        self.request_shutdown = request_shutdown
        self.shutdown_timer = eTimer()
        self.shutdown_timer.callback.append(self.doShutdown)
        self.after_event_shutdown = False

        Screen.__init__(self, session)
        self.avswitch = AVSwitch()

        print("enter standby")

        self["actions"] = ActionMap(
            ["StandbyActions"],
            {
                "power": self.Power
            },
            -1
        )

        globalActionMap.setEnabled(False)

        self.setMute()

        self.paused_service = None
        self.prev_running_service = None
        self.time_handler_conn = False

        if self.session.current_dialog:
            if self.session.current_dialog.ALLOW_SUSPEND == Screen.SUSPEND_STOPS:
                self.prev_running_service = self.session.nav.getCurrentlyPlayingServiceReference()
                self.session.nav.stopService()
            elif self.session.current_dialog.ALLOW_SUSPEND == Screen.SUSPEND_PAUSES:
                self.paused_service = self.session.current_dialog
                self.paused_service.pauseService()

        if SystemInfo["ScartSwitch"]:
            self.avswitch.setInput("SCART")
        else:
            self.avswitch.setInput("AUX")
        self.onFirstExecBegin.append(self.__onFirstExecBegin)
        self.onClose.append(self.__onClose)

        if config.misc.standbyCounter.value == 0 and config.misc.useTransponderTime.value:
            th = eDVBLocalTimeHandler.getInstance()
            if not th.ready():
                refstr = config.tv.lastservice.value if config.servicelist.lastmode.value == 'tv' else config.radio.lastservice.value
                ref = eServiceReference(refstr)
                if ref.valid():
                    th.m_timeUpdated.append(self.timeReady)
                    self.session.nav.playService(ref, False, False)

    def timeReady(self):
        if self.time_handler_conn:
            self.time_handler_conn = None
            self.session.nav.stopService()

    def __onClose(self):
        logger.info("...")
        Screens.Standby.inStandby = None
        self.timeReady()
        if not self.session.shutdown:
            if self.prev_running_service:
                self.session.nav.playService(self.prev_running_service)
            elif self.paused_service:
                self.paused_service.unPauseService()
            self.shutdown_timer.stop()
            startTimeshift()
        self.session.screen["Standby"].boolean = False
        globalActionMap.setEnabled(True)

    def __onFirstExecBegin(self):
        logger.info("...")
        Screens.Standby.inStandby = self
        self.session.screen["Standby"].boolean = True
        config.misc.standbyCounter.value += 1
        logger.debug("stopping timeshift")
        stopTimeshift()
        is_recording = isLiveRecordingOrRecordingSoon(self.session)
        logger.debug("is_recording: %s", is_recording)
        if not is_recording and hasattr(config.plugins, "moviecockpit"):
            logger.debug("purging and archiving now...")
            FileManager.getInstance("MVC").purgeTrashcan(
                int(config.plugins.moviecockpit.trashcan_retention.value))
            FileManager.getInstance("MVC").archive()
        self.shutdown_timer.start(1000, True)

    def doShutdown(self):
        logger.info("jobs: %s", len(getPendingJobs()))
        is_recording = isLiveRecordingOrRecordingSoon(self.session)
        jobs = len(getPendingJobs())
        logger.debug("is_recording: %s, jobs: %s", is_recording, jobs)
        if not is_recording and not jobs:
            logger.debug("after_event_shutdown: %s", self.after_event_shutdown)
            if self.request_shutdown or self.after_event_shutdown:
                self.shutdown_timer.stop()
                if config.usage.on_short_powerpress.value == "shutdown":
                    logger.debug("quitMainloop")
                    quitMainloop(1)
        else:
            timer = isLiveRecording()
            if timer:
                logger.debug("afterEvent: %s", timer.afterEvent)
                if timer.afterEvent in [AFTEREVENT.AUTO, AFTEREVENT.DEEPSTANDBY]:
                    logger.debug("afterEvent: %s", timer.afterEvent)
                    self.after_event_shutdown = True
            self.shutdown_timer.start(10000)

    def createSummary(self):
        return StandbySummary


class StandbySummary(Screen):
    skin = """
        <screen position="0,0" size="132,64">
            <widget source="global.CurrentTime" render="Label" position="0,0" size="132,64" font="Regular;40" halign="center">
                <convert type="ClockToText" />
            </widget>
            <widget source="session.RecordState" render="FixedLabel" text=" " position="0,0" size="132,64" zPosition="1" >
                <convert type="ConfigEntryTest">config.usage.blinking_display_clock_during_recording,True,CheckSourceBoolean</convert>
                <convert type="ConditionalShowHide">Blink</convert>
            </widget>
        </screen>"""
