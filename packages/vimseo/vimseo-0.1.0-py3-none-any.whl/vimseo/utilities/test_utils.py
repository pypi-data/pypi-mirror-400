# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Copyright (c) 2019 IRT-AESE.
# All rights reserved.
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: XXXXXXXXXXX
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
from __future__ import annotations

import logging
import sys

from vimseo.api import set_config
from vimseo.config.config_manager import config

LOGGER = logging.getLogger(__name__)


def get_working_mock_command():
    """A command that works on Windows or Linux."""
    if sys.platform.startswith("win"):
        return "powershell Start-Sleep -m 50"
    return "sleep 0.05"


class WrapperMockCommands:
    """A context to mock wrapper command lines by dummy commands that return no error on
    Windows and Linux."""

    def __init__(self):
        self.__original_commands = {}

    def __enter__(self):
        self.__original_commands["CMD_ABAQUS_CAE"] = config.CMD_ABAQUS_CAE
        self.__original_commands["CMD_ABAQUS_CAE_POST"] = config.CMD_ABAQUS_CAE_POST
        self.__original_commands["CMD_ABAQUS_RUN"] = config.CMD_ABAQUS_RUN

        LOGGER.info("Replacing wrapper commands by dummy working command.")
        dummy_cmd = get_working_mock_command()

        set_config("CMD_ABAQUS_CAE", dummy_cmd)
        set_config("CMD_ABAQUS_CAE_POST", dummy_cmd)
        set_config("CMD_ABAQUS_RUN", dummy_cmd)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        LOGGER.info("Replacing back dummy commands by the original commands.")
        for key, value in self.__original_commands.items():
            set_config(key, value)


class SetConfig:
    def __init__(self, field_name, new_value):
        self.field_name = field_name
        self.new_value = new_value
        self._original_value = None

    def __enter__(self):
        self._original_value = config.get_config_as_dict()[self.field_name]
        set_config(self.field_name, self.new_value)
        LOGGER.info(
            f"Replacing config field {self.field_name} with value {self._original_value} "
            f"by {self.new_value}."
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        LOGGER.info(
            f"Replacing back config value to {self.field_name}={self._original_value}."
        )
        set_config(self.field_name, self._original_value)
