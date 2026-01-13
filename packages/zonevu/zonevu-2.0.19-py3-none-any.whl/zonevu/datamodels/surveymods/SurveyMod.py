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

from typing import Optional, Union, List
from dataclasses import dataclass, field
from zonevu.datamodels.DataModel import DataModel
from strenum import StrEnum
from datetime import datetime

from .SurveyModPoint import SurveyModPoint
from ...datamodels.Helpers import MakeIsodateOptionalField

from zonevu.datamodels.surveymods.SurveyModEntry import SurveyModTypeEnum



class HDomain(StrEnum):
    """Horizontal domain of survey mod."""
    MD = 'MD'
    VX = 'VX'

@dataclass
class SurveyMod(DataModel):
    """The raw data for a Target Line or Wellbore Modification object"""
    """Summary record for a survey mod on a wellbore."""
    #: Description of the frac
    description: Optional[str] = None
    #: SurveyMod type (e.g., target line, wellbore mod)
    type: SurveyModTypeEnum = SurveyModTypeEnum.WellboreModification
    creation_date: Optional[datetime] = MakeIsodateOptionalField()
    survey_id: int = -1
    wellbore_id: int = -1
    well_id: int = -1
    vertical_section_azimuth: Optional[float] = None
    domain: Optional[HDomain] = None
    allow_display_in_other_domains: Optional[bool] = False
    start_with_tie_point: Optional[bool] = False
    anchor_survey_station_id: Optional[int] = -1
    show_drilling_window: bool = True
    window_above : Optional[float] = None
    window_below : Optional[float] = None
    window_left  : Optional[float] = None
    window_right : Optional[float] = None
    points: List[SurveyModPoint] = ()
