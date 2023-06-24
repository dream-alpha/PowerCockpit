[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b2bd0d6acd544dde84a051c63af65e85)](https://www.codacy.com/gh/dream-alpha/PowerCockpit/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dream-alpha/PowerCockpit&amp;utm_campaign=Badge_Grade)
[![Gemfury](https://badge.fury.io/fp/gemfury.svg)](https://gemfury.com/f/partner)

# PowerCockpit (POC)
## Features
- POC is a plugin for DreamOS settop boxes
- POC enhances and secures the power-off process of the settop box by:
  - checking if recordings are running or to be started soon
  - checking if tasks like long running file operations are in process
  - enters idle mode to allow those tasks to complete before powering off

## Limitations
- POC supports DreamOS only
- POC is being tested on DM 920 and DM ONE only

## Installation
To install PowerCockpit execute the following command in a console on your dreambox:
- apt-get install wget (only required the first time)
- wget --no-check-certificate https://dream-alpha.github.io/PowerCockpit/powercockpit.sh -O - | /bin/sh

The installation script will also install a feed source that enables a convenient upgrade to the latest version with the following commands or automatically as part of a DreamOS upgrade:
- apt-get update
- apt-get upgrade

## Languages
- english
- german
- italian (by Spaeleus)
- spanish (by Magog)

## Links
- Support: https://github.com/dream-alpha/PowerCockpit/discussions
- Package feed: https://gemfury.com/dream-alpha
