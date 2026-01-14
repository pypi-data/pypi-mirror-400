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

import json
import logging
from os import path
from pathlib import Path

import setuptools  # noqa: F401
from numpy.distutils.core import Extension
from numpy.distutils.core import setup

LOGGER = logging.getLogger(__name__)

LIB_SUFFIX = "_lib"
PATH_TO_LIB = Path("..") / "vims" / "lib_vims"
SUBROUTINE_PATH_FILE = PATH_TO_LIB / "subroutines.json"


def __get_subroutines(json_file: Path):
    return json.load(Path(json_file).open())


subroutines = __get_subroutines(SUBROUTINE_PATH_FILE)
LOGGER.info(f"Subroutines are {subroutines}")
extensions = [
    Extension(
        f"{path.splitext(Path(filename).name)[0]}{LIB_SUFFIX}",
        [str(PATH_TO_LIB / filename)],
    )
    for filename in subroutines
]
setup(ext_modules=extensions)
