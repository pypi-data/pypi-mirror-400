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
#
#

"""
Geosteering interpretations service.

List and retrieve geosteering interpretations and entries for a wellbore,
check change status, and fetch full interpretations with configurable pick
adjustments and sampling interval.
"""

from enum import Enum
from typing import Union

from ..datamodels.geosteering.Interpretation import Interpretation, InterpretationEntry
from ..datamodels.wells.Wellbore import Wellbore
from .Client import Client


class PickAdjustEnum(Enum):
    """Pick adjustment when exporting interpretation picks."""
    BlockBoundaries = 0   # Export values at boundaries between interpretation blocks. Default.
    NormalFaults = 1
    MidPoints = 2


class GeosteeringService:
    """Fetch, add and delete geosteering interpretations and entries."""

    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_interpretations(self, wellbore_id: int) -> list[InterpretationEntry]:
        interpsUrl = "geosteer/interpretations/%s" % wellbore_id
        items = self.client.get_list(interpsUrl)
        interps = [InterpretationEntry.from_dict(w) for w in items]
        return interps

    def get_interpretation_entry(self, interp_id: int) -> InterpretationEntry:
        """
        Get an updated entry for a specified geosteering interpretation
        
        :param interp_id: a geosteering interpretation id
        :return: An InterpretationEntry, that includes info on status of a geosteering interp, such as change status.
        """
        url = "geosteer/interpretation/entry/%s" % interp_id
        item = self.client.get(url)
        entry = InterpretationEntry.from_dict(item)
        return entry

    def interpretation_changed(self, interp: Union[Interpretation, InterpretationEntry]) -> bool:
        """
        Check whether a specified geosteering interpretation changed on the server

        :param interp: The geosteering interpretation to check on
        :return: Returns True if the interpretation has changed on the server
        """
        entry = self.get_interpretation_entry(interp.id)
        changed = entry.row_version != interp.row_version
        return changed

    def load_interpretations(self, wellbore: Wellbore) -> list[InterpretationEntry]:
        interps = self.get_interpretations(wellbore.id)
        wellbore.interpretations = interps
        return interps

    def get_interpretation(
        self,
        entry: Union[int, InterpretationEntry],
        pic_adjust: PickAdjustEnum = PickAdjustEnum.BlockBoundaries,
        interval: Union[float, None] = None,
        horizon_output: bool = False,
        *,
        fill_all_pick_type_defs: bool = True,
        convert_intra_block_picks: bool = True,
    ) -> Interpretation:
        """
        Retrieve a full geosteering interpretation.

        Fetches the complete interpretation for a given interpretation entry or ID, allowing control over how picks are
        adjusted (block boundaries, faults, or midpoints), the optional sampling interval, and output options (horizon
        output, filling pick type definitions). An option is provided to convert intra-block picks to start-of-block
        picks for downstream consistency.

        Args:
            entry (Union[int, InterpretationEntry]): Interpretation ID or an interpretation entry instance.
            pic_adjust (PickAdjustEnum, optional): Pick adjustment mode when exporting.
                Defaults to BlockBoundaries.
            interval (float | None, optional): Sampling interval. If None, no re-sampling is done.
            horizon_output (bool, optional): If True, return horizon style output.
                Defaults to False.
            fill_all_pick_type_defs (bool, optional): If True, include all pick type definitions (even if not present).
                Defaults to True.
            convert_intra_block_picks (bool, optional): If True, convert intra-block picks to start-of-block picks.
                Defaults to True.

        Returns:
            Interpretation: Fully populated interpretation including picks and metadata.

        Notes:
            - Picks at negative measured depth (MD) are removed.
            - When conversion is enabled, intra-block picks are flagged as block starts.
        """
        interp_id = entry.id if isinstance(entry, InterpretationEntry) else entry
        interpUrl = "geosteer/interpretation/%s" % interp_id

        query_params = {'pickadjust': str(pic_adjust.value)}
        if interval is not None:
            query_params['interval'] = str(interval)
        query_params['horizonoutput'] = str(horizon_output).lower()  # Convert boolean to string
        query_params['fillAllPickTypeDefs'] = str(fill_all_pick_type_defs).lower()
        query_params["convertIntraBlockPicks"] = str(convert_intra_block_picks).lower()

        item = self.client.get(interpUrl, query_params, True)
        interp = Interpretation.from_dict(item)

        return interp

    def load_interpretation(
        self,
        interp: Interpretation,
        pic_adjust: PickAdjustEnum = PickAdjustEnum.BlockBoundaries,
        interval: Union[float, None] = None,
        horizon_output: bool = False,
        *,
        fill_all_pick_type_defs: bool = True,
        convert_intra_block_picks: bool = True,
    ) -> Interpretation:
        """
        Populate an existing ``Interpretation`` instance with full server data.

        This is a convenience wrapper around ``get_interpretation`` that mutates the
        provided ``interp`` object in-place (copying all dataclass field values from the
        freshly retrieved full interpretation) and then returns the same instance. Use
        this when you already hold a lightweight / stale interpretation object and want
        to refresh it without replacing references elsewhere in your code.

        Args:
            interp (Interpretation): An existing interpretation object to hydrate.
            pic_adjust (PickAdjustEnum, optional): Pick adjustment mode. See
                ``get_interpretation`` for semantics. Defaults to BlockBoundaries.
            interval (float | None, optional): Optional sampling interval. If None no
                re-sampling request is sent.
            horizon_output (bool, optional): If True request horizon style output.
                Defaults to False.
            fill_all_pick_type_defs (bool, optional): If True include all pick type
                definitions, even if unused. Defaults to True.
            convert_intra_block_picks (bool, optional): If True convert intra-block
                picks to start-of-block picks (passed through to ``get_interpretation``).
                Defaults to True.

        Returns:
            Interpretation: The same instance passed in (now fully populated).

        Note:
            All existing attributes on ``interp`` are overwritten with server values.
        """
        full_interp = self.get_interpretation(interp.id, pic_adjust, interval, horizon_output,
            fill_all_pick_type_defs=fill_all_pick_type_defs, convert_intra_block_picks=convert_intra_block_picks
        )
        for field in full_interp.__dataclass_fields__:
            setattr(interp, field, getattr(full_interp, field))
        return interp

    def add_interpretation(self, wellbore_id: int, interp: Interpretation, overwrite: bool = False) -> None:
        # NOTE: we assume that the curve ids in the interp curve defs refer to curves that exist on this wellbore on
        #       the server.
        interp.target_wellbore_id = wellbore_id  # Must match
        url = "geosteer/interpretation/add/%s" % wellbore_id
        query_params = {'overwrite': overwrite, 'rowversion': ''}
        item = self.client.post(url, interp.to_dict(), True, query_params)
        server_interp: Interpretation = Interpretation.from_dict(item)
        interp.copy_ids_from(server_interp)

    def delete_interpretation(self, interp: Union[Interpretation, InterpretationEntry], delete_code: str) -> None:
        url = "geosteer/interpretation/delete/%s" % interp.id
        query_params = {} if interp.row_version is None else {'rowversion': interp.row_version}
        query_params["deletecode"] = delete_code
        self.client.delete(url, query_params)

