#  Copyright (c) 2025 Ubiterra Corporation. All rights reserved.
#  #
#  This ZoneVu Python SDK software is the property of Ubiterra Corporation.
#  You shall use it only in accordance with the terms of the ZoneVu Service Agreement.
#  #
#  This software is made available on PyPI for download and use. However, it is NOT open source.
#  Unauthorized copying, modification, or distribution of this software is strictly prohibited.
#  #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#  PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
#  FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#
#
#

"""
Frac job listing entry.

Lightweight summary of a frac job used when listing completions for a
wellbore.
"""

from ..DataModel import DataModel
from dataclasses import dataclass
from typing import Optional
from strenum import StrEnum


class SurveyModTypeEnum(StrEnum):
    """Type of survey mod: wellbore mod, target line, raw survey mod."""
    WellboreModification = "WellboreModification"
    TargetLine = "TargetLine"
    DrilledToPlan = "DrilledToPlan"
    FloatingWaypoints = "FloatingWaypoints"
    WaypointAndGuideline = "WaypointAndGuideline"
    TargetLineUTurnReturn = "TargetLineUTurnReturn"


@dataclass
class SurveyModEntry(DataModel):
    """Summary record for a survey mod on a wellbore."""
    #: Description of the frac
    description: Optional[str] = None
    #: Mod type
    type: SurveyModTypeEnum = SurveyModTypeEnum.WellboreModification
