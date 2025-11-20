# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


from Components.config import config, ConfigYesNo, ConfigSubsection, ConfigSelection
from .Debug import log_levels, logger, initLogging


class ConfigInit():
    def __init__(self):
        logger.info("...")
        config.plugins.powercockpit = ConfigSubsection()
        config.plugins.powercockpit.show_idle_msg = ConfigYesNo(default=True)
        config.plugins.powercockpit.debug_log_level = ConfigSelection(
            default="INFO", choices=list(log_levels.keys()))
        initLogging()
