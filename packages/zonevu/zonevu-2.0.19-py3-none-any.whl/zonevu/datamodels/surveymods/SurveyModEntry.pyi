from ..DataModel import DataModel as DataModel
from dataclasses import dataclass
from strenum import StrEnum

class SurveyModTypeEnum(StrEnum):
    WellboreModification = 'WellboreModification'
    TargetLine = 'TargetLine'
    DrilledToPlan = 'DrilledToPlan'
    FloatingWaypoints = 'FloatingWaypoints'
    WaypointAndGuideline = 'WaypointAndGuideline'
    TargetLineUTurnReturn = 'TargetLineUTurnReturn'

@dataclass
class SurveyModEntry(DataModel):
    description: str | None = ...
    type: SurveyModTypeEnum = ...
