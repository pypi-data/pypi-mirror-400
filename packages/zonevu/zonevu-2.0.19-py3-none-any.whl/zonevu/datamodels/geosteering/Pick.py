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
Geosteering pick.

Represents a point along the well path with target TVD.
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import config

from ..DataModel import DataModel
from .HorizonDepths import HorizonDepths


@dataclass
class Pick(DataModel):
    """
    Geosteering pick at a measured depth with target TVD/TVT and coordinates.
    
    .. _pick-type:
    
    Pick Type
    =========

    The pick type is determined by the combination of block_flag and fault_flag:
    
    - block_flag=True, fault_flag=False: Block boundary pick - represents the end of one block and start of another
    - block_flag=True, fault_flag=True: Hidden block pick - represents the end of a block and start of a hidden block
    - block_flag=False, fault_flag=True: Fault pick - represents the other side of a fault, should be preceded by 
      a pick at the same MD so the throw can be calculated from the difference in target_tvd
    - block_flag=False, fault_flag=False: Sub-block pick - can be treated as a regular block pick
    """
    #: TVD for this md on wellbore
    tvd: Optional[float] = field(default=None, metadata=config(field_name="TVD"))
    #: MD (Measured Depth) of this along wellbore
    md: float = field(default=0, metadata=config(field_name="MD"))
    #: Vx (Vs) x-coordinate for this pick along wellbore projected into a plane for the current display azimuth
    vx: Optional[float] = field(default=None, metadata=config(field_name="VX"))
    #: TVT (True Vertical Thickness) of pick from target TVD
    target_tvt: Optional[float] = field(default=None, metadata=config(field_name="TargetTVT"))
    #: TVD (True Vertical Depth) of pick in wellbore depth coordinates
    target_tvd: Optional[float] = field(default=None, metadata=config(field_name="TargetTVD"))
    #: Absolute elevation of pick
    target_elevation: Optional[float] = field(default=None, metadata=config(field_name="TargetElevation"))
    #: Latitude of pick in WGS84 Datum
    latitude: Optional[float] = None
    #: Longitude of pick in WGS84 Datum
    longitude: Optional[float] = None
    #: X-coordinate of pick in projected x,y coordinates of project well is in
    x: Optional[float] = None
    #: Y-coordinate of pick in projected x,y coordinates of project well is in
    y: Optional[float] = None
    #: X-offset of pick relative to well surface location
    dx: Optional[float] = field(default=None, metadata=config(field_name="DX"))
    #: Y-offset of pick relative to well surface location
    dy: Optional[float] = field(default=None, metadata=config(field_name="DY"))
    #: Elevation for this md on wellbore
    elevation: Optional[float] = None
    #: Helps classify this pick. See :ref:`pick-type` for details
    block_flag: bool = False
    #: Helps classify this pick. See :ref:`pick-type` for details
    fault_flag: bool = False
    #: The system id of the type wellbore
    type_wellbore_id: int = -1
    #: The system id of the type well log curve def
    type_curve_def_id: Optional[int] = None

    curve_values: Optional[List[Optional[float]]] = field(default=None, metadata=config(field_name="CurveValues"))
    horizons: Optional[HorizonDepths] = field(default=None, metadata=config(field_name="Horizons"))

    @property
    def valid(self) -> bool:
        """
        Validity check on this pick.
        
        :return: True if all required numeric fields are defined and finite
        """
        md_ok = self.md is not None and math.isfinite(self.md)
        tvd_ok = self.target_tvd is not None and math.isfinite(self.target_tvd)
        tvt_ok = self.target_tvt is not None and math.isfinite(self.target_tvt)
        x_ok = self.x is not None and math.isfinite(self.x)
        y_ok = self.y is not None and math.isfinite(self.y)
        lat_ok = self.latitude is not None and math.isfinite(self.latitude)
        lon_ok = self.longitude is not None and math.isfinite(self.longitude)
        elev_ok = self.target_elevation is not None and math.isfinite(self.target_elevation)
        ok = md_ok and tvd_ok and tvt_ok and x_ok and y_ok and lat_ok and lon_ok and elev_ok
        return ok

    def is_block(self) -> bool:
        """
        Determine if this is a block boundary pick.
        
        A block boundary pick represents the end of one block and start of another
        """
        return self.block_flag and not self.fault_flag

    def is_fault(self) -> bool:
        """
        Determine if this is a fault pick.

        A fault pick represents the other side of a fault, should be preceded by
          a pick at the same MD so the throw can be calculated from the difference in target_tvd        
        """
        return self.fault_flag and not self.block_flag

    def hidden(self) -> bool:
        """
        Determine if this is a hidden block pick.

        A hidden block pick represents the end of a block and start of a hidden block
        """
        return self.block_flag and self.fault_flag

    def is_sub(self) -> bool:
        """
        Determine if this is a sub-block pick.

        A sub-block pick can be treated as a regular block pick, or as a pick inside a block
        """
        return not self.fault_flag and not self.block_flag
