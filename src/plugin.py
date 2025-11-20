# coding=utf-8
# Copyright (C) 2018-2025 by dream-alpha
# License: GNU General Public License v3.0 (see LICENSE file for details)


import Screens.Standby
from .Debug import logger
from .Version import VERSION
from . import Standby
from . import TryQuitMainLoop
from .ConfigInit import ConfigInit


def Plugins(**__):
    logger.info("  +++ Version: %s starts...", VERSION)
    ConfigInit()
    Screens.Standby.Standby = Standby.Standby
    Screens.Standby.TryQuitMainloop = TryQuitMainLoop.TryQuitMainloop
    descriptors = []
    return descriptors
