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
#
#

"""
SurveyMods service.

List, retrieve, and add survey mods (target lines and wellbore modifications) entities.
"""
from .SurveyService import SurveyService
from .. import ZonevuError
from ..datamodels.surveymods.SurveyMod import SurveyMod
from ..datamodels.surveymods import SurveyModEntry
from ..datamodels.wells.Wellbore import Wellbore
from .Client import Client


class SurveyModsService:
    """List, retrieve, load, and add notes and categories for a wellbore."""

    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_mods(self, wellbore_id: int) -> list[SurveyModEntry]:
        url = "surveymods/%s" % wellbore_id
        items = self.client.get_list(url)
        mods = [SurveyMod.from_dict(w) for w in items]
        return mods

    def find_mod(self, mod_id: int) -> SurveyMod:
        url = "surveymod/%s" % mod_id
        item = self.client.get(url)
        mod = SurveyMod.from_dict(item)
        return mod

    def load_mods(self, wellbore: Wellbore) -> list[SurveyMod]:
        mod_entries = self.get_mods(wellbore.id)
        wellbore.surveymods = []
        for mod_entry in mod_entries:
            try:
                mod = self.find_mod(mod_entry.id)
                wellbore.surveymods.append(mod)
            except ZonevuError as mod_err:
                print('Could not load survey mod "%s" because %s' % mod_err.message)
            except Exception as err2:
                print('Could not load survey mod "%s" because %s' % err2)
        return wellbore.surveymods

    def add_mods(self, wellbore: Wellbore | int, mods: list[SurveyMod]) -> None:
        """
        Adds a survey mod to a wellbore. Updates the passed in mod with zonevu ids.
        @param wellbore: Zonevu id of wellbore to which survey will be added.
        @param mod: SurveyMod object
        @return: Throw a ZonevuError if the method fails
        """
        wellbore_id = wellbore if isinstance(wellbore, int) else wellbore.id
        url = "surveymod/add/%s" % wellbore_id
        for mod in mods:
            d = mod.to_dict()
            item = self.client.post(url, d)
            server_mod = SurveyMod.from_dict(item)
            mod.copy_ids_from(server_mod)

    def delete_mod(self, mod: SurveyMod, delete_code: str) -> None:
        url = "surveymod/delete/%s" % mod.id
        self.client.delete(url, {"deletecode": delete_code})



    def update_survey_id(self, mod: SurveyMod, old_survey_id: int, new_survey_id: int) -> bool:
        """For well copy, update the survey_id and the tie point station ID to point to the copied survey."""
        stat = False
        if new_survey_id:
            survey_svc = SurveyService(self.client)
            old_survey = survey_svc.find_survey(old_survey_id)
            new_survey = survey_svc.find_survey(new_survey_id)
            if new_survey:
                mod.survey_id = new_survey.id
                has_tie_point = False
                if old_survey and mod.anchor_survey_station_id and mod.anchor_survey_station_id > 0 and mod.start_with_tie_point:
                    num_old_stations = len(old_survey.stations)
                    num_new_stations = len(new_survey.stations)
                    if num_old_stations == num_new_stations:
                        for i in range(num_old_stations):
                            if old_survey.stations[i].id == mod.anchor_survey_station_id:
                                mod.anchor_survey_station_id = new_survey.stations[i].id
                                has_tie_point = True
                                stat = True
                                break

                if not has_tie_point:
                    mod.start_with_tie_point = False
                    mod.anchor_survey_station_id = -1
                    stat = True

        return stat


