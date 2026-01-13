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
"""Compute the mean square error between the model and reference output data."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from numpy import abs as np_abs
from numpy import min as np_min
from numpy import max as np_max
from numpy import mean

from gemseo_calibration.measures.mean_measure import MeanMeasure

if TYPE_CHECKING:
    from gemseo.typing import RealArray

LOGGER = logging.getLogger(__name__)

EPSILON = 1e-12

class MSE(MeanMeasure):
    """The mean square error between the model and reference output data."""

    @staticmethod
    def _compare_data(data: RealArray, other_data: RealArray) -> RealArray:
        return (data - other_data) ** 2

