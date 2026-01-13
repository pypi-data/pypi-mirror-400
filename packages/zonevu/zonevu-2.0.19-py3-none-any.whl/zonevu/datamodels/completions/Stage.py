#  Copyright (c) 2024 Ubiterra Corporation. All rights reserved.
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
Frac stage details.

Represents a single stage within a frac job, including timing and parameters.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ...datamodels.completions.DepthFeature import DepthFeature
from ...datamodels.completions.Plug import Plug
from ...datamodels.Helpers import (
    DeprecatedFieldInfo,
    MakeIsodateOptionalField,
    deprecated_field,
    with_field_deprecations,
)
from ..DataModel import DataModel
from .UserDefinedStageValue import UserDefinedStageValue


def _warn_on_stage_user_param_values(value, _default, is_init: bool) -> bool:
    if is_init:
        return bool(value)
    return True


@with_field_deprecations
@dataclass
class Stage(DataModel):
    """Single frac stage with timing, features (perfs/plugs), and notes."""
    # Represents a ZoneVu frac stage data object on a wellbore
    sequence_num: int = 0
    key: Optional[str] = ''
    gap: bool = False
    note: Optional[str] = ''

    num_clusters: Optional[int] = None
    toe_plug: Optional[Plug] = None
    toe_md: float = 0
    heel_md: float = 0
    tvd_depth: Optional[float] = None

    #: DEPRECATED Use user_defined_stage_values for user-supplied metadata.
    user_param_values: List[Optional[float]] = deprecated_field(
        info=DeprecatedFieldInfo(
            warning="Stage.user_param_values is deprecated; use Stage.user_defined_stage_values for user metadata.",
            warn_if=_warn_on_stage_user_param_values,
        ),
        default_factory=list[Optional[float]],
    )
    user_defined_stage_values: Optional[List[UserDefinedStageValue]] = None
    depth_features: List[DepthFeature] = field(default_factory=list[DepthFeature])

    proppant_weight: Optional[float] = None
    water_volume: Optional[float] = None
    slurry_rate: Optional[float] = None

    pressure: Optional[float] = None
    duration: Optional[float] = None
    start_date: Optional[datetime] = MakeIsodateOptionalField()
    bottom_pressure: Optional[float] = None
    breakdown_pressure: Optional[float] = None
    closure_pressure: Optional[float] = None
    avg_surface_pressure: Optional[float] = None
    max_surface_pressure: Optional[float] = None
    max_bottom_pressure: Optional[float] = None
    isip_pressure: Optional[float] = None
    closure_gradient: Optional[float] = None
    frac_gradient: Optional[float] = None
    slurry_volume: Optional[float] = None

    avg_proppant_conc: Optional[float] = None
    max_proppant_conc: Optional[float] = None
    acid: Optional[float] = None
    FR_fluid: Optional[float] = None
    FR_powder: Optional[float] = None
    biocide: Optional[float] = None
    clay_stabilizer: Optional[float] = None
    scale_inhibitor: Optional[float] = None
    water_salinity: Optional[float] = None
    time_to_max_injection_rate: Optional[float] = None
    plug_type: Optional[str] = None

    screened_out: bool = False
    frac_hit: bool = False

    frac_quality: Optional[float] = None
    frac_length_up: Optional[float] = None
    frac_length_down: Optional[float] = None
    frac_length_left: Optional[float] = None
    frac_length_right: Optional[float] = None
    frac_wing_angle: Optional[float] = None


    def copy_ids_from(self, source: DataModel):
        super().copy_ids_from(source)
        if isinstance(source, Stage):
            if source.toe_plug is not None and self.toe_plug is not None:
                self.toe_plug.copy_ids_from(source.toe_plug)
            DataModel.merge_lists(self.depth_features, source.depth_features)
