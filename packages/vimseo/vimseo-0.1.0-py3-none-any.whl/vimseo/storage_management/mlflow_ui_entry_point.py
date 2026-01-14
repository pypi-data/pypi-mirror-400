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

from pathlib import Path

from vimseo.config.config_manager import config
from vimseo.storage_management.archive_settings import DEFAULT_ARCHIVE_ROOT


def main() -> None:
    if config.DB_MODE == "Local":
        command = [
            "mlflow",
            "ui",
            "--backend-store-uri",
            f"file:\\\\{Path(config.DB_URI_LOCAL if config.DB_URI_LOCAL != '' else DEFAULT_ARCHIVE_ROOT).absolute().resolve()}",
        ]
        print(f"Run command: {' '.join(command)}")
    else:
        print(f"Browse {config.DB_URI_TEAM} to open database interface.")


if __name__ == "__main__":
    main()
