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
Geosteering interpretation.

Holds picks, blocks, and parameters describing an interpretation along a well.
"""

import math
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List, Optional, Tuple, Union

from dataclasses_json import config
from strenum import StrEnum

from ...datamodels.geosteering.Blocks import Block, Fault, Layer, Throw
from ...datamodels.Helpers import (
    DeprecatedFieldInfo,
    MakeIsodateOptionalField,
    deprecated_field,
    with_field_deprecations,
)
from ..DataModel import DataModel
from ..misc.permission import Editability, Visibility
from .CurveDef import CurveDef
from .Horizon import GeosteerHorizonRole, Horizon, TypewellHorizonDepth
from .Pick import Pick


@dataclass
class Zone:
    """A named interval used to group horizons within an interpretation."""

    top: Horizon
    bottom: Optional[Horizon]


def _warn_on_target_formation(value, _default, _is_init: bool) -> bool:
    return value not in (None, -1, 0)

class AutoExtendMethod(StrEnum):
    """Method used to calculate last data md when extending the last block when new data arrives."""

    LastStation = 'LastStation'
    HoleDepth = 'HoleDepth'

class InclinationType(StrEnum):
    """Method used to automatically extend the dip of the last block when new data arrives"""

    MD = "MD"
    VX = "VX"
    THD = "THD"


@with_field_deprecations
@dataclass
class Interpretation(DataModel):
    """Complete geosteering interpretation including picks, blocks, and options."""

    description: Optional[str] = ''
    starred: bool = False
    target_wellbore_id: int = -1
    target_wellbore_name: Optional[str] = None
    target_wellbore_number: Optional[str] = None
    #: DEPRECATED Prefer using target_horizon_id to identify the target formation
    target_formation_id: int = deprecated_field(
        info=DeprecatedFieldInfo(
            warning="Interpretation.target_formation_id is deprecated; use Interpretation.target_horizon_id instead.",
            warn_if=_warn_on_target_formation,
        ),
        default=-1,
    )
    target_formation_name: Optional[str] = None
    target_formation_member_name: Optional[str] = None
    target_horizon_id: Optional[int] = None
    hang_horizon_id: Optional[int] = None
    target_top_horizon_id: Optional[int] = None
    target_base_horizon_id: Optional[int] = None
    zone_show_above_and_below: Optional[bool] = None
    zone_start_md: Optional[float] = field(default=None, metadata=config(field_name="ZoneStartMD"))
    zone_end_md: Optional[float] = field(default=None, metadata=config(field_name="ZoneEndMD"))
    owner_name: Optional[str] = None
    owner_id: int = -1
    owner_company_name: str = ''
    visibility: Visibility = Visibility.Owner
    editability: Editability = Editability.Locked
    thickness: Optional[float] = None
    #: Method used to calculate last data md when extending the last block when new data arrives
    auto_extend_method: Optional[AutoExtendMethod] = None
    #: Md distance to add to the last data md when extending the last block when new data arrives
    auto_extend_last_block_dist: Optional[float] = None
    #: Method used to automatically extend the dip of the last block when new data arrives
    auto_extend_dip: Optional[InclinationType] = None
    coordinate_system: Optional[str] = None
    picks: list[Pick] = field(default_factory=list[Pick])
    curve_defs: list[CurveDef] = field(default_factory=list[CurveDef])
    horizons: list[Horizon] = field(default_factory=list[Horizon])
    typewell_horizon_depths: Optional[list[TypewellHorizonDepth]] = field(default_factory=list[TypewellHorizonDepth])

    def copy_ids_from(self, source: DataModel):
        super().copy_ids_from(source)
        if isinstance(source, Interpretation):
            DataModel.merge_lists(self.picks, source.picks)
            DataModel.merge_lists(self.curve_defs, source.curve_defs)
            DataModel.merge_lists(self.horizons, source.horizons)

    @property
    def valid(self) -> bool:
        """
        Check if the picks in the interpretation are valid and in order.
        
        :return:
        """
        enough_picks = len(self.picks) > 1
        picks_valid = all(p.valid for p in self.picks)
        picks_md_increases = all(p1.md <= p2.md for p1, p2 in zip(self.picks, self.picks[1:]))
        ok = enough_picks and picks_valid and picks_md_increases
        return ok

    def get_zone(self) -> Optional[Zone]:
        """
        Gets the zone defined by user for this interpretation.

        If none is defined, use the target (hang) formation to find a top of zone where the bottom is
        assumed to be the next horizon down.

        NOTE: the target (hang) formation can be different from the user defined top of zone. So the target_formation
        and the horizon marked with the 'ZoneTop' role could be different.

        :return: Zone comprised of a top and bottom horizon.
        """
        top = next((h for h in self.horizons if h.role == GeosteerHorizonRole.ZoneTop), None)
        bottom = next((h for h in self.horizons if h.role == GeosteerHorizonRole.ZoneBottom), None)

        if top is None:
            top = next((h for h in self.horizons if h.formation_id == self.target_formation_id), None)
            bottom = None

        if bottom is None:
            index = self.horizons.index(top)
            bottom = self.horizons[index + 1] if index + 1 < len(self.horizons) else None

        zone =  Zone(top, bottom)
        return zone


    def make_contiguous_blocks(self) -> List[Block]:
        """
        Computes a "blocks only" set of blocks of this interpretation, where blocks are contiguous in MD (any gaps filled).
        :return: a list of geosteering blocks that are contiguous with no faults
        """
        blocks, faults = self.make_blocks_and_faults()
        just_blocks = [b.make_copy() for b in blocks]  # Make a list of copies of blocks
        contiguous_blocks: List[Block] = []

        for bb1, bb2 in zip(just_blocks, just_blocks[1:]):
            b1: Block = bb1
            b2: Block = bb2
            b1.next_item = b2
            contiguous_blocks.append(b1)
            if b1.md_end < b2.md_start:  # Check for gap and make an infill block if needed
                infill_block = Block.make_infill_block(b1, b2)
                b1.next_item = infill_block
                infill_block.next_item = b2
                contiguous_blocks.append(infill_block)

        last_block = just_blocks[-1]
        last_block.next_item = None
        contiguous_blocks.append(last_block)
        return contiguous_blocks


    def make_blocks_and_faults(
        self,
        interval: Optional[float] = None,
        *,
        keepHz: Optional[Callable[[Horizon], bool]] = None,
    ) -> Tuple[List[Block], List[Fault]]:
        """
        Computes the blocks and faults for this interpretation
        :param interval: If provided, blocks will be of width 'interval' and no faults will be generated.
        :return: a list of geosteering blocks and faults
        """
        # Make a list of layer thicknesses for each employed typewell
        target_horizon_id = self.target_horizon_id

        hz_map = {h.id: h for h in self.horizons}
        def useHz(h_id: int) -> bool:
            hz = hz_map.get(h_id)
            if hz is None:
                return False
            if keepHz is not None:    
                return keepHz(hz) or hz.show
            else:
                return hz.show

        # Create a list of geosteering blocks
        horizons_dict = {h.id: h for h in self.horizons}  # Make a horizon lookup dictionary
        picks = self.picks if interval is None else self.make_evenly_spaced_picks(interval)
        blocks: List[Block] = []
        faults: List[Fault] = []

        target_horizon: Optional[Horizon] = None
        if target_horizon_id is None or target_horizon_id == 0:
            ref_hz_id = 0
            if horizons_dict.get(ref_hz_id) is None:
                hz = Horizon(id=ref_hz_id, name="<Reference>", formation_id=0)
                horizons_dict[ref_hz_id] = hz
                self.horizons.append(hz)
            target_horizon_id = ref_hz_id
        target_horizon = horizons_dict[target_horizon_id]

        last_block_or_fault: Union[Block, Fault, None] = None
        for idx in range(1, len(picks)):
            p1 = picks[idx - 1]
            p2 = picks[idx]
            tgtTvd1 = p1.target_tvd
            tgtTvd2 = p2.target_tvd
            if p1.block_flag or not p1.fault_flag:  # Create block
                block = Block(next_item=None, start_pick=p1, end_pick=p2)
                blocks.append(block)
                if last_block_or_fault is not None:
                    last_block_or_fault.next_item = block
                last_block_or_fault = block
                if tgtTvd1 is None or tgtTvd2 is None:
                    continue
                pickHzs = p1.horizons
                hz_tvds = (
                    [
                        (h_id, tvd) for h_id, tvd in zip(pickHzs.horizon_ids, pickHzs.tvds)
                        if tvd is not None and useHz(h_id)
                    ]
                    if pickHzs is not None
                    else []
                )
                if len(hz_tvds) > 1:
                    type_offset = 0  # hard-wired 0 suggests HorizonDepths.tvds are LWD tvds
                    for i in range(1, len(hz_tvds)):
                        hz_tvd = hz_tvds[i - 1]
                        hz_tvd_bot = hz_tvds[i]
                        tvd = hz_tvd[1]
                        tgtTvd = tvd + type_offset
                        # Compute geometry of the layer for this horizon pair
                        tvd1 = tgtTvd
                        tvd2 = tgtTvd + tgtTvd2 - tgtTvd1
                        thickness = hz_tvd_bot[1] - tvd
                        horizon = horizons_dict[hz_tvd[0]]  # Find horizon for this type well depth
                        horizon_bot = horizons_dict[hz_tvd_bot[0]]
                        layer = Layer(block=block, horz=horizon, bottom_horz=horizon_bot,
                                      tvd_start=tvd1, tvd_end=tvd2,thickness=thickness)
                        block.layers.append(layer)  # Create layer and add to block for this pick
                        if horizon.id == target_horizon_id:
                            block.target_layer = layer
                else:
                    tvd1 = tgtTvd1  # Compute geometry of the layer for top only
                    tvd2 = tgtTvd2
                    thickness = 0
                    horizon = target_horizon  # Use target horizon
                    layer = Layer(block=block, horz=horizon, bottom_horz=horizon,
                                  tvd_start=tvd1, tvd_end=tvd2, thickness=thickness)
                    block.layers.append(layer)  # Create layer and add to block for this pick
                    block.target_layer = layer
            elif p1.fault_flag:  # Create fault
                fault = Fault(next_item=None, pick=p1)
                faults.append(fault)
                if last_block_or_fault is not None:
                    last_block_or_fault.next_item = fault
                last_block_or_fault = fault
                if tgtTvd1 is None or tgtTvd2 is None:
                    continue
                tvd1 = tgtTvd1  # Compute geometry of the layer for top only
                tvd2 = tgtTvd2
                throw_amt = tvd2 - tvd1
                if math.fabs(throw_amt) > 0:
                    horizon = target_horizon  # Use target horizon
                    throw = Throw(fault, horizon, tvd1, tvd2, throw_amt)
                    fault.throws.append(throw)  # Create fault throw and add to block for this pick
                    fault.target_throw = throw

        return blocks, faults

    def make_evenly_spaced_picks(self, interval: float, first_md: Optional[float] = None,
            last_md: Optional[float] = None) -> List[Pick]:
        """
        Converts the actual picks in this interpretation into evenly spaced picks, with no faults.
        :param interval: The sample interval in MD for output picks
        :param first_md: Beginning MD for output picks
        :param last_md: Ending MD for output picks
        :return:
        Note: faults are discarded.
        """
        blocks = self.make_contiguous_blocks()
        first_block = blocks[0]
        last_block = blocks[-1]
        first_md = first_block.md_start if first_md is None else first_md
        last_md = last_block.md_end if last_md is None else last_md
        md = first_md
        current_block = first_block
        evenly_spaced_picks: List[Pick] = []
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            while md < last_md:
                while not current_block.contains_md(md):
                    current_block = current_block.find_next_block()
                    if current_block is None:
                        break
                if current_block is None:
                    break
                try:
                    pick = current_block.make_pick(md)
                except RuntimeWarning as e:
                    print('*** Runtime Error at md = %s: %s' % (md, e))
                    pick = current_block.make_pick(md)   # Redo calc to cause error
                evenly_spaced_picks.append(pick)
                md += interval

        return evenly_spaced_picks



@dataclass
class InterpretationEntry(DataModel):
    """Listing record for an interpretation with minimal fields."""

    description: Optional[str] = ''
    starred: bool = False
    owner_company_name: str = ''
    visibility: Visibility = Visibility.Owner
    editability: Editability = Editability.Locked
    last_modified_by_name: str = ''
    last_modified_date: Optional[datetime] = MakeIsodateOptionalField()

    @property
    def interpretation(self) -> Interpretation:
        return Interpretation(id=self.id, name=self.name, row_version=self.row_version, description=self.description,
                              starred=self.starred)


