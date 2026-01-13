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
Well catalogue and operations service.

Provides search and retrieval of wells and related data (logs, tops,
surveys, geosteering, completions, notes). Exposes helpers to find wells by
name, ID, UWI, and by proximity, and to load aggregated well data.
"""

import copy
import time
import urllib.parse
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .SurveyModsService import SurveyModsService
from ..datamodels.Company import Division
from ..datamodels.geospatial.GeoLocation import GeoLocation
from ..datamodels.geosteering.Interpretation import Interpretation
from ..datamodels.misc.permission import Editability
from ..datamodels.Project import ProjectEntry
from ..datamodels.strat.StratColumn import StratColumn
from ..datamodels.wells.Well import Well, WellEntry
from ..datamodels.wells.Welllog import WellLogTypeEnum
from .Client import Client, ZonevuError
from .CompanyService import CompanyService
from .CompletionsService import CompletionsService
from .GeosteeringService import GeosteeringService
from .NoteService import NoteService
from .ProjectService import ProjectService
from .SurveyService import SurveyService
from .WellData import WellData, WellDataOptions
from .WelllogService import WelllogService
from .WelltopService import WelltopService


class WellService:
    """Search/find wells and load related data (logs, tops, surveys, fracs)."""

    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_wells(self,
                  name: Optional[str] = None,
                  project: Optional[Union[ProjectEntry, int, str]] = None,
                  division: Optional[Union[Division, int, str]] = None
                  ) -> List[WellEntry]:
        """
        Get list of well catalog entries.

        :param name: Optional well name to match. Can be partial.
        :param project: If provided, get all wells in the given project identifier (project name, system id, or Project catalog entry)
        :param division:  Optional division identifier (division object or system id or division name)
        :return:  A list of well catalog entries that match. These are not full well objects.

        NOTE: if no search parameters provided, all wells in this zonevu account returned.
        """
        if project is None:
            return self.find_by_name(match_token = name, exact_match=False, division=division)
        else:
            return self.find_by_project(project)

    def get(self, well_identifier: Union[WellEntry, int, str], well_data: Optional[Set[WellData]] = None) -> Optional[Well]:
        """
        Get a well based on a well catalog entry, a well name, or a well system id.

        :param well_identifier: either a well id, a well catalog entry, or a well name
        :param well_data:  optional directives to load the well with tops, surveys, or other well child data.
        :return: a well object

        NOTE:  use the well object 'primary_wellbore' property to access most of the well child data, including tops, surveys, etc.
        """
        well: Optional[Well] = None
        if isinstance(well_identifier, WellEntry):
            well = self.find_by_id(well_identifier.id)
        elif isinstance(well_identifier, int):
            well =  self.find_by_id(well_identifier)
        elif isinstance(well_identifier, str):
            well =  self.get_first_named(well_identifier)
        else:
            return None

        if well is None:
            return None

        if well_data is not None:
            self.load_well(well, well_data)
        return well

    def exists(self, identifier: Union[str, int]) -> bool:
        if isinstance(identifier, int):
            well = self.find_by_id(identifier)
            return well is not None
        elif isinstance(identifier, str):
            wells = self.find_by_name(identifier)
            exists = len(wells) > 0
            return exists

    def find_by_name(self, match_token: Optional[str] = None, exact_match: Optional[bool] = True, division: Optional[Union[Division, int, str]] = None,
                     page: Optional[int] = 0) -> List[WellEntry]:
        """
        Find listing entries a well or wells whose names match a name or that start with a name fragment

        :param match_token: name or name fragment to use to search for wells. If not provided, gets all wells.
        :param exact_match: whether to exactly match the well name.
        :param division: division (business unit) to search in. If None, searches all divisions user is authorized for
        :param page: page number that is used by this method to retrieve all wells since the limit is 500 per call (optional).
        :return: A list of well entries (summary data structures) that match. These are not full well objects.

        NOTE: usually you ignore the page parameter.
        """
        url = "wells"
        max_pages = 50     # This means that it won't do more than 50 round trips to retrieve search result pages.
        params = {"exactmatch": str(exact_match)}

        if division is not None:
            division_id = -1
            if isinstance(division, str):
                divisions = CompanyService(self.client).get_divisions()
                division_obj = next((d for d in divisions if d.name.lower() == division.lower()), None)
                if division_obj is None:
                    raise Exception(f'no such division "{division}"')
                division_id = division_obj.id
            elif isinstance(division, Division):
                division_id = division.id
            elif isinstance(division, int):
                division_id = division
            else:
                raise Exception(f'illegal division type encountered')
            params["divisionid"] = division_id

        all_entries: list[WellEntry] = []
        more = True
        if match_token is not None:
            params["name"] = urllib.parse.quote_plus(match_token)

        counter = 0
        while more:
            params["page"] = str(page)
            wells_response = self.client.get_dict(url, params, False)
            items = wells_response['Wells']
            more = wells_response['More']
            page = wells_response['Page']
            entries = [WellEntry.from_dict(w) for w in items]
            all_entries.extend(entries)
            counter += 1
            if counter > max_pages:
                break               # Safety check. Limits us to 500 iterations, which is 250,000 wells.
            time.sleep(0.050)       # Pause for 50 ms so as not to run into trouble with webapi throttling.

        return all_entries

    def find_by_project(self, project_identifier: Optional[Union[ProjectEntry, int, str]]) -> List[WellEntry]:
        project_svc = ProjectService(self.client)
        project = project_svc.get(project_identifier)
        if project is None:
            return []
        else:
            return project.wells


    def find_by_location(self, location: GeoLocation, distance: float) -> List[WellEntry]:
        uwi = "wells/nearby"
        params = {"latitude": location.latitude, "longitude": location.longitude, "radius": distance}
        try:
            items = self.client.get_list(uwi, params, False)
            entries = [WellEntry.from_dict(w) for w in items]
            return entries
        except ZonevuError as err:
            if err.status_code == 404:
                return []
            raise err

    def find_by_id(self, well_id: int) -> Well:
        url = "well/id/%s" % well_id
        item = self.client.get(url, {}, True)
        well = Well.from_dict(item)
        return well

    def find_by_uwi(self, uwi: str) -> Optional[Well]:
        url = "well/uwi"
        params = {"uwi": urllib.parse.quote_plus(uwi)}
        try:
            item = self.client.get(url, params, False)
            well = Well.from_dict(item)
            return well
        except ZonevuError as err:
            if err.status_code == 404:
                return None
            raise err

    def find_wells_original_uwi(self, uwi: str) -> List[WellEntry]:
        # Get wells by original UWI.
        url = "wells/originaluwi"
        params = {'uwi': uwi}
        items = self.client.get_list(url, params, False)
        entries = [WellEntry.from_dict(w) for w in items]
        return entries

    def find_similar(self, name: str, location: GeoLocation, tolerance: float = 0.9, distance: float = 2) -> List[WellEntry]:
        """
        Finds wells in ZoneVu near a location with nearly or exactly the same name.

        :param name: the name to attempt to match to the full (well name + well number) well name
        :param location: the geolocation to search nearby for wells
        :param tolerance: the text similarity threshold [0, 1], where 1 is an exact match and zero is no match.
        :param distance: the radius in meters around 'location' to search.
        :return:
        """
        nearby_wells = self.find_by_location(location, distance)  # Find all wells within N meters.
        raw_output: List[Tuple[float, WellEntry]] = []
        for well in nearby_wells:
            similarity = SequenceMatcher(None, name, well.full_name).ratio()
            raw_output.append((similarity, well))
        output = [item for item in raw_output if item[0] > tolerance]
        output = sorted(output, key=lambda item: item[0], reverse=True)
        return [item[1] for item in output]

    def get_first_named(self, well_name: str, exact_match: bool = True) -> Optional[Well]:
        """
        Find the first well with the given name and return the full well object.

        :param str well_name: Exact well name including well number (if any).
        :param bool exact_match: If True, search by exact full-name match; if False, allow partial match.
        :return: The full well object if found, else None.
        """
        well_entries = self.find_by_name(well_name, exact_match)  # Find well listing entry by name doing an exact match
        if len(well_entries) == 0:
            return None
        well = self.find_by_id(well_entries[0].id)  # Get the full well object from ZoneVu
        return well

    def load_well(
        self,
        well: Well,
        well_data: Optional[Set[WellData]] = None,
        *,
        show_progress: bool = False,
        fill_all_pick_type_defs: bool = True,
        convert_intra_block_picks: bool = True,
    ) -> None:
        """
        Load well child data (logs, tops, surveys, fracs, geosteering, notes) into a well object.

        :param well: The well to load data into. Must have a valid id.
        :param well_data: A set of WellData enum values indicating which child data to load.
        :param show_progress: If True, print progress messages to console.
        :param fill_all_pick_type_defs: If True, when loading geosteering interpretations, load all pick type definitions. If False, only load pick type definitions that have picks in the interpretation.
        :param convert_intra_block_picks: If True, when loading geosteering interpretations, convert intra-block picks to start-of-block picks.
        """
        options = WellDataOptions(well_data)
        loaded_well = self.find_by_id(well.id)
        well.merge_from(loaded_well)
        primary_wb = well.primary_wellbore
        if primary_wb is None:
            return

        if options.welllogs:
            if show_progress:
                print("Loading well logs...")
            try:
                log_svc = WelllogService(self.client)
                log_svc.load_welllogs(primary_wb, options.curves)
            except Exception as err:
                print('Could not load well logs because %s' % err)
            if show_progress:
                num_logs = len(primary_wb.welllogs) if primary_wb.welllogs is not None else 0
                print(f"   Num logs = {num_logs}")

        if options.surveys:
            if show_progress:
                print("Loading surveys...")
            try:
                survey_svc = SurveyService(self.client)
                survey_svc.load_surveys(primary_wb)
            except Exception as err:
                print('Could not load well surveys because %s' % err)
            if show_progress:
                num_surveys = len(primary_wb.surveys) if primary_wb.surveys is not None else 0
                print(f"   Num surveys = {num_surveys}")

        if options.tops:
            if show_progress:
                print("Loading well tops...")
            try:
                top_svc = WelltopService(self.client)
                top_svc.load_welltops(primary_wb)
            except Exception as err:
                print('Could not load well tops because %s' % err)
            if show_progress:
                num_tops = len(primary_wb.tops) if primary_wb.tops is not None else 0
                print(f"   Num tops = {num_tops}")

        if options.fracs:
            if show_progress:
                print("Loading fracs...")
            try:
                frac_svc = CompletionsService(self.client)
                frac_svc.load_fracs(primary_wb)
            except Exception as err:
                print('Could not load fracs because %s' % err)
            if show_progress:
                num_fracs = len(primary_wb.fracs) if primary_wb.fracs is not None else 0
                print(f"   Num fracs = {num_fracs}")

        if options.geosteering:
            if show_progress:
                print("Loading geosteering interpretations...")
            try:
                primary_wb.interpretations.clear()
                geosteer_svc = GeosteeringService(self.client)
                geosteering_entries = geosteer_svc.get_interpretations(primary_wb.id)
                for interp_entry in geosteering_entries:
                    try:
                        interp = geosteer_svc.get_interpretation(interp_entry.id,
                                                                 fill_all_pick_type_defs=fill_all_pick_type_defs,
                                                                 convert_intra_block_picks=convert_intra_block_picks)
                        primary_wb.interpretations.append(interp)
                    except Exception as interp_err:
                        print(f'Could not retrieve wellbore "{primary_wb.name}" geosteering interpretation with id {interp_entry.id}: {interp_err}')
            except Exception as err:
                print(f'Could not load wellbore "{primary_wb.name}" geosteering interpretations: {err}')
            if show_progress:
                num_interps = len(primary_wb.interpretations) if primary_wb.interpretations is not None else 0
                print(f"   Num interpretations = {num_interps}")

        if options.notes:
            if show_progress:
                print("Loading well user notes...")
            try:
                notes_svc = NoteService(self.client)
                notes_svc.load_notes(primary_wb)
            except Exception as err:
                print('Could not load well user notes because %s' % err)
            if show_progress:
                num_notes = len(primary_wb.notes) if primary_wb.notes is not None else 0
                print(f"   Num notes = {num_notes}")

        if options.surveymods:
            if show_progress:
                print("Loading well target lines and wellbore mods...")
            try:
                smods_svc = SurveyModsService(self.client)
                smods_svc.load_mods(primary_wb)
            except Exception as err:
                print('Could not load well target lines and wellbore mods because %s' % err)
            if show_progress:
                num_mods = len(primary_wb.surveymods) if primary_wb.surveymods is not None else 0
                print(f"   Num target lines and wellbore mods = {num_mods}")

    def get_stratcolumn(self, well: Union[Well, WellEntry, int]) -> StratColumn | None:
        """
        Get the selected strat column for the well
        """
        well_id = well if isinstance(well, int) else well.id
        url = "well/stratcolumn/%s" % well_id
        item = self.client.get(url)
        col = StratColumn.from_dict(item)
        return col

    def get_stratcolumns(self, well: Union[Well, WellEntry, int]) -> list[StratColumn]:
        """
        Get all strat columns for the well
        """
        well_id = well if isinstance(well, int) else well.id
        url = "well/stratcolumns/%s" % well_id
        items = self.client.get_list(url)
        cols = [StratColumn.from_dict(w) for w in items]
        return cols

    def create_well(self, well: Well, well_data: Optional[Set[WellData]], *, project_id: Optional[int] = None) -> None:
        """
        Create a well and its child data on the server

        :param well:  Well to create in ZoneVu account
        :param well_data:  Which child data on the well to also create on the newly created well.
        :param project_id: Optional project id. If set the created well will be associated with this project, and will be created in the company that owns the project.

        Note: passed in well will be altered.
        """
        options = WellDataOptions(well_data)

        # First, create the well itself.
        wellUrl = "well/create"
        trimmed_well = well.make_trimmed_copy()
        query_params: Dict[str, Any] | None = None
        if project_id is not None:
            query_params= {"projectId": project_id}
        item = self.client.post(wellUrl, trimmed_well.to_dict(), query_params=query_params)
        created_well = Well.from_dict(item)
        # Update ids on well and wellbores to new ids in ZoneVu
        well.id = created_well.id
        for wb, wb_copy in zip(well.wellbores, created_well.wellbores):
            wb.id = wb_copy.id

        # Exit if well has no wellbores.
        if well.primary_wellbore is None:
            return

        # Create all child data for the primary wellbore.
        wellbore = well.primary_wellbore

        # Surveys
        survey_lut: Dict[int, int] = dict()  # Need LUT for surveys to re-reference from tops that refer to them.
        if options.surveys:
            survey_svc = SurveyService(self.client)
            for survey in wellbore.surveys:
                src_id = survey.id
                survey_svc.add_survey(wellbore, survey)  # Note: updates survey ids on 'wellbore'
                survey_lut[src_id] = survey.id

        # Well tops
        if options.tops:
            top_svc = WelltopService(self.client)
            for top in wellbore.tops:
                if top.survey_id in survey_lut:
                    top.survey_id = survey_lut[top.survey_id]  # Re-reference top survey to new survey on wellbore
            top_svc.add_tops(wellbore, wellbore.tops)

        # Well logs
        if options.welllogs:
            log_svc = WelllogService(self.client)
            curve_lut: Dict[int, int] = dict()
            for log in wellbore.welllogs:
                old_curve_ids = [c.id for c in log.curves]
                for curve in log.curves:
                    curve_lut[curve.id] = curve.id
                log_svc.add_welllog(wellbore, log)
                for old_id, new_id in zip(old_curve_ids, [c.id for c in log.curves]):
                    curve_lut[old_id] = new_id

            # Now add curve groups, as they can reference curves from multiple logs
            for log in wellbore.welllogs:
                for group in log.curve_groups:
                    group.curve_ids = [curve_lut[curve_id] for curve_id in group.curve_ids]
                    for params in group.curve_channel_params:
                        curve_id = params.curve_id
                        if curve_id in curve_lut:
                            params.curve_id = curve_lut[curve_id]
                        else:
                            raise ZonevuError.local('cannot create curve group on log without providing curves')
                    log_svc.add_curve_group(log.id, group)

        # Well log curve samples
        if options.curves:
            log_svc = WelllogService(self.client)
            for log in wellbore.welllogs:
                for curve in log.curves:
                    log_svc.add_curve_samples(curve)
                log_svc.create_las_file_server(log)    # Create

        # Geosteering interpretations
        interp_lut: Dict[int, int] = dict()  # Need LUT for interps to re-reference from fracs that refer to them.
        if options.geosteering:
            # Note: curve ids in curve defs in interpretations refer to curves that already exist on server
            geosteer_svc = GeosteeringService(self.client)
            for interp in wellbore.interpretations:
                org_id = interp.id
                geosteer_svc.add_interpretation(wellbore.id, interp)
                interp_lut[org_id] = interp.id

        if options.fracs:
            # Do some validation.
            # If we are loading frac data, and it refers to a geosteering interpretation, must first create the interp,
            # and update the reference in the frac to the new instances. It is illegal to create a frac in this method
            # that refers to a geosteering interpretation without creating the interpretation in this method.
            refs_to_interps = any(frac.interpretation_id is not None for frac in well.primary_wellbore.fracs)
            if refs_to_interps and not options.geosteering:
                raise ZonevuError.local('cannot create frac on wellbore without providing geosteering interps')

            frac_svc = CompletionsService(self.client)
            for frac in wellbore.fracs:
                if frac.interpretation_id is not None:
                    frac.interpretation_id = interp_lut.get(frac.interpretation_id)
                frac_svc.add_frac(wellbore, frac)

        # Wellbore notes
        if options.notes:
            notes_svc = NoteService(self.client)
            notes_svc.add_notes(wellbore, wellbore.notes)

        # Wellbore Mods and Target Lines
        if options.surveymods:
            new_mods = []
            mods_svc = SurveyModsService(self.client)
            for mod in wellbore.surveymods:
                old_survey_id = mod.survey_id
                new_survey_id = survey_lut.get(old_survey_id)
                if mods_svc.update_survey_id(mod, old_survey_id, new_survey_id):
                    new_mods.append(mod)

            mods_svc.add_mods(wellbore, new_mods)

    def add_tops(self, well: Well) -> None:
        """
        Updates the well tops on the server for all wellbores on the well from the tops on each wellbore

        :param well: well object
        """
        for wellbore in well.wellbores:
            top_svc = WelltopService(self.client)
            top_svc.add_tops(wellbore, wellbore.tops)

    def update_well(self, well: Well) -> None:
        """
        Updates a well. Note that only the well-level properties are updated.

        :param well: well object
        :return: Throw a ZonevuError if method fails
        """
        url = "well/update/%s" % well.id
        item = self.client.patch(url, well.to_dict(), True)

    def delete_well(self, well_id: int, delete_code: str) -> None:
        url = "well/delete/%s" % well_id
        url_params: Dict[str, Any] = {"deletecode": delete_code}
        self.client.delete(url, url_params)

    def get_well_projects(self, well_id: int) -> list[ProjectEntry]:
        # Get a list of projects that include this well.
        url = "well/projects/%s" % well_id
        items = self.client.get_list(url)
        entries = [ProjectEntry.from_dict(w) for w in items]
        return entries

    def copy_well(self,
                  well: Well,
                  well_copy_name: str,
                  well_copy_number: Optional[str],
                  well_copy_uwi: str,
                  *,
                  project_id: Optional[int] = None,
                  show_progress: bool = False
                  ) -> Well:
        """
        This function makes and saves a copy of a well and all of its child data.

        :param well: the well to be copied
        :param well_copy_name:  name of copied well
        :param well_copy_number:  number of copied well. If None, the well number from the source well will be used.
        :param well_copy_uwi:  UWI of copied well
        :param project_id: Optional project id. If set the well copy will be associated with this project, and will be created in the company that owns the project.
        :return: the copy of the well

        Notes
        -----
        1.  We are copying a well and all of its constituent child data, including surveys, well logs, tops, etc. We will do a "Phase I" copy of all of this, except the geosteering interpretations.
        2.  We will also copy the geosteering interpretations -- this will be "Phase II". This is a special case because these refer to other wells, namely, type wells. We will assume that those wells are not being copied, therefore the references in the geosteering interpretations to those wells will remain valid.
        3.  The geosteering interpretations also refer to LWD well log curves on this well that is being copied. Those references need to be updated since we have copied in Phase I the well logs on this very well.
        """
        geosteer_svc = GeosteeringService(self.client)

        # Phase I - create and save a copy of the well and all its child data, except geosteering interpretations
        well_copy = copy.deepcopy(well)
        well_copy.name = well_copy_name
        well_copy.uwi = well_copy_uwi
        if well_copy_number is not None:
            well_copy.number = well_copy_number
        # Note: adjust well log types to mask out Witsml source.
        for wellbore in well_copy.wellbores:
            for log in wellbore.welllogs:
                if log.source == WellLogTypeEnum.Witsml:
                    log.source = WellLogTypeEnum.Digital

        # NOTE: create_well updates all the system ids on the well and all of its children to the new saved ids.
        #       We will use those new system ids below.
        if show_progress:
            print(f'Creating copy of well "{well.name} {well.number}" (id={well.id}) ...')
        self.create_well(well_copy, {WellData.surveys, WellData.logs, WellData.curves, WellData.tops,
                                     WellData.notes, WellData.surveymods}, project_id=project_id)
        if show_progress:
            print(f'   Created well copy "{well_copy.name} {well_copy.number}" (id={well_copy.id})')

        wb_orig = well.primary_wellbore
        if wb_orig is None:
            return well_copy

        # Phase II - copy the geosteering interpretations, update curve defs that refer to this wellbores logs, & save.
        # Make a lookup dict that relates the well log curves in the original well to the curves in the copied well.
        wb_copy = well_copy.primary_wellbore
        if wb_copy is None:
            print(f'* Warning could not copy wellbore "{wb_orig.name}" (id={wb_orig.id})')
            return well_copy

        log_lut = {orig.id: cpy.id for orig, cpy in zip(wb_orig.welllogs, wb_copy.welllogs)}
        curve_lut = {orig.id: cpy.id for orig, cpy in zip(wb_orig.well_log_curves, wb_copy.well_log_curves)}
        grp_lut = {orig.id: cpy.id for orig, cpy in zip(wb_orig.well_log_curve_groups, wb_copy.well_log_curve_groups)}

        # Update curve defs in geosteering interpretations that refer to this wellbores logs
        total_interps = len(wb_orig.interpretations)
        if show_progress:
            print(f'   Copying {total_interps} geosteering interpretations ...')
            # Track time of last progress print so we can emit periodic updates (requested behavior)
            last_interp_progress_print = time.time()
        else:
            last_interp_progress_print = 0.0  # unused when show_progress is False

        interp_id_lut: Dict[int, int] = {}
        for interp in wb_orig.interpretations:
            interp_copy = copy.deepcopy(interp)  # Make a copy of the interpretation
            if interp_copy.editability == Editability.Locked:
                interp_copy.editability = Editability.Owner

            for d in interp_copy.curve_defs:  # For curve defs that refer to this well, and update them to correct system ids
                if d.curve_id is not None and d.curve_id in curve_lut:
                    d.curve_id = curve_lut[d.curve_id]  # Update the curve def curve id reference
                if d.curve_group_id is not None and d.curve_group_id in grp_lut:
                    d.curve_group_id = grp_lut[d.curve_group_id]  # Update the curve def curve id reference
                if d.well_id is not None and d.well_id == well.id:
                    d.well_id = well_copy.id
                if d.well_log_id is not None and d.well_log_id in log_lut:
                    d.well_log_id = log_lut[d.well_log_id]
                if d.wellbore_id is not None and d.wellbore_id == wb_orig.id:
                    d.wellbore_id = wb_copy.id

            # if any horizon depths point to the original wellbore, update them to point to the copy
            for td in interp_copy.typewell_horizon_depths or []:
                if td.type_wellbore_id == wb_orig.id:
                    td.type_wellbore_id = wb_copy.id

            try:
                geosteer_svc.add_interpretation(wb_copy.id, interp_copy)  # Save interp onto well copy
                interp_id_lut[interp.id] = interp_copy.id

                # Periodically print how many interpretations have been copied (no more than every 10 seconds)
                if show_progress:
                    now = time.time()
                    if now - last_interp_progress_print > 10.0:
                        print(f'      Copied {len(interp_id_lut)}/{total_interps} interpretations ...')
                        last_interp_progress_print = now
            except ZonevuError as interp_err:
                print(f'* Warning could not copy interpretation "{interp_copy.name}" (id={interp_copy.id}):\n{interp_err.message}')

        # Do fracs last since a frac could refer to a geosteering interp
        if show_progress:
            print(f'   Copying {len(wb_orig.fracs)} fracs ...')
        frac_svc = CompletionsService(self.client)
        for frac in wb_orig.fracs:
            frac_copy = copy.deepcopy(frac)
            if frac.interpretation_id is not None:
                if frac.interpretation_id in interp_id_lut:
                    frac_copy.interpretation_id = interp_id_lut[frac.interpretation_id]
            frac_svc.add_frac(wb_copy.id, frac_copy)

        return well_copy




